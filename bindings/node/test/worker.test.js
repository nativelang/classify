import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { copyFileSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";

test("queued calls share a worker, recover from failure, and allow the app to exit", (t) => {
  const dir = mkdtempSync(join(tmpdir(), "classify-node-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  copyFileSync(new URL("../index.js", import.meta.url), join(dir, "index.mjs"));
  writeFileSync(join(dir, "bootstrap.sh"), `echo "$$" >> starts
while IFS= read -r request; do
  case "$request" in
    *broken*) exit 1 ;;
    *invalid*) echo '{"error":{"code":"invalid_argument","message":"Invalid categories"}}' ;;
    *unrelated*) echo '{"status":"unknown","category":null}' ;;
    *) echo '{"status":"matched","category":"negative"}' ;;
  esac
done
`);
  const probe = `
    import assert from 'node:assert/strict';
    import { classify } from './index.mjs';
    const call = text => classify(text, ['negative']);
    const group = [call('review'), call('invalid'), call('unrelated')];
    const [match, invalid, unknown] = await Promise.allSettled(group);
    assert.deepEqual(match, { status: 'fulfilled', value: 'negative' });
    assert.equal(invalid.reason.code, 'invalid_argument');
    assert.deepEqual(unknown, { status: 'fulfilled', value: null });
    await new Promise(resolve => setTimeout(resolve, 20));
    assert.equal(await call('review'), 'negative');
    await assert.rejects(call('broken'));
    assert.equal(await call('review'), 'negative');
  `;
  const run = spawnSync(process.execPath, ["--input-type=module", "--eval", probe], {
    cwd: dir, timeout: 5000, encoding: "utf8",
  });
  assert.ifError(run.error);
  assert.equal(run.status, 0, run.stderr);
  assert.equal(readFileSync(join(dir, "starts"), "utf8").trim().split("\n").length, 2);
});

test("an explicit app exit stops the active classifier", async (t) => {
  const dir = mkdtempSync(join(tmpdir(), "classify-exit-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  copyFileSync(new URL("../index.js", import.meta.url), join(dir, "index.mjs"));
  writeFileSync(join(dir, "bootstrap.sh"), 'echo "$$" > pid\nexec sleep 10\n');
  const probe = `
    import { existsSync } from 'node:fs';
    import { classify } from './index.mjs';
    classify('review', ['negative']);
    setInterval(() => { if (existsSync('pid')) process.exit(0); }, 10);
  `;
  const run = spawnSync(process.execPath, ["--input-type=module", "--eval", probe], {
    // The worker inherits stderr. A pipe here would wait for its EOF too.
    cwd: dir, timeout: 2000, stdio: "ignore",
  });
  assert.ifError(run.error);
  assert.equal(run.status, 0);
  const pid = Number(readFileSync(join(dir, "pid"), "utf8"));
  for (let attempt = 0; attempt < 50; attempt++) {
    try {
      process.kill(pid, 0);
    } catch (error) {
      assert.equal(error.code, "ESRCH");
      return;
    }
    await new Promise(resolve => setTimeout(resolve, 20));
  }
  assert.fail("The classifier survived explicit app exit.");
});
