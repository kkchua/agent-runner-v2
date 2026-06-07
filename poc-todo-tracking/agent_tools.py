#!/usr/bin/env python3
"""Agent tools for todo tracking — executed locally, not via API."""

class TodoTracker:
    def __init__(self):
        self.todos: list[str] = []
        self.completed: list[bool] = []
        self.notes: list[str] = []

    def create_todos(self, descriptions: list[str]) -> str:
        self.todos.extend(descriptions)
        self.completed.extend([False] * len(descriptions))
        self.notes.extend([""] * len(descriptions))
        result = f"Created {len(descriptions)} todos:\n"
        for i, desc in enumerate(descriptions, 1):
            result += f"  {i}. {desc}\n"
        return result

    def mark_complete(self, index: int, notes: str = "") -> str:
        if 1 <= index <= len(self.todos):
            self.completed[index - 1] = True
            self.notes[index - 1] = notes
            return f"Marked #{index} complete: {self.todos[index-1]}"
        return f"Error: Invalid index {index}"

    def get_status(self) -> str:
        lines = ["Todo Status:"]
        for i, todo in enumerate(self.todos):
            status = "✅" if self.completed[i] else "⏳"
            lines.append(f"  {i+1}. {status} {todo}")
        done = sum(self.completed)
        total = len(self.todos)
        lines.append(f"\nProgress: {done}/{total}")
        return "\n".join(lines)

    @property
    def is_complete(self) -> bool:
        return len(self.todos) > 0 and all(self.completed)
