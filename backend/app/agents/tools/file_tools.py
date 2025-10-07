"""
File Operation Tools

Tools for reading, writing, and editing files.
"""

import aiofiles
import os
from typing import Any, List
from pathlib import Path

from .base_tool import BaseTool, ToolParameter


class FileReadTool(BaseTool):
    """Read contents of a file"""

    def get_name(self) -> str:
        return "read_file"

    def get_description(self) -> str:
        return "Read the contents of a file from the filesystem"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type="string",
                description="Absolute or relative path to the file to read",
                required=True
            ),
            ToolParameter(
                name="encoding",
                type="string",
                description="File encoding (default: utf-8)",
                required=False,
                default="utf-8"
            )
        ]

    async def execute(self, file_path: str, encoding: str = "utf-8") -> Any:
        """Read file contents"""
        self.validate_parameters(file_path=file_path)

        try:
            async with aiofiles.open(file_path, mode='r', encoding=encoding) as f:
                content = await f.read()

            return {
                "success": True,
                "file_path": file_path,
                "content": content,
                "size_bytes": len(content.encode(encoding))
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}"
            }


class FileWriteTool(BaseTool):
    """Write content to a file"""

    def get_name(self) -> str:
        return "write_file"

    def get_description(self) -> str:
        return "Write content to a file, creating it if it doesn't exist"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type="string",
                description="Path where the file should be written",
                required=True
            ),
            ToolParameter(
                name="content",
                type="string",
                description="Content to write to the file",
                required=True
            ),
            ToolParameter(
                name="encoding",
                type="string",
                description="File encoding (default: utf-8)",
                required=False,
                default="utf-8"
            ),
            ToolParameter(
                name="create_dirs",
                type="boolean",
                description="Create parent directories if they don't exist",
                required=False,
                default=True
            )
        ]

    async def execute(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> Any:
        """Write content to file"""
        self.validate_parameters(file_path=file_path, content=content)

        try:
            # Create parent directories if needed
            if create_dirs:
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(file_path, mode='w', encoding=encoding) as f:
                await f.write(content)

            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": len(content.encode(encoding))
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error writing file: {str(e)}"
            }


class FileEditTool(BaseTool):
    """Edit a file by replacing a section"""

    def get_name(self) -> str:
        return "edit_file"

    def get_description(self) -> str:
        return "Edit a file by replacing old content with new content"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type="string",
                description="Path to the file to edit",
                required=True
            ),
            ToolParameter(
                name="old_content",
                type="string",
                description="Content to replace (must exist in file)",
                required=True
            ),
            ToolParameter(
                name="new_content",
                type="string",
                description="New content to insert",
                required=True
            ),
            ToolParameter(
                name="encoding",
                type="string",
                description="File encoding (default: utf-8)",
                required=False,
                default="utf-8"
            )
        ]

    async def execute(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        encoding: str = "utf-8"
    ) -> Any:
        """Edit file by replacing content"""
        self.validate_parameters(
            file_path=file_path,
            old_content=old_content,
            new_content=new_content
        )

        try:
            # Read current content
            async with aiofiles.open(file_path, mode='r', encoding=encoding) as f:
                content = await f.read()

            # Check if old_content exists
            if old_content not in content:
                return {
                    "success": False,
                    "error": f"Old content not found in file: {file_path}"
                }

            # Replace content
            new_file_content = content.replace(old_content, new_content, 1)

            # Write back
            async with aiofiles.open(file_path, mode='w', encoding=encoding) as f:
                await f.write(new_file_content)

            return {
                "success": True,
                "file_path": file_path,
                "replacements": 1
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error editing file: {str(e)}"
            }


class FileListTool(BaseTool):
    """List files in a directory"""

    def get_name(self) -> str:
        return "list_files"

    def get_description(self) -> str:
        return "List files and directories in a given path"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="directory",
                type="string",
                description="Directory path to list",
                required=True
            ),
            ToolParameter(
                name="pattern",
                type="string",
                description="Glob pattern to filter files (e.g., '*.py')",
                required=False
            ),
            ToolParameter(
                name="recursive",
                type="boolean",
                description="Search recursively in subdirectories",
                required=False,
                default=False
            )
        ]

    async def execute(
        self,
        directory: str,
        pattern: str = "*",
        recursive: bool = False
    ) -> Any:
        """List files in directory"""
        self.validate_parameters(directory=directory)

        try:
            path = Path(directory)

            if not path.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {directory}"
                }

            if not path.is_dir():
                return {
                    "success": False,
                    "error": f"Not a directory: {directory}"
                }

            # List files
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))

            # Format results
            file_list = []
            for f in files:
                file_list.append({
                    "path": str(f),
                    "name": f.name,
                    "is_file": f.is_file(),
                    "is_dir": f.is_dir(),
                    "size": f.stat().st_size if f.is_file() else None
                })

            return {
                "success": True,
                "directory": directory,
                "count": len(file_list),
                "files": file_list
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing files: {str(e)}"
            }
