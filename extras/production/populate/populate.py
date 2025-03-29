#!/usr/bin/env python3
import os
import subprocess
import sys

# base directory where the script is located
base_dir = os.path.dirname(os.path.abspath(__file__))

# list of script paths to execute, relative to the current directory
scripts = [
    os.path.join(base_dir, "populate-users.py"),
    os.path.join(base_dir, "populate-customers.py"),
    os.path.join(base_dir, "populate-plans.py"),
]

# check if the script is running locally
is_local = "--local" in sys.argv

# determine the project path
if is_local:
    home_dir = os.environ.get("HOME", "")

    if not home_dir:
        print("HOME environment variable is not set.\n")
        exit(1)

    project_path = os.path.join(
        home_dir,
        "Developer",
        "workspaces",
        "python",
        "pyaa",
    )
else:
    project_path = "/app/pyaa"

# ensure the project path exists
if not os.path.exists(project_path):
    print(f"django project path not found: {project_path}\n")
    exit(1)

# iterate over the list of scripts and execute each one
for script_path in scripts:
    # ensure the script exists
    if not os.path.exists(script_path):
        print(f"script not found: {script_path}\n")
        continue

    # read the script content
    with open(script_path, "r") as script_file:
        script_content = script_file.read()

    # determine the command to execute based on the environment
    if is_local:
        command = ["python3", os.path.join(project_path, "manage.py"), "shell"]
    else:
        command = [
            "docker",
            "exec",
            "-i",
            "app-pyaa-1",
            "python3",
            "manage.py",
            "shell",
        ]

    process = subprocess.Popen(
        command,
        cwd=project_path,
        stdin=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = process.communicate(input=script_content)

    if process.returncode != 0:
        print(f"Error executing script {script_path}:\n{stderr}\n")
    else:
        print(f"Successfully executed script: {script_path}")
