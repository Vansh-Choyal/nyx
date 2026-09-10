import subprocess
from core import config

def run_command(cmd):
    print(f"Running command: {cmd}")
    
    result = subprocess.run(
        ["wsl", "bash", "-c", cmd],
        cwd=config["current_directory"],  # Python handles the Windows path execution here
        capture_output=True,
        text=True
    )

    # Added escaping for quotes/newlines in stdout/stderr to prevent string breakages
    import json
    return json.dumps({
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }, indent=4)