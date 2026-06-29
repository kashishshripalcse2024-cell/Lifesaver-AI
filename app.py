from flask import Flask, render_template, request, redirect
import sqlite3
import google.generativeai as genai

app = Flask(__name__)
# Configure Gemini AI
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


# ---------- AI Priority ----------
def get_ai_priority(task):

    task = task.lower()

    high = [
        "exam",
        "interview",
        "hackathon",
        "submission",
        "deadline",
        "urgent"
    ]

    medium = [
        "python",
        "project",
        "assignment",
        "study",
        "meeting"
    ]

    for word in high:
        if word in task:
            return "High Priority"

    for word in medium:
        if word in task:
            return "Medium Priority"

    return "Low Priority"


# ---------- AI Suggestion ----------
def get_ai_suggestion(task):
    try:
        prompt = f"""
You are an intelligent productivity assistant.

The user has this task:
{task}

Give:
1. One short productivity suggestion.
2. One motivational sentence.

Keep the answer under 50 words.
"""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print("Gemini Error:", e)
        return "💡 Break this task into smaller steps."

    

@app.route("/", methods=["GET", "POST"])
def home():

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    # Add Task
    if request.method == "POST":

        task = request.form["task"]
        date = request.form["date"]
        priority = get_ai_priority(task)
        suggestion = get_ai_suggestion(task)

        cursor.execute(
            """
            INSERT INTO tasks(task, date, priority)
            VALUES (?, ?, ?)
            """,
            (f"{task} | {suggestion}", date, priority)
        )

        conn.commit()

    # Search
    search = request.args.get("search", "").strip()

    if search:
        cursor.execute(
            """
            SELECT id, task, date, priority, completed
            FROM tasks
            WHERE LOWER(task) LIKE LOWER(?)
            """,
            ('%' + search + '%',)
        )
    else:
        cursor.execute(
            """
            SELECT id, task, date, priority, completed
            FROM tasks
            ORDER BY id DESC
            """
        )

    tasks = cursor.fetchall()

    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task[4] == 1)
    pending_tasks = total_tasks - completed_tasks
    if total_tasks > 0:
        progress = int((completed_tasks / total_tasks) * 100)
    else:
         progress = 0

    conn.close()

    return render_template(
        "index.html",
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        progress=progress,
        search=search
    )


@app.route("/complete/<int:id>")
def complete(id):

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tasks SET completed=1 WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)