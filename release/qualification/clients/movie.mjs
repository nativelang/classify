import { createInterface } from "node:readline";
import { classify } from "@nativelang/classify";

console.log(process.arch);
for await (const line of createInterface({ input: process.stdin, crlfDelay: Infinity })) {
    const [text, ...categories] = line.split("\t");
    console.log(await classify(text, categories) ?? "");
}
