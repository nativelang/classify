import { execFile, spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { dirname, join } from "node:path";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

const bootstrap = fileURLToPath(new URL("./bootstrap.sh", import.meta.url));
let worker;
let queue = Promise.resolve();
process.once("exit", () => worker?.child.kill());

async function startWorker() {
  let command = "/bin/sh";
  let args = [bootstrap];
  if (process.platform === "win32") {
    const script = fileURLToPath(new URL("./install.ps1", import.meta.url));
    const powershell = join(process.env.SystemRoot, "System32", "WindowsPowerShell", "v1.0", "powershell.exe");
    const install = promisify(execFile)(powershell,
      ["-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", script], { windowsHide: true });
    install.child.stderr.pipe(process.stderr, { end: false });
    command = (await install).stdout.trimEnd();
    args = ["infer", "--profile", join(dirname(command), "model", "profile.json")];
  }
  const child = spawn(command, args, { stdio: ["pipe", "pipe", "inherit"], windowsHide: true });
  const output = createInterface({ input: child.stdout, crlfDelay: Infinity });
  const current = { child, lines: output[Symbol.asyncIterator](), error: null };

  const rememberError = (error) => {
    current.error = error;
  };
  child.once("error", rememberError);
  child.stdin.on("error", rememberError);
  child.once("close", () => {
    if (worker === current) worker = undefined;
  });
  return current;
}

async function infer(request) {
  const current = worker ??= await startWorker();
  const { child } = current;
  // Keep Node alive for this response. An idle worker should follow the app's lifetime.
  child.ref();
  child.stdin.ref();
  child.stdout.ref();

  let response;
  try {
    await new Promise((resolve, reject) => {
      child.stdin.write(request + "\n", (error) => error ? reject(error) : resolve());
    });
    const { value, done } = await current.lines.next();
    if (done) throw current.error ?? new Error("The local Classify process stopped before responding.");
    response = JSON.parse(value);
    if (!response?.error && !(response?.status === "unknown" && response.category === null) &&
        !(response?.status === "matched" && typeof response.category === "string")) {
      throw new Error("Unexpected response from the local Classify process.");
    }
  } catch (error) {
    if (worker === current) worker = undefined;
    child.kill();
    throw error;
  } finally {
    child.stdin.unref();
    child.stdout.unref();
    child.unref();
  }
  if (response.error) {
    const error = new Error(response.error.message);
    error.code = response.error.code;
    throw error;
  }
  return response.category;
}

export async function classify(text, categories) {
  const request = JSON.stringify({ text, categories });
  // The worker replies in order, with one JSON line per request.
  const result = queue.then(() => infer(request));
  queue = result.catch(() => {});
  return result;
}
