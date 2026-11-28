import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { fileURLToPath } from "node:url";

const bootstrap = fileURLToPath(new URL("./bootstrap.sh", import.meta.url));
let worker;
let queue = Promise.resolve();
process.once("exit", () => worker?.child.kill());

function startWorker() {
  const child = spawn("/bin/sh", [bootstrap], { stdio: ["pipe", "pipe", "inherit"] });
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
  const current = worker ??= startWorker();
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
