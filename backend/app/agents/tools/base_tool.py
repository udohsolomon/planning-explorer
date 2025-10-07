"""
BaseTool - Base class for agent tools

Provides standardized interface for tools that agents can use.
Tools are converted to Anthropic's tool format for Claude.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Tool parameter definition"""
    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = True
    enum: Optional[List[str]] = None
    default: Optional[Any] = None


class BaseTool(ABC):
    """
    Base class for all agent tools.

    Tools must implement:
    - name: Tool identifier
    - description: What the tool does
    - parameters: List of parameters
    - execute: Tool execution logic
    """

    def __init__(self):
        self.name = self.get_name()
        self.description = self.get_description()
        self.parameters = self.get_parameters()

    @abstractmethod
    def get_name(self) -> str:
        """Return tool name"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Return tool description"""
        pass

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        """Return list of tool parameters"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool parameters

        Returns:
            Tool execution result
        """
        pass

    def to_anthropic_tool(self) -> Dict[str, Any]:
        """
        Convert tool to Anthropic's tool format.

        Returns:
            Tool definition in Anthropic format
        """
        # Build properties for parameters
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }

            if param.enum:
                properties[param.name]["enum"] = param.enum

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate that provided parameters match requirements.

        Args:
            **kwargs: Parameters to validate

        Returns:
            True if valid, raises ValueError if invalid
        """
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(
                    f"Required parameter '{param.name}' missing for tool '{self.name}'"
                )

        return True
