import os
import utils

container_names = utils.ps(r"{{.Names}}")

if len(container_names) == 0:
    print("No container was found")
    exit()

container_name = container_names[0]
print(
    f"Running inside of {container_name} of {len(container_names)} containers")

os.system(f"docker exec -it {container_name} sh")
