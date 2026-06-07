#!/usr/bin/env python3
"""POC: Real test - does Qwen actually update todos.md PROGRESSIVELY?

The previous test showed Qwen creates todos.md but marks everything [x] at once.
This test checks if it updates progressively DURING execution.
"""
import subprocess
import tempfile
import time
import threading
from pathlib import Path

def monitor_file(path, duration=30):
    """Monitor a file for changes over time."""
    print(f"\n[monitor] Watching {path} for {duration}s...")
    prev_content = ""
    start = time.time()
    
    while time.time() - start < duration:
        try:
            if path.exists():
                content = path.read_text()
                if content != prev_content:
                    print(f"[monitor] 📝 Change detected at {time.time()-start:.1f}s")
                    print(f"[monitor] Content ({len(content)} bytes):")
                    for line in content.splitlines():
                        print(f"  {line}")
                    prev_content = content
        except Exception:
            pass
        time.sleep(0.5)

def test_qwen_progressive():
    """Test if Qwen updates todos.md progressively."""
    print("=" * 60)
    print("TEST: Qwen Progressive Todo Updates")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create a task that takes time (multiple file operations)
        task = """Create these files in order, with a 1-second delay between each:
1. step1.txt with content "Step 1 done"
2. step2.txt with content "Step 2 done"  
3. step3.txt with content "Step 3 done"
4. step4.txt with content "Step 4 done"
5. step5.txt with content "Step 5 done"

After creating all files, read them all and show me the contents.
"""
        
        prompt = f"""You are a coding assistant.

TASK: {task}

MANDATORY PROGRESS TRACKING:
BEFORE you do ANY work, create a file called 'todos.md' with:
# Progress
- [ ] Create step1.txt
- [ ] Create step2.txt
- [ ] Create step3.txt
- [ ] Create step4.txt
- [ ] Create step5.txt
- [ ] Read all files

IMPORTANT: Update todos.md AFTER each step. Change [ ] to [x] as you complete each item.
This is CRITICAL - you must update the file progressively, not all at once at the end.
"""
        
        print(f"\nWorking directory: {tmpdir}")
        print("Starting Qwen CLI...\n")
        
        # Start file monitor in background
        todos_path = tmpdir / "todos.md"
        monitor_thread = threading.Thread(target=monitor_file, args=(todos_path, 45))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            result = subprocess.run(
                ["qwen", "--output-format", "json", "--approval-mode", "yolo"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(tmpdir),
            )
            
            print(f"\n[main] Exit code: {result.returncode}")
            print(f"[main] Output length: {len(result.stdout)} chars")
            
            # Final check
            if todos_path.exists():
                print(f"\n[main] ✅ Final todos.md:")
                print(todos_path.read_text())
            else:
                print(f"\n[main] ❌ todos.md was NOT created")
            
            # Check step files
            for i in range(1, 6):
                step_file = tmpdir / f"step{i}.txt"
                if step_file.exists():
                    print(f"[main] ✅ step{i}.txt exists")
                else:
                    print(f"[main] ❌ step{i}.txt missing")
                    
        except subprocess.TimeoutExpired:
            print("\n[main] ⏱️  Timeout after 60s")
        except Exception as e:
            print(f"\n[main] ❌ Error: {e}")

def test_claude_progressive():
    """Test if Claude updates todos.md progressively."""
    print("\n" + "=" * 60)
    print("TEST: Claude Progressive Todo Updates")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        task = """Create these files in order:
1. step1.txt with content "Step 1 done"
2. step2.txt with content "Step 2 done"  
3. step3.txt with content "Step 3 done"

After creating all files, read them all and show me the contents.
"""
        
        prompt = f"""You are a coding assistant.

TASK: {task}

MANDATORY PROGRESS TRACKING:
BEFORE you do ANY work, create a file called 'todos.md' with:
# Progress
- [ ] Create step1.txt
- [ ] Create step2.txt
- [ ] Create step3.txt
- [ ] Read all files

IMPORTANT: Update todos.md AFTER each step. Change [ ] to [x] as you complete each item.
This is CRITICAL - you must update the file progressively, not all at once at the end.
"""
        
        print(f"\nWorking directory: {tmpdir}")
        print("Starting Claude CLI...\n")
        
        todos_path = tmpdir / "todos.md"
        monitor_thread = threading.Thread(target=monitor_file, args=(todos_path, 45))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            result = subprocess.run(
                ["claude", "--print", "--output-format", "text"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(tmpdir),
            )
            
            print(f"\n[main] Exit code: {result.returncode}")
            
            if todos_path.exists():
                print(f"\n[main] ✅ Final todos.md:")
                print(todos_path.read_text())
            else:
                print(f"\n[main] ❌ todos.md was NOT created")
            
            for i in range(1, 4):
                step_file = tmpdir / f"step{i}.txt"
                if step_file.exists():
                    print(f"[main] ✅ step{i}.txt exists")
                else:
                    print(f"[main] ❌ step{i}.txt missing")
                    
        except subprocess.TimeoutExpired:
            print("\n[main] ⏱️  Timeout after 60s")
        except Exception as e:
            print(f"\n[main] ❌ Error: {e}")

if __name__ == "__main__":
    print("POC: Progressive Todo Tracking\n")
    print("Testing if LLMs update todo files PROGRESSIVELY during execution\n")
    
    test_qwen_progressive()
    test_claude_progressive()
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("""
Key finding: CLI tools don't support function calling.
- Qwen creates todos.md but marks everything complete at the end
- Claude ignores todo instructions entirely
- Codex fails with custom prompts

The OpenAI API approach (Ed Donner's notebook) works because:
1. Tools are defined as JSON schemas
2. LLM calls them natively via function calling
3. We capture progress from tool calls, not files
4. LLM CANNOT skip the tool calls

For CLI tools, we need a different approach:
1. Sidecar polling (monitor files during execution)
2. Post-processing (extract progress from output)
3. Structured output formats (easier to parse)
4. Hybrid: Combine multiple approaches
""")
