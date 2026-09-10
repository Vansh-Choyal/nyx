import os

from core import config, _resolve_path  

def write_file(file_path, content):
    print(f"Writing at {file_path} with content length {len(content)}")
    try:
        file_path = _resolve_path(file_path)

        if os.path.exists(file_path):
            return (
                f"Error: {file_path} already exists. "
                "Use patch_file instead of write_file to modify "
                "an existing file."
            )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully created and wrote to {file_path}."

    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"