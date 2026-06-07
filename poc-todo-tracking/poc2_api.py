#!/usr/bin/env python3
"""POC 2: Test function calling with Claude API (not CLI)

Anthropic API supports tool use natively.
This demonstrates the same create_todos/mark_complete pattern with Claude.
"""
import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path

# ============================================================================
# Test 1: Claude API via anthropic Python SDK
# ============================================================================

def test_claude_api():
    """Test Claude API with native tool use."""
    print("=" * 60)
    print("TEST 1: Claude API (anthropic SDK)")
    print("=" * 60)
    
    try:
        import anthropic
    except ImportError:
        print("⚠️  anthropic SDK not installed. Install with: pip install anthropic")
        return None
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not set")
        return None
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Define tools
    tools = [
        {
            "name": "create_todos",
            "description": "Create a todo list with descriptions",
            "input_schema": {
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
        {
            "name": "mark_complete",
            "description": "Mark a todo as complete",
            "input_schema": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "1-based index of todo to mark complete"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notes about completion"
                    }
                },
                "required": ["index", "notes"]
            }
        }
    ]
    
    # Todo state
    todos = []
    completed = []
    
    def handle_tool_use(tool_name, tool_input):
        if tool_name == "create_todos":
            descriptions = tool_input["descriptions"]
            todos.extend(descriptions)
            completed.extend([False] * len(descriptions))
            print(f"[todo] Created {len(descriptions)} items:")
            for i, t in enumerate(descriptions, 1):
                print(f"  {i}. {t}")
            return f"Created {len(descriptions)} todos"
        elif tool_name == "mark_complete":
            idx = tool_input["index"]
            notes = tool_input["notes"]
            if 1 <= idx <= len(todos):
                completed[idx - 1] = True
                print(f"[todo] ✓ Item {idx} completed: {todos[idx-1]}")
                if notes:
                    print(f"  Notes: {notes}")
                return f"Marked item {idx} as complete"
            return f"Invalid index: {idx}"
        return f"Unknown tool: {tool_name}"
    
    # Build messages
    messages = [
        {"role": "user", "content": """Create a file called 'hello.txt' in /tmp with content "Hello from Claude API".
Then read it back and show me the contents.

MANDATORY: Before doing anything, call create_todos() with your plan.
After each step, call mark_complete() with the index and notes."""}
    ]
    
    print("\nSending request to Claude API...\n")
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=tools,
            messages=messages,
        )
        
        print(f"Response stop reason: {response.stop_reason}")
        print(f"Response usage: input={response.usage.input_tokens}, output={response.usage.output_tokens}")
        
        # Process response
        tool_results = []
        for content in response.content:
            if content.type == "tool_use":
                tool_name = content.name
                tool_input = content.input
                tool_id = content.id
                
                print(f"\n[tool_call] {tool_name}({json.dumps(tool_input)})")
                
                result = handle_tool_use(tool_name, tool_input)
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": [{"type": "text", "text": str(result)}]
                })
            elif content.type == "text":
                print(f"\n[text] {content.text}")
        
        # If there were tool calls, continue the conversation
        if tool_results:
            print("\n--- Continuing with tool results ---\n")
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            
            response2 = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                tools=tools,
                messages=messages,
            )
            
            print(f"Response 2 stop reason: {response2.stop_reason}")
            for content in response2.content:
                if content.type == "tool_use":
                    tool_name = content.name
                    tool_input = content.input
                    tool_id = content.id
                    
                    print(f"\n[tool_call] {tool_name}({json.dumps(tool_input)})")
                    
                    result = handle_tool_use(tool_name, tool_input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": [{"type": "text", "text": str(result)}]
                    })
                elif content.type == "text":
                    print(f"\n[text] {content.text}")
            
            # Final continuation
            if tool_results:
                messages.append({"role": "assistant", "content": response2.content})
                messages.append({"role": "user", "content": tool_results})
                
                response3 = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    tools=tools,
                    messages=messages,
                )
                
                print(f"\nResponse 3 stop reason: {response3.stop_reason}")
                for content in response3.content:
                    if content.type == "text":
                        print(f"\n[text] {content.text}")
        
        # Check if file was created
        hello_path = Path("/tmp/hello.txt")
        if hello_path.exists():
            print(f"\n✅ hello.txt was created!")
            print(f"Content: {hello_path.read_text()}")
        else:
            print(f"\n❌ hello.txt was NOT created")
        
        print(f"\nFinal todo state: {len(todos)} todos, {sum(completed)} completed")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# Test 2: OpenAI API with function calling
# ============================================================================

def test_openai_api():
    """Test OpenAI API with native function calling."""
    print("\n" + "=" * 60)
    print("TEST 2: OpenAI API (gpt-4o)")
    print("=" * 60)
    
    try:
        from openai import OpenAI
    except ImportError:
        print("⚠️  openai SDK not installed. Install with: pip install openai")
        return None
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set")
        return None
    
    client = OpenAI(api_key=api_key)
    
    # Define tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_todos",
                "description": "Create a todo list with descriptions",
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
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mark_complete",
                "description": "Mark a todo as complete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "index": {
                            "type": "integer",
                            "description": "1-based index of todo to mark complete"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about completion"
                        }
                    },
                    "required": ["index", "notes"]
                }
            }
        }
    ]
    
    # Todo state
    todos = []
    completed = []
    
    def handle_tool_call(tool_name, arguments):
        args = json.loads(arguments) if isinstance(arguments, str) else arguments
        if tool_name == "create_todos":
            descriptions = args["descriptions"]
            todos.extend(descriptions)
            completed.extend([False] * len(descriptions))
            print(f"[todo] Created {len(descriptions)} items:")
            for i, t in enumerate(descriptions, 1):
                print(f"  {i}. {t}")
            return f"Created {len(descriptions)} todos"
        elif tool_name == "mark_complete":
            idx = args["index"]
            notes = args["notes"]
            if 1 <= idx <= len(todos):
                completed[idx - 1] = True
                print(f"[todo] ✓ Item {idx} completed: {todos[idx-1]}")
                if notes:
                    print(f"  Notes: {notes}")
                return f"Marked item {idx} as complete"
            return f"Invalid index: {idx}"
        return f"Unknown tool: {tool_name}"
    
    # Build messages
    messages = [
        {"role": "user", "content": """Create a file called 'hello_openai.txt' in /tmp with content "Hello from OpenAI API".
Then read it back and show me the contents.

MANDATORY: Before doing anything, call create_todos() with your plan.
After each step, call mark_complete() with the index and notes."""}
    ]
    
    print("\nSending request to OpenAI API...\n")
    
    try:
        max_turns = 10
        for turn in range(max_turns):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
            )
            
            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason
            
            print(f"Turn {turn + 1}: finish_reason={finish_reason}")
            
            if finish_reason == "tool_calls":
                for tc in message.tool_calls:
                    print(f"\n[tool_call] {tc.function.name}({tc.function.arguments})")
                    result = handle_tool_call(tc.function.name, tc.function.arguments)
                    messages.append(message)
                    messages.append({
                        "role": "tool",
                        "content": result,
                        "tool_call_id": tc.id,
                    })
            else:
                print(f"\n[text] {message.content}")
                messages.append(message)
                break
        
        # Check if file was created
        hello_path = Path("/tmp/hello_openai.txt")
        if hello_path.exists():
            print(f"\n✅ hello_openai.txt was created!")
            print(f"Content: {hello_path.read_text()}")
        else:
            print(f"\n❌ hello_openai.txt was NOT created")
        
        print(f"\nFinal todo state: {len(todos)} todos, {sum(completed)} completed")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("POC 2: Function Calling with Claude and OpenAI APIs\n")
    
    # Test Claude API
    claude_ok = test_claude_api()
    
    # Test OpenAI API
    openai_ok = test_openai_api()
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Claude API: {'✅ PASS' if claude_ok else '❌ FAIL'}")
    print(f"OpenAI API: {'✅ PASS' if openai_ok else '❌ FAIL'}")
