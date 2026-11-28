import { copyFileSync } from "node:fs";

copyFileSync("../../app/bootstrap.sh", "./bootstrap.sh");
copyFileSync("../../app/install.ps1", "./install.ps1");
copyFileSync("../../LICENSE", "./LICENSE");
copyFileSync("../../examples/node/README.md", "./README.md");
