"""
Agent Tools Module

Custom tools that agents can use to interact with the Planning Explorer system:

- File operations (read, write, edit, list)
- Elasticsearch queries and indexing
- Supabase database operations
- AI processing (embeddings, summarization, scoring)
- Testing and validation tools
"""

from .base_tool import BaseTool
from .file_tools import FileReadTool, FileWriteTool, FileEditTool, FileListTool
from .elasticsearch_tools import (
    ElasticsearchQueryTool,
    ElasticsearchIndexTool,
    ElasticsearchBulkTool,
    ElasticsearchDeleteTool
)
from .supabase_tools import (
    SupabaseCRUDTool,
    SupabaseAuthTool,
    SupabaseStorageTool
)
from .ai_tools import (
    EmbeddingTool,
    SummarizationTool,
    OpportunityScoringTool,
    SemanticSearchTool
)

__all__ = [
    "BaseTool",
    "FileReadTool",
    "FileWriteTool",
    "FileEditTool",
    "FileListTool",
    "ElasticsearchQueryTool",
    "ElasticsearchIndexTool",
    "ElasticsearchBulkTool",
    "ElasticsearchDeleteTool",
    "SupabaseCRUDTool",
    "SupabaseAuthTool",
    "SupabaseStorageTool",
    "EmbeddingTool",
    "SummarizationTool",
    "OpportunityScoringTool",
    "SemanticSearchTool",
]
