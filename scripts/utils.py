import os


def ps(fmt):
    return os.popen(
        f"docker ps -f ancestor=abigail --format \"{fmt}\"").read().splitlines()
