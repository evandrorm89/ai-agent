import os
from pathlib import Path
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)


def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))

        valid_target_dir = (
            os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        )
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        path = Path(target_dir)
        if not path.is_dir():
            return f'Error: "{directory}" is not a directory'

        files_info: list[str] = []
        for content in os.listdir(target_dir):
            joined_path = os.path.join(target_dir, content)
            files_info.append(
                f"- {content}: file_size={os.path.getsize(joined_path)} bytes, is_dir={os.path.isdir(joined_path)}"
            )
        return "\n".join(files_info)
    except Exception:
        return "Error: An unexpected error occurred while validating the directory"
