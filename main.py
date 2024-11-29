from cProfile import label

import flet as ft
import sqlite3
from datetime import datetime



def create_db():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        due_date TEXT,
        priority TEXT,
        completed BOOLEAN NOT NULL CHECK (completed IN (0, 1))
    )
    """)
    conn.commit()
    conn.close()


def add_task_to_db(task, due_date, priority):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO tasks (task, due_date, priority, completed) 
    VALUES (?, ?, ?, 0)
    """, (task, due_date, priority))
    conn.commit()
    conn.close()


def get_all_tasks_from_db():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def mark_task_completed(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def delete_task_from_db(task_id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def update_task_in_db(task_id, task, due_date, priority):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE tasks SET task = ?, due_date = ?, priority = ? WHERE id = ?
    """, (task, due_date, priority, task_id))
    conn.commit()
    conn.close()



def main(page: ft.Page):
    # Set page style
    page.title = "Modern To-Do List"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 20

    task_input = ft.TextField(label="Task Description", autofocus=True)
    due_date_input = ft.TextField(label='Due Date', autofocus=True)
    priority_input = ft.Dropdown(label="Priority", options=[
        ft.dropdown.Option("Low"),
        ft.dropdown.Option("Medium"),
        ft.dropdown.Option("High"),
    ])

    task_list = ft.Column()

    def refresh_task_list():
        task_list.controls.clear()
        tasks = get_all_tasks_from_db()
        for task in tasks:
            task_id, task_desc, due_date, priority, completed = task
            task_text = f"{task_desc} (Due: {due_date} | Priority: {priority})"
            task_status = "Completed" if completed else "Incomplete"
            task_row = ft.Row(
                controls=[
                    ft.Text(f"{task_text} [{task_status}]"),
                    ft.IconButton(ft.icons.CHECK, on_click=lambda e, task_id=task_id: mark_completed(task_id)),
                    ft.IconButton(ft.icons.EDIT, on_click=lambda e, task_id=task_id: edit_task(task_id)),
                    ft.IconButton(ft.icons.DELETE, on_click=lambda e, task_id=task_id: delete_task(task_id)),
                ]
            )
            task_list.controls.append(task_row)
        page.update()

    def add_task(e):
        task_desc = task_input.value
        due_date = due_date_input.value
        priority = priority_input.value

        if task_desc:
            add_task_to_db(task_desc, due_date, priority)
            refresh_task_list()
            task_input.value = ""
            due_date_input.value = None
            priority_input.value = None
            page.update()

    def mark_completed(task_id):
        mark_task_completed(task_id)
        refresh_task_list()

    def delete_task(task_id):
        delete_task_from_db(task_id)
        refresh_task_list()

    def edit_task(task_id):
        task_desc = task_input.value
        due_date = due_date_input.value
        priority = priority_input.value
        if task_desc:
            update_task_in_db(task_id, task_desc, due_date, priority)
            refresh_task_list()


    add_button = ft.ElevatedButton("Add Task", on_click=add_task)
    refresh_task_list()

    page.add(
        task_input,
        due_date_input,
        priority_input,
        add_button,
        task_list
    )


create_db()

ft.app(target=main)