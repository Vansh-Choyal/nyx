from core import config, _resolve_path


def read_file(file_path, start_line=1, end_line=0):
    print(f"Reading {file_path} from {start_line} to {end_line}")
    try:
        file_path = _resolve_path(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if start_line < 1:
            return "Error: start_line must be >= 1"

        if end_line != 0 and end_line < start_line:
            return "Error: end_line must be >= start_line"

        if start_line > len(lines):
            return (
                f"Error: start_line {start_line} is beyond "
                f"the end of the file ({len(lines)} lines)"
            )

        if end_line == 0:
            end_line = len(lines)

        return "".join(
            f"{i}: {lines[i - 1]}"
            for i in range(start_line, min(end_line, len(lines)) + 1)
        )

    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"