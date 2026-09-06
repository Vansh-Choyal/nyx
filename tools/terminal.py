import subprocess

def run_command(cmd):
    result = subprocess.run(
        ["wsl", "bash", "-c", cmd],
        capture_output=True,
        text=True
    )
    print(f"Running command: {cmd}")

    return f'''
        "return_code": {result.returncode},
        "stdout": {result.stdout},
        "stderr": {result.stderr}
    '''