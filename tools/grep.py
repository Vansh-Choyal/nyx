import shlex

from core.core import config, _resolve_path
from tools.terminal import run_command


def grep(pattern, path, recursive=False):
    print(f"Running `grep` on {path} with the pattern {grep}")
    try:
        path = _resolve_path(path)

        cmd = ["grep", "-n"]

        if recursive:
            cmd.append("-r")

        cmd.extend([
            shlex.quote(pattern),
            shlex.quote(path)
        ])

        return run_command(" ".join(cmd))

    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"