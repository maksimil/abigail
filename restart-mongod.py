import os
import subprocess
import shutil
import json

shutil.rmtree("./db")
os.mkdir("./db")

process = subprocess.Popen(
    ["mongod", "--dbpath", "./db"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

while process.poll() == None:
    stdout = process.stdout.readline()
    output = json.loads(stdout)

    if output["msg"] == "Waiting for connections":
        subprocess.run(
            ["sh", "-c", "source ./env.sh;mongosh admin ./mongo-init.js --quiet;"])

    if output["msg"] == "Connection ended":
        break

process.kill()
