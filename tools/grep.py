import shlex
from tools.terminal import run_command


def grep(pattern, path, recursive=False):
    print(f"Running grep at {path} with the pattern: {pattern}")
    
    cmd = ["grep", "-n"]

    if recursive:
        cmd.append("-r")

    cmd.extend([
        shlex.quote(pattern),
        shlex.quote(path)
    ])

    return run_command(" ".join(cmd))