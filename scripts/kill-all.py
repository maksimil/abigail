import os
import utils

for cid in utils.ps("{{.ID}}"):
    ccid = os.popen(f"docker kill {cid}").read().split()[0]
    print(f"killed {ccid}")

print("done")
