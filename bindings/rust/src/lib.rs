//! Classify text locally using the Classify runtime.

use serde_json::{json, Value};
use std::io::{self, BufRead, BufReader, Write};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::sync::Mutex;

static SESSION: Mutex<Option<Session>> = Mutex::new(None);

struct Session {
    child: Child,
    input: ChildStdin,
    output: BufReader<ChildStdout>,
}

#[cfg(not(windows))]
fn worker_command() -> io::Result<Command> {
    let mut command = Command::new("/bin/sh");
    command.args(["-c", include_str!("../bootstrap.sh")]);
    Ok(command)
}

#[cfg(windows)]
fn worker_command() -> io::Result<Command> {
    use std::path::PathBuf;
    let root =
        std::env::var_os("SystemRoot").ok_or_else(|| io::Error::other("missing SystemRoot"))?;
    let shell = PathBuf::from(root).join(r"System32\WindowsPowerShell\v1.0\powershell.exe");
    let mut bootstrap = Command::new(shell)
        .args([
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            "& ([ScriptBlock]::Create([Console]::In.ReadToEnd()))",
        ])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .spawn()?;
    bootstrap
        .stdin
        .take()
        .expect("piped stdin")
        .write_all(include_bytes!("../install.ps1"))?;
    let install = bootstrap.wait_with_output()?;
    if !install.status.success() {
        return Err(io::Error::other("Classify installation failed"));
    }
    let path = String::from_utf8(install.stdout).map_err(io::Error::other)?;
    let exe = PathBuf::from(path.trim());
    let profile = exe.with_file_name("model").join("profile.json");
    let mut command = Command::new(exe);
    command.arg("infer").arg("--profile").arg(profile);
    Ok(command)
}

impl Session {
    fn start() -> io::Result<Self> {
        let mut command = worker_command()?;
        let mut child = command
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .spawn()?;
        Ok(Self {
            input: child.stdin.take().expect("piped stdin"),
            output: BufReader::new(child.stdout.take().expect("piped stdout")),
            child,
        })
    }

    fn request(&mut self, text: &str, categories: &[&str]) -> io::Result<Value> {
        writeln!(
            self.input,
            "{}",
            json!({"text": text, "categories": categories})
        )?;
        self.input.flush()?;
        let mut line = String::new();
        self.output.read_line(&mut line)?;
        Ok(serde_json::from_str(&line)?)
    }
}

impl Drop for Session {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

/// Returns the matching category, or `None` when the model abstains.
/// Calls reuse one local runtime process.
pub fn classify(text: &str, categories: &[&str]) -> io::Result<Option<String>> {
    let mut guard = SESSION
        .lock()
        .map_err(|_| io::Error::other("Classify session lock failed"))?;
    if guard.is_none() {
        *guard = Some(Session::start()?);
    }
    let reply = match guard.as_mut().unwrap().request(text, categories) {
        Ok(value) => value,
        Err(err) => {
            *guard = None;
            return Err(err);
        }
    };
    if let Some(message) = reply["error"]["message"].as_str() {
        return Err(io::Error::other(message.to_owned()));
    }
    match (reply["status"].as_str(), reply.get("category")) {
        (Some("matched"), Some(Value::String(label))) => Ok(Some(label.clone())),
        (Some("unknown"), Some(Value::Null)) => Ok(None),
        _ => {
            *guard = None;
            Err(io::Error::new(
                io::ErrorKind::InvalidData,
                "unexpected Classify response",
            ))
        }
    }
}
