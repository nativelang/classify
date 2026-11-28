import { copyFileSync, readFileSync, writeFileSync } from "node:fs";

copyFileSync("../../app/bootstrap.sh", "./bootstrap.sh");
copyFileSync("../../app/install.ps1", "./install.ps1");
copyFileSync("../../LICENSE", "./LICENSE");
const example = readFileSync("../../examples/node/README.md", "utf8");
writeFileSync("./README.md", example.replaceAll("../../docs/", "https://github.com/nativelang/classify/blob/main/docs/"));
