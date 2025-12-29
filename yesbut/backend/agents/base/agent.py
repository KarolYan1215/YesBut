"""
Base Agent Class

Abstract base class for all agents in the YesBut system.
Provides common functionality for LLM interaction, streaming, and tool use.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator, List, Optional, Callable
from datetime import datetime
import logging
import json
import uuid
import asyncio

from anthropic import AsyncAnthropic


class BaseAgent(ABC):
    """
    Abstract base class for all YesBut agents.

    All 8 agent types inherit from this base class:
    - RPA (Requirement Parsing Agent)
    - GEN (Generator Agent)
    - ISA (Information Scout Agent)
    - ACA (Audit & Compliance Agent)
    - BM (Branch Manager Agent)
    - GA (Game Arbiter Agent)
    - UOA (Utility Optimization Agent)
    - REC (Reverse Engineering Compiler)

    Common Functionality:
    - LLM interaction with streaming support
    - Tool calling and structured output
    - State management and checkpointing
    - Logging and metrics collection
    - Error handling and retry logic

    Attributes:
        agent_id: Unique identifier for this agent instance
        agent_type: Type identifier (e.g., 'RPA', 'GEN')
        agent_name: Human-readable name
        llm_client: Anthropic client for LLM calls
        tools: List of available tools
        prompt_templates: Agent-specific prompt templates
        streaming_callback: Callback for SSE event emission
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        agent_name: str,
        llm_client: Optional[AsyncAnthropic] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        streaming_callback: Optional[Callable] = None,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
    ):
        """
        Initialize the base agent.

        Args:
            agent_id: Unique identifier for this agent instance
            agent_type: Type identifier (e.g., 'RPA', 'GEN')
            agent_name: Human-readable name for display
            llm_client: Anthropic client for LLM calls
            tools: List of tools available to this agent
            streaming_callback: Callback for emitting SSE events
            model: Model name to use
            max_tokens: Maximum tokens for response
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.agent_name = agent_name
        self.llm_client = llm_client
        self.tools = tools or []
        self.streaming_callback = streaming_callback
        self.model = model
        self.max_tokens = max_tokens
        self.prompt_templates: Dict[str, str] = {}
        self._checkpoint_store: Dict[str, Dict[str, Any]] = {}
        self._logger = logging.getLogger(f"agent.{agent_type}.{agent_id}")

    @abstractmethod
    async def run(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute the agent's main task.

        This is the primary entry point for agent execution.
        Each agent type implements this method with its specific logic.

        Args:
            input_data: Task-specific input data
            context: Shared context including graph state, session info

        Yields:
            Dict[str, Any]: SSE events during execution
        """
        pass

    async def invoke_llm(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = True,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Invoke the LLM with optional streaming.

        Handles:
        - Message formatting
        - Tool binding
        - Streaming token output
        - Error handling and retries

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tools to bind
            stream: Whether to stream the response
            system_prompt: Optional system prompt

        Yields:
            str: Response tokens (if streaming) or full response
        """
        if self.llm_client is None:
            raise RuntimeError("LLM client not initialized")

        # Build request parameters
        request_params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }

        if system_prompt:
            request_params["system"] = system_prompt

        if tools:
            request_params["tools"] = tools

        try:
            if stream:
                async with self.llm_client.messages.stream(**request_params) as stream_response:
                    async for text in stream_response.text_stream:
                        yield text
            else:
                response = await self.llm_client.messages.create(**request_params)
                for block in response.content:
                    if hasattr(block, 'text'):
                        yield block.text
        except Exception as e:
            self.log("error", f"LLM invocation failed: {e}")
            raise

    async def invoke_llm_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Invoke LLM with tool use support.

        Args:
            messages: List of messages
            tools: Tools to make available
            system_prompt: System prompt

        Returns:
            Dict with response content and tool calls
        """
        if self.llm_client is None:
            raise RuntimeError("LLM client not initialized")

        request_params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }

        if system_prompt:
            request_params["system"] = system_prompt

        if tools:
            request_params["tools"] = tools

        response = await self.llm_client.messages.create(**request_params)

        result = {
            "content": [],
            "tool_calls": [],
            "stop_reason": response.stop_reason,
        }

        for block in response.content:
            if hasattr(block, 'text'):
                result["content"].append({"type": "text", "text": block.text})
            elif hasattr(block, 'type') and block.type == "tool_use":
                result["tool_calls"].append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        return result

    async def invoke_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Invoke a specific tool by name.

        Args:
            tool_name: Name of the tool to invoke
            tool_input: Input parameters for the tool

        Returns:
            Dict[str, Any]: Tool execution result

        Raises:
            ValueError: If tool not found
        """
        # Find tool by name
        tool = None
        for t in self.tools:
            if t.get("name") == tool_name:
                tool = t
                break

        if tool is None:
            raise ValueError(f"Tool '{tool_name}' not found")

        # Get tool handler
        handler = tool.get("handler")
        if handler is None:
            raise ValueError(f"Tool '{tool_name}' has no handler")

        # Execute tool
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(**tool_input)
            else:
                result = handler(**tool_input)
            return {"success": True, "result": result}
        except Exception as e:
            self.log("error", f"Tool execution failed: {e}", tool=tool_name)
            return {"success": False, "error": str(e)}

    async def emit_event(
        self,
        event_type: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Emit an SSE event via the streaming callback.

        Event types:
        - agent_thinking: Agent is processing
        - reasoning_step: Intermediate reasoning
        - node_preview: Preview node before finalization
        - node_finalized: Node confirmed
        - error: Error occurred

        Args:
            event_type: Type of event to emit
            data: Event payload data
        """
        if self.streaming_callback is None:
            return

        event = {
            "type": event_type,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "agent_name": self.agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        try:
            if asyncio.iscoroutinefunction(self.streaming_callback):
                await self.streaming_callback(event)
            else:
                self.streaming_callback(event)
        except Exception as e:
            self.log("error", f"Failed to emit event: {e}")

    def get_prompt(
        self,
        template_name: str,
        **kwargs: Any,
    ) -> str:
        """
        Get a formatted prompt from the agent's prompt templates.

        Args:
            template_name: Name of the prompt template
            **kwargs: Variables to substitute in the template

        Returns:
            str: Formatted prompt string
        """
        template = self.prompt_templates.get(template_name)
        if template is None:
            raise ValueError(f"Prompt template '{template_name}' not found")

        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")

    def register_prompt(self, name: str, template: str) -> None:
        """
        Register a prompt template.

        Args:
            name: Template name
            template: Template string with {variable} placeholders
        """
        self.prompt_templates[name] = template

    async def checkpoint(
        self,
        state: Dict[str, Any],
    ) -> str:
        """
        Save agent state to checkpoint for resumption.

        Args:
            state: State dictionary to checkpoint

        Returns:
            str: Checkpoint ID
        """
        checkpoint_id = str(uuid.uuid4())
        self._checkpoint_store[checkpoint_id] = {
            "state": state,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.log("debug", f"Created checkpoint: {checkpoint_id}")
        return checkpoint_id

    async def restore(
        self,
        checkpoint_id: str,
    ) -> Dict[str, Any]:
        """
        Restore agent state from checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to restore

        Returns:
            Dict[str, Any]: Restored state dictionary
        """
        checkpoint = self._checkpoint_store.get(checkpoint_id)
        if checkpoint is None:
            raise ValueError(f"Checkpoint '{checkpoint_id}' not found")

        self.log("debug", f"Restored checkpoint: {checkpoint_id}")
        return checkpoint["state"]

    def log(
        self,
        level: str,
        message: str,
        **extra: Any,
    ) -> None:
        """
        Log a message with agent context.

        Args:
            level: Log level ('debug', 'info', 'warning', 'error')
            message: Log message
            **extra: Additional context to include in log
        """
        log_data = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "agent_name": self.agent_name,
            **extra,
        }

        log_func = getattr(self._logger, level, self._logger.info)
        log_func(message, extra=log_data)

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable,
    ) -> None:
        """
        Register a tool for this agent.

        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON schema for tool input
            handler: Function to handle tool calls
        """
        self.tools.append({
            "name": name,
            "description": description,
            "input_schema": input_schema,
            "handler": handler,
        })

    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        Get tools formatted for LLM API.

        Returns:
            List of tool definitions without handlers
        """
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["input_schema"],
            }
            for t in self.tools
        ]

    async def think(self, thought: str) -> None:
        """
        Emit a thinking event.

        Args:
            thought: The agent's current thought
        """
        await self.emit_event("agent_thinking", {"thought": thought})

    async def reason(self, step: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Emit a reasoning step event.

        Args:
            step: Description of the reasoning step
            details: Additional details
        """
        await self.emit_event("reasoning_step", {
            "step": step,
            "details": details or {},
        })

    async def preview_node(self, node_data: Dict[str, Any]) -> None:
        """
        Emit a node preview event.

        Args:
            node_data: Preview node data
        """
        await self.emit_event("node_preview", {"node": node_data})

    async def finalize_node(self, node_data: Dict[str, Any]) -> None:
        """
        Emit a node finalized event.

        Args:
            node_data: Finalized node data
        """
        await self.emit_event("node_finalized", {"node": node_data})

    async def report_error(self, error: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Emit an error event.

        Args:
            error: Error message
            details: Additional error details
        """
        await self.emit_event("error", {
            "error": error,
            "details": details or {},
        })
