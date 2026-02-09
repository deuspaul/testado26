# testado26

This repository contains a small Python CLI application skeleton for managing a simple todo list.

Files added in this branch:

- `src/todo.py`: A minimal CLI using `argparse` with `add` and `list` commands. Tasks are stored as JSON in `tasks.json`.
- `tasks.json`: JSON file used to persist tasks (starts empty).
- `requirements.txt`: Lists dependencies (none required; uses standard library).

Usage examples:

Add a task:

```bash
python3 src/todo.py add --title "Buy milk" --desc "2 liters"
```

List tasks:

```bash
python3 src/todo.py list
```
# testado26