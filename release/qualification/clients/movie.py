import platform
import sys

from nativelang_classify import classify

print(platform.machine(), flush=True)
for line in sys.stdin:
    text, *categories = line.rstrip("\n").split("\t")
    print(classify(text, categories) or "", flush=True)
