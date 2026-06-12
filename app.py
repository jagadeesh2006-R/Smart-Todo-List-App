import streamlit as st # type: ignore
import sqlite3
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
from datetime import date

conn = sqlite3.connect("todo.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT,
    priority TEXT,
    due_date TEXT,
    status TEXT
)
""")
conn.commit()

def add_task(task, priority, due_date):
    c.execute(
        "INSERT INTO tasks(task, priority, due_date, status) VALUES(?,?,?,?)",
        (task, priority, due_date, "Pending")
    )
    conn.commit()

def get_tasks():
    c.execute("SELECT * FROM tasks")
    return c.fetchall()

def update_status(task_id):
    c.execute(
        "UPDATE tasks SET status='Completed' WHERE id=?",
        (task_id,)
    )
    conn.commit()

def delete_task(task_id):
    c.execute(
        "DELETE FROM tasks WHERE id=?",
        (task_id,)
    )
    conn.commit()

st.set_page_config(
    page_title="Smart To-Do List",
    layout="wide"
)

st.title("✅ Smart To-Do List App")

st.subheader("Add New Task")

task = st.text_input("Task Name")

priority = st.selectbox(
    "Priority",
    ["High", "Medium", "Low"]
)

due_date = st.date_input(
    "Due Date",
    min_value=date.today()
)

if st.button("Add Task"):
    if task:
        add_task(task, priority, str(due_date))
        st.success("Task Added Successfully!")

tasks = get_tasks()

df = pd.DataFrame(
    tasks,
    columns=["ID","Task","Priority","Due Date","Status"]
)

if not df.empty:

    total = len(df)

    completed = len(
        df[df["Status"]=="Completed"]
    )

    pending = len(
        df[df["Status"]=="Pending"]
    )

    progress = (completed/total)*100

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total Tasks", total)
    col2.metric("Completed", completed)
    col3.metric("Pending", pending)
    col4.metric("Progress %", f"{progress:.1f}")

    st.divider()

    st.subheader("Task List")

    for index,row in df.iterrows():

        col1,col2,col3,col4,col5,col6 = st.columns(
            [3,1,1,1,1,1]
        )

        col1.write(row["Task"])
        col2.write(row["Priority"])
        col3.write(row["Due Date"])
        col4.write(row["Status"])

        if row["Status"]=="Pending":
            if col5.button("Complete",key=f"c{row['ID']}"):
                update_status(row["ID"])
                st.rerun()
        if col6.button(
            "Delete",
            key=f"d{row['ID']}"
        ):
            delete_task(row["ID"])
            st.rerun()

    st.divider()

    st.subheader("Task Analytics")

    status_counts = (
        df["Status"]
        .value_counts()
        .reset_index()
    )

    status_counts.columns = [
        "Status",
        "Count"
    ]

    fig = px.pie(
        status_counts,
        names="Status",
        values="Count",
        title="Completed vs Pending Tasks"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:
    st.info("No Tasks Added Yet.")