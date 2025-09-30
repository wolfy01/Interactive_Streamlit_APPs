import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd

TASK_FILE = "tasks.json"

# ------------------ Helpers ------------------ #
def load_tasks():
    if os.path.exists(TASK_FILE):
        try:
            with open(TASK_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def get_time_remaining(due_date_str):
    """Return time left until due date, or expired status."""
    if not due_date_str:
        return "No due date"
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
    now = datetime.now()
    diff = due_date - now
    if diff.total_seconds() <= 0:
        return "⏰ Overdue!"
    days, seconds = diff.days, diff.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m left"

# ------------------ App ------------------ #
def todo_list():
    st.set_page_config(page_title="Advanced To-Do List", page_icon="📝")
    st.title("📝 Advanced To-Do List")
    st.markdown("Manage tasks with **due dates, completion tracking, snooze options, and export**.")

    tasks = load_tasks()

    # ---------------- Add Task ---------------- #
    with st.expander("➕ Add a New Task"):
        new_task = st.text_input("Task name:")
        due_date = st.date_input("Due date:")
        due_time = st.time_input("Due time:")
        if st.button("Add Task", type="primary"):
            if new_task.strip():
                due_datetime = datetime.combine(due_date, due_time).strftime("%Y-%m-%d %H:%M")
                tasks.append({"task": new_task.strip(), "due": due_datetime, "status": "pending"})
                save_tasks(tasks)
                st.success("✅ Task added successfully!")
                st.rerun()
            else:
                st.warning("⚠️ Task cannot be empty.")

    # ---------------- Pending Tasks ---------------- #
    pending = [t for t in tasks if t["status"] == "pending"]

    if pending:
        st.subheader("📌 Pending Tasks")
        for i, task in enumerate(pending):
            col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
            col1.write(f"**{task['task']}**")
            col2.write(get_time_remaining(task["due"]))

            # Mark completed
            if col3.button("✅ Done", key=f"done_{i}"):
                task["status"] = "completed"
                save_tasks(tasks)
                st.success(f"Task '{task['task']}' marked as completed.")
                st.rerun()

            # Snooze buttons
            if col4.button("⏰ +1d", key=f"snooze_day_{i}"):
                due = datetime.strptime(task["due"], "%Y-%m-%d %H:%M")
                task["due"] = (due + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
                save_tasks(tasks)
                st.info(f"Task '{task['task']}' snoozed for 1 day.")
                st.rerun()

            if col5.button("⏰ +1w", key=f"snooze_week_{i}"):
                due = datetime.strptime(task["due"], "%Y-%m-%d %H:%M")
                task["due"] = (due + timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M")
                save_tasks(tasks)
                st.info(f"Task '{task['task']}' snoozed for 1 week.")
                st.rerun()

    else:
        st.info("🎉 No pending tasks. You're all caught up!")

    # ---------------- Completed Tasks ---------------- #
    completed = [t for t in tasks if t["status"] == "completed"]
    if completed:
        with st.expander("✅ Completed Tasks"):
            for t in completed:
                st.write(f"~~{t['task']}~~ (due {t['due']})")

    # ---------------- Export Tasks ---------------- #
    st.subheader("📤 Export Tasks")
    if tasks:
        df = pd.DataFrame(tasks)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download as CSV", data=csv, file_name="tasks.csv", mime="text/csv")

        st.download_button(
            "⬇️ Download as JSON",
            data=json.dumps(tasks, indent=4),
            file_name="tasks.json",
            mime="application/json"
        )

    # ---------------- Clear All ---------------- #
    if tasks and st.button("🗑️ Clear All Tasks"):
        save_tasks([])
        st.warning("All tasks cleared.")
        st.rerun()

if __name__ == "__main__":
    todo_list()
