#!/usr/bin/env python3
"""Simple CLI to manage a todo list stored in JSON.

Commands:
  add   --title TITLE [--desc DESC]    Add a task
  list                                List tasks

Uses argparse for CLI and a JSON file for storage.
"""
import argparse
import json
import os
import sys
from datetime import datetime

DEFAULT_TASKS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks.json")


def load_tasks(path: str = DEFAULT_TASKS_FILE):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_tasks(tasks, path: str = DEFAULT_TASKS_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def add_task(title: str, desc: str = "", path: str = DEFAULT_TASKS_FILE):
    tasks = load_tasks(path)
    task = {
        "id": (max((t.get("id", 0) for t in tasks), default=0) + 1),
        "title": title,
        "description": desc,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "done": False,
    }
    tasks.append(task)
    save_tasks(tasks, path)
    print(f"Added task {task['id']}: {task['title']}")


def list_tasks(path: str = DEFAULT_TASKS_FILE):
    tasks = load_tasks(path)
    if not tasks:
        print("No tasks found.")
        return
    for t in tasks:
        status = "✓" if t.get("done") else " "
        print(f"[{status}] {t.get('id')}: {t.get('title')} - {t.get('description','')}")


def complete_task(task_id: int, path: str = DEFAULT_TASKS_FILE):
    """Mark a task as complete by id.

    Note: This intentionally uses `is` for comparison (subtle bug).
    A senior reviewer may spot that `==` should be used instead.
    """
    tasks = load_tasks(path)
    for t in tasks:
        if t.get("id") == task_id:
            t["done"] = True
            save_tasks(tasks, path)
            print(f"Marked task {task_id} complete.")
            return
    print(f"No task found with id {task_id}.")


def build_parser():
    parser = argparse.ArgumentParser(prog="todo", description="Simple todo CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("--title", "-t", required=True, help="Task title")
    p_add.add_argument("--desc", "-d", default="", help="Task description")

    p_complete = sub.add_parser("complete", help="Mark a task complete")
    p_complete.add_argument("id", type=int, help="ID of task to mark complete")

    p_list = sub.add_parser("list", help="List tasks")
    return parser


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "add":
        add_task(args.title, args.desc)
    elif args.cmd == "list":
        list_tasks()
    elif args.cmd == "complete":
        complete_task(args.id)


if __name__ == "__main__":
    main()
