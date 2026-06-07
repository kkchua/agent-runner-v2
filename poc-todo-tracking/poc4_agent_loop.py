#!/usr/bin/env python3
"""POC: Agent Loop with Function Calling for CLI Tools

This is the REAL solution. Instead of hoping the LLM will create/update todo files,
we build an agent loop that:
1. Defines tools as JSON schemas (create_todos, mark_complete)
2. Passes tools to the LLM via CLI
3. Captures tool calls from LLM output
4. Executes tool calls locally
5. Feeds results back to LLM
6. Repeats until done

This mirrors Ed Donner's OpenAI API pattern but works with CLI tools.
"""
import json
import subprocess
import tempfile
import time
import re
from pathlib import Path
from typing import Any

# ============================================================================
# Todo State (managed by host, not LLM)
# ============================================================================

class TodoTracker:
    """Manages todo state and progress tracking."""
    
    def __init__(self):
        self.todos: list[str] = []
        self.completed: list[bool] = []
        self.notes: list[str] = []
    
    def create_todos(self, descriptions: list[str]) -> str:
        """Create todo list."""
        self.todos.extend(descriptions)
        self.completed.extend([False] * len(descriptions))
        self.notes.extend([""] * len(descriptions))
        
        result = f"Created {len(descriptions)} todos:\n"
        for i, desc in enumerate(descriptions, 1):
            result += f"  {i}. {desc}\n"
        print(f"[todo] 📋 {desc}")
        return result
    
    def mark_complete(self, index: int, notes: str = "") -> str:
        """Mark todo as complete."""
        if 1 <= index <= len(self.todos):
            self.completed[index - 1] = True
            self.notes[index - 1] = notes
            print(f"[todo] ✅ #{index}: {self.todos[index-1]}")
            if notes:
                print(f"   {notes}")
            return f"Marked #{index} as complete"
        return f"Error: Invalid index {index}"
    
    def get_status(self) -> str:
        """Get current todo status."""
        lines = ["Todo Status:"]
        for i, todo in enumerate(self.todos):
            status = "✅" if self.completed[i] else "⏳"
            line = f"  {i+1}. {status} {todo}"
            if self.notes[i]:
                line += f" - {self.notes[i]}"
            lines.append(line)
        
        done = sum(self.completed)
        total = len(self.todos)
        lines.append(f"\nProgress: {done}/{total} ({done/total*100:.0f}%)" if total > 0 else "\nProgress: 0/0")
        return "\n".join(lines)
    
    @property
    def is_complete(self) -> bool:
        return len(self.todos) > 0 and all(self.completed)


# ============================================================================
# Tool Definitions
# ============================================================================

TOOL_DEFINITIONS = {
    "create_todos": {
        "description": "Create a todo list with descriptions. Call this FIRST to plan your work.",
        "parameters": {
            "type": "object",
            "properties": {
                "descriptions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of todo item descriptions"
                }
            },
            "required": ["descriptions"]
        }
    },
    "mark_complete": {
        "description": "Mark a todo as complete. Call this when you finish each item.",
        "parameters": {
            "type": "object",
            "properties": {
                "index": {
                    "type": "integer",
                    "description": "1-based index of the todo to mark complete"
                },
                "notes": {
                    "type": "string",
                    "description": "Brief notes about what was done"
                }
            },
            "required": ["index", "notes"]
        }
    }
}

# ============================================================================
# Tool Call Extraction (from LLM text output)
# ============================================================================

def extract_tool_calls(text: str) -> list[dict]:
    """Extract tool calls from LLM text output.
    
    The LLM will output tool calls in this format:
    ```tool_call
    {"tool": "create_todos", "args": {"descriptions": ["...", "..."]}}
    ```
    
    Or inline:
    TOOL_CALL: {"tool": "mark_complete", "args": {"index": 1, "notes": "Done"}}
    """
    tool_calls = []
    
    # Pattern 1: Code blocks with tool_call
    pattern1 = r'```tool_call\s*\n(.*?)\n```'
    for match in re.finditer(pattern1, text, re.DOTALL):
        try:
            call = json.loads(match.group(1))
            if "tool" in call and "args" in call:
                tool_calls.append(call)
        except json.JSONDecodeError:
            pass
    
    # Pattern 2: Inline TOOL_CALL:
    pattern2 = r'TOOL_CALL:\s*(\{.*?\})'
    for match in re.finditer(pattern2, text):
        try:
            call = json.loads(match.group(1))
            if "tool" in call and "args" in call:
                tool_calls.append(call)
        except json.JSONDecodeError:
            pass
    
    # Pattern 3: JSON lines starting with {"tool":
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('{"tool":') or line.startswith('{"tool":'):
            try:
                call = json.loads(line)
                if "tool" in call and "args" in call:
                    tool_calls.append(call)
            except json.JSONDecodeError:
                pass
    
    return tool_calls


# ============================================================================
# Agent Loop
# ============================================================================

class AgentLoop:
    """Agent loop that wraps CLI tools with function calling."""
    
    def __init__(self, cli_cmd: list[str], cli_kwargs: dict = None):
        self.cli_cmd = cli_cmd
        self.cli_kwargs = cli_kwargs or {}
        self.tracker = TodoTracker()
        self.messages: list[dict] = []
        self.max_turns = 15
    
    def execute_tool(self, tool_call: dict) -> str:
        """Execute a tool call and return result."""
        tool_name = tool_call.get("tool", "")
        args = tool_call.get("args", {})
        
        if tool_name == "create_todos":
            return self.tracker.create_todos(args.get("descriptions", []))
        elif tool_name == "mark_complete":
            return self.tracker.mark_complete(
                args.get("index", 0),
                args.get("notes", "")
            )
        else:
            return f"Error: Unknown tool {tool_name}"
    
    def build_prompt(self, task: str) -> str:
        """Build prompt with tool instructions."""
        return f"""You are a coding assistant. You have access to tools for tracking your progress.

TOOLS AVAILABLE:
1. create_todos: Create a todo list with descriptions
   Format: ```tool_call
   {{"tool": "create_todos", "args": {{"descriptions": ["Step 1", "Step 2"]}}}}
   ```

2. mark_complete: Mark a todo as complete
   Format: ```tool_call
   {{"tool": "mark_complete", "args": {{"index": 1, "notes": "What was done"}}}}
   ```

MANDATORY WORKFLOW:
1. FIRST: Call create_todos() with your plan
2. THEN: Do the work
3. AFTER EACH STEP: Call mark_complete() with the index and notes
4. FINALLY: Provide summary to user

TASK: {task}

IMPORTANT: You MUST use the tools above. Do NOT skip create_todos.
Call mark_complete after EACH step, not all at the end.
"""
    
    def run(self, task: str) -> dict:
        """Run the agent loop."""
        print(f"=== Agent Loop Started ===")
        print(f"Task: {task}\n")
        
        # Build initial prompt
        prompt = self.build_prompt(task)
        
        for turn in range(self.max_turns):
            print(f"\n--- Turn {turn + 1} ---")
            
            # Call CLI tool
            try:
                result = subprocess.run(
                    self.cli_cmd,
                    input=prompt,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    **self.cli_kwargs
                )
                
                output = result.stdout
                
                if result.returncode != 0:
                    print(f"[error] CLI returned {result.returncode}")
                    print(f"[error] stderr: {result.stderr[:500]}")
                    break
                
                print(f"[output] {len(output)} chars")
                
                # Extract tool calls
                tool_calls = extract_tool_calls(output)
                
                if tool_calls:
                    print(f"[tools] Found {len(tool_calls)} tool calls")
                    
                    # Execute each tool call
                    tool_results = []
                    for call in tool_calls:
                        result = self.execute_tool(call)
                        tool_results.append(f"Tool result: {result}")
                    
                    # Feed results back to LLM
                    prompt = f"Tool execution results:\n" + "\n".join(tool_results) + "\n\nContinue your work. Remember to call mark_complete() after each step."
                    
                else:
                    # No tool calls - LLM provided final answer
                    print(f"[final] {output[:500]}")
                    break
                    
            except subprocess.TimeoutExpired:
                print("[error] Timeout")
                break
            except Exception as e:
                print(f"[error] {e}")
                break
        
        # Final status
        print(f"\n=== Final Status ===")
        print(self.tracker.get_status())
        
        return {
            "todos": self.tracker.todos,
            "completed": self.tracker.completed,
            "notes": self.tracker.notes,
            "progress": f"{sum(self.tracker.completed)}/{len(self.tracker.todos)}"
        }


# ============================================================================
# Test Cases
# ============================================================================

def test_qwen_agent_loop():
    """Test agent loop with Qwen CLI."""
    print("\n" + "=" * 60)
    print("TEST: Qwen Agent Loop")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        loop = AgentLoop(
            cli_cmd=["qwen", "--output-format", "json", "--approval-mode", "yolo"],
            cli_kwargs={"cwd": tmpdir}
        )
        
        result = loop.run("""Create 3 files:
1. hello1.txt with "Hello 1"
2. hello2.txt with "Hello 2"
3. hello3.txt with "Hello 3"
Then read them all and show contents.
""")
        
        print(f"\nResult: {result}")


def test_claude_agent_loop():
    """Test agent loop with Claude CLI."""
    print("\n" + "=" * 60)
    print("TEST: Claude Agent Loop")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        loop = AgentLoop(
            cli_cmd=["claude", "--print", "--output-format", "text"],
            cli_kwargs={"cwd": tmpdir}
        )
        
        result = loop.run("""Create 3 files:
1. hello1.txt with "Hello 1"
2. hello2.txt with "Hello 2"
3. hello3.txt with "Hello 3"
Then read them all and show contents.
""")
        
        print(f"\nResult: {result}")


if __name__ == "__main__":
    print("POC: Agent Loop with Function Calling for CLI Tools\n")
    print("This demonstrates the REAL solution:\n")
    print("1. Define tools as JSON schemas")
    print("2. Pass tools to LLM via prompt")
    print("3. Extract tool calls from LLM output")
    print("4. Execute tool calls locally")
    print("5. Feed results back to LLM")
    print("6. Repeat until done\n")
    
    # Test with Qwen (fastest)
    test_qwen_agent_loop()
    
    # Test with Claude
    # test_claude_agent_loop()
    
    print("\n" + "=" * 60)
    print("KEY INSIGHT")
    print("=" * 60)
    print("""
The OpenAI API approach works because function calling is NATIVE.
The LLM MUST call tools - it can't skip them.

For CLI tools, we approximate this by:
1. Defining tools in the prompt
2. Asking LLM to output tool calls in a specific format
3. Extracting and executing tool calls locally
4. Feeding results back

This is FRAGILE because:
- LLM may not follow the format
- LLM may skip tool calls
- Extraction is regex-based

BETTER APPROACH:
For agent-runner-v2, we should:
1. Use the OpenAI API directly for function calling (when possible)
2. For CLI tools, use sidecar polling + post-processing
3. Define clear tool schemas in prompts
4. Validate tool call output before proceeding
""")
