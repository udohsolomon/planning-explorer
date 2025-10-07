"""
Supabase Tools

Tools for interacting with Supabase database and authentication.
Enables agents to perform CRUD operations and auth management.
"""

from typing import Any, List, Dict, Optional
from supabase import create_client, Client

from .base_tool import BaseTool, ToolParameter
from app.core.config import settings


class SupabaseCRUDTool(BaseTool):
    """Perform CRUD operations on Supabase tables"""

    def __init__(self):
        super().__init__()
        self.client: Optional[Client] = None

    def get_name(self) -> str:
        return "supabase_crud"

    def get_description(self) -> str:
        return """Perform CRUD operations on Supabase tables.

Supports:
- SELECT: Query data with filters
- INSERT: Create new records
- UPDATE: Modify existing records
- DELETE: Remove records
- UPSERT: Insert or update based on conflict"""

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="CRUD operation to perform",
                required=True,
                enum=["select", "insert", "update", "delete", "upsert"]
            ),
            ToolParameter(
                name="table",
                type="string",
                description="Table name",
                required=True
            ),
            ToolParameter(
                name="data",
                type="object",
                description="Data for insert/update/upsert operations (JSON object)",
                required=False
            ),
            ToolParameter(
                name="filters",
                type="object",
                description="Filters for select/update/delete (e.g., {'id': '123'})",
                required=False
            ),
            ToolParameter(
                name="columns",
                type="string",
                description="Columns to select (comma-separated, default: '*')",
                required=False,
                default="*"
            ),
            ToolParameter(
                name="order_by",
                type="string",
                description="Column to order by",
                required=False
            ),
            ToolParameter(
                name="limit",
                type="number",
                description="Limit number of results",
                required=False
            )
        ]

    async def execute(
        self,
        operation: str,
        table: str,
        data: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None,
        columns: str = "*",
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Any:
        """
        Execute CRUD operation.

        Args:
            operation: select, insert, update, delete, upsert
            table: Table name
            data: Data for write operations
            filters: Filters for queries
            columns: Columns to select
            order_by: Sort column
            limit: Result limit

        Returns:
            Operation result
        """
        self.validate_parameters(operation=operation, table=table)

        try:
            # Initialize Supabase client if needed
            if not self.client:
                self.client = create_client(
                    settings.supabase_url,
                    settings.supabase_key
                )

            # Execute operation
            if operation == "select":
                return await self._select(table, columns, filters, order_by, limit)
            elif operation == "insert":
                return await self._insert(table, data)
            elif operation == "update":
                return await self._update(table, data, filters)
            elif operation == "delete":
                return await self._delete(table, filters)
            elif operation == "upsert":
                return await self._upsert(table, data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Supabase {operation} failed: {str(e)}",
                "table": table
            }

    async def _select(
        self,
        table: str,
        columns: str,
        filters: Optional[Dict[str, Any]],
        order_by: Optional[str],
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Execute SELECT query"""
        query = self.client.table(table).select(columns)

        # Apply filters
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        # Apply ordering
        if order_by:
            query = query.order(order_by)

        # Apply limit
        if limit:
            query = query.limit(limit)

        # Execute
        response = query.execute()

        return {
            "success": True,
            "operation": "select",
            "table": table,
            "count": len(response.data),
            "data": response.data
        }

    async def _insert(
        self,
        table: str,
        data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute INSERT"""
        if not data:
            return {"success": False, "error": "Data required for insert"}

        response = self.client.table(table).insert(data).execute()

        return {
            "success": True,
            "operation": "insert",
            "table": table,
            "inserted": len(response.data),
            "data": response.data
        }

    async def _update(
        self,
        table: str,
        data: Optional[Dict[str, Any]],
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute UPDATE"""
        if not data:
            return {"success": False, "error": "Data required for update"}

        query = self.client.table(table).update(data)

        # Apply filters
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        response = query.execute()

        return {
            "success": True,
            "operation": "update",
            "table": table,
            "updated": len(response.data),
            "data": response.data
        }

    async def _delete(
        self,
        table: str,
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute DELETE"""
        query = self.client.table(table).delete()

        # Apply filters
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        else:
            return {
                "success": False,
                "error": "Filters required for delete (safety check)"
            }

        response = query.execute()

        return {
            "success": True,
            "operation": "delete",
            "table": table,
            "deleted": len(response.data)
        }

    async def _upsert(
        self,
        table: str,
        data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute UPSERT"""
        if not data:
            return {"success": False, "error": "Data required for upsert"}

        response = self.client.table(table).upsert(data).execute()

        return {
            "success": True,
            "operation": "upsert",
            "table": table,
            "upserted": len(response.data),
            "data": response.data
        }


class SupabaseAuthTool(BaseTool):
    """Manage Supabase authentication"""

    def __init__(self):
        super().__init__()
        self.client: Optional[Client] = None

    def get_name(self) -> str:
        return "supabase_auth"

    def get_description(self) -> str:
        return """Manage Supabase authentication operations.

Supports:
- Verify JWT token
- Get user by ID
- List users (admin)
- Update user metadata"""

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Auth operation to perform",
                required=True,
                enum=["verify_token", "get_user", "list_users", "update_user"]
            ),
            ToolParameter(
                name="token",
                type="string",
                description="JWT token (for verify_token)",
                required=False
            ),
            ToolParameter(
                name="user_id",
                type="string",
                description="User ID (for get_user, update_user)",
                required=False
            ),
            ToolParameter(
                name="metadata",
                type="object",
                description="User metadata to update",
                required=False
            )
        ]

    async def execute(
        self,
        operation: str,
        token: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute auth operation"""
        self.validate_parameters(operation=operation)

        try:
            if not self.client:
                self.client = create_client(
                    settings.supabase_url,
                    settings.supabase_key
                )

            if operation == "verify_token":
                if not token:
                    return {"success": False, "error": "Token required"}

                user = self.client.auth.get_user(token)
                return {
                    "success": True,
                    "operation": "verify_token",
                    "valid": user is not None,
                    "user": user.dict() if user else None
                }

            elif operation == "get_user":
                if not user_id:
                    return {"success": False, "error": "User ID required"}

                # Get user from admin API
                user = self.client.auth.admin.get_user_by_id(user_id)
                return {
                    "success": True,
                    "operation": "get_user",
                    "user": user.dict() if user else None
                }

            elif operation == "list_users":
                users = self.client.auth.admin.list_users()
                return {
                    "success": True,
                    "operation": "list_users",
                    "count": len(users),
                    "users": [u.dict() for u in users]
                }

            elif operation == "update_user":
                if not user_id or not metadata:
                    return {"success": False, "error": "User ID and metadata required"}

                user = self.client.auth.admin.update_user_by_id(
                    user_id,
                    {"user_metadata": metadata}
                )
                return {
                    "success": True,
                    "operation": "update_user",
                    "user": user.dict() if user else None
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Auth operation failed: {str(e)}",
                "operation": operation
            }


class SupabaseStorageTool(BaseTool):
    """Manage Supabase storage operations"""

    def __init__(self):
        super().__init__()
        self.client: Optional[Client] = None

    def get_name(self) -> str:
        return "supabase_storage"

    def get_description(self) -> str:
        return "Manage files in Supabase storage buckets"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Storage operation",
                required=True,
                enum=["upload", "download", "list", "delete"]
            ),
            ToolParameter(
                name="bucket",
                type="string",
                description="Storage bucket name",
                required=True
            ),
            ToolParameter(
                name="path",
                type="string",
                description="File path in bucket",
                required=False
            ),
            ToolParameter(
                name="file_data",
                type="string",
                description="File content (for upload)",
                required=False
            )
        ]

    async def execute(
        self,
        operation: str,
        bucket: str,
        path: Optional[str] = None,
        file_data: Optional[str] = None
    ) -> Any:
        """Execute storage operation"""
        self.validate_parameters(operation=operation, bucket=bucket)

        try:
            if not self.client:
                self.client = create_client(
                    settings.supabase_url,
                    settings.supabase_key
                )

            storage = self.client.storage.from_(bucket)

            if operation == "upload":
                if not path or not file_data:
                    return {"success": False, "error": "Path and file_data required"}

                response = storage.upload(path, file_data)
                return {
                    "success": True,
                    "operation": "upload",
                    "bucket": bucket,
                    "path": path
                }

            elif operation == "download":
                if not path:
                    return {"success": False, "error": "Path required"}

                data = storage.download(path)
                return {
                    "success": True,
                    "operation": "download",
                    "bucket": bucket,
                    "path": path,
                    "data": data
                }

            elif operation == "list":
                files = storage.list(path or "")
                return {
                    "success": True,
                    "operation": "list",
                    "bucket": bucket,
                    "count": len(files),
                    "files": files
                }

            elif operation == "delete":
                if not path:
                    return {"success": False, "error": "Path required"}

                storage.remove([path])
                return {
                    "success": True,
                    "operation": "delete",
                    "bucket": bucket,
                    "path": path
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Storage operation failed: {str(e)}",
                "operation": operation,
                "bucket": bucket
            }
