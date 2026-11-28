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

impl Session {
    fn start() -> io::Result<Self> {
        let mut child = Command::new("/bin/sh")
            .args(["-c", include_str!("../bootstrap.sh")])
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
