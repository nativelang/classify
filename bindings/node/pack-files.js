import { copyFileSync } from "node:fs";

copyFileSync("../../app/bootstrap.sh", "./bootstrap.sh");
copyFileSync("../../LICENSE", "./LICENSE");
copyFileSync("../../examples/node/README.md", "./README.md");
