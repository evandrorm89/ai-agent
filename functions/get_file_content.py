import os
from config import MAX_CHARS
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Gets the content of a specified file relative to the working directory, returning an error if the file is not found or is not a regular file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="file path to read, relative to the working directory (default is the working directory itself)",
            ),
        },
        required=["file_path"],
    ),
)


def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        file_path = os.path.normpath(os.path.join(working_dir_abs, file_path))

        valid_target_dir = (
            os.path.commonpath([working_dir_abs, file_path]) == working_dir_abs
        )
        if not valid_target_dir:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(file_path, "r") as f:
            content = f.read(
                MAX_CHARS
            )  # Read the first 1000 characters to avoid loading large files into memory

            if f.read(
                1
            ):  # Check if there is more content after the first 1000 characters
                content += (
                    f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
                )

            return content
    except Exception as e:
        return f"Error reading files: {e}"
