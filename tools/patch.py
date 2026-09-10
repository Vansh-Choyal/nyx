from core import config, _resolve_path


def patch_file(file_path, old_text, new_text):
    print(f"Patching {file_path}")
    try:
        file_path = _resolve_path(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        count = content.count(old_text)

        if count == 0:
            return "Error: old_text was not found in the file."

        if count > 1:
            return (
                f"Error: old_text was found {count} times. "
                "It must match exactly once."
            )

        content = content.replace(old_text, new_text, 1)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully patched {file_path}."

    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"