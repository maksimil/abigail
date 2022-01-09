#!/usr/bin/env python3

import os
import subprocess
import shutil
import json

shutil.rmtree("./db")
os.mkdir("./db")

process = subprocess.Popen(
    ["mongod", "--dbpath", "./db"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
)

while process.poll() is None:
    stdout = process.stdout.readline()
    output = json.loads(stdout)

    if output["msg"] == "Waiting for connections":
        subprocess.run(["sh", "./scripts/mongo-init.sh"])

    if output["msg"] == "Connection ended":
        break

process.kill()
