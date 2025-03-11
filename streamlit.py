# strmsm.py
import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import base64
from collections import Counter
from datetime import datetime, time as dtime
import time
import schedule
import threading
import smtplib
from email.mime.text import MIMEText
from nse1 import NSEReportsDownloader

st.set_page_config(page_title="NSE Reports Dashboard", page_icon="📈", layout="wide")

DOWNLOAD_FOLDER = r"C:\Users\srika\Downloads\sprngbrd_project\report_files"
CHROMEDRIVER_PATH = r"C:\Users\srika\Downloads\sprngbrd_project\chromedriver.exe"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "noreply.nsebot.downloader@gmail.com"
SMTP_PASSWORD = "valu tugl vgag uris"

if "users" not in st.session_state:
    st.session_state["users"] = {"admin": "password"}

def send_notification_email(email, date, download_time):
    subject = "NSE Reports Download Completed"
    body = f"""
    Hello,

    The scheduled download of NSE reports for {date} at {download_time} has completed successfully.
    Files are available in: {DOWNLOAD_FOLDER}

    Regards,
    NSE Reports Dashboard
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

def set_background(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.error(f"Background image not found at {image_path}")

def list_reports(directory):
    file_counts = Counter()
    if os.path.exists(directory):
        for root, _, files in os.walk(directory):
            folder_name = os.path.basename(root)
            file_counts[folder_name] += len(files)
    else:
        st.error(f"Directory '{directory}' not found!")
    return file_counts

def display_reports_chart(file_counts):
    file_counts = {folder: count for folder, count in file_counts.items() if folder != 'report_files' and count > 0}
    if file_counts:
        fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
        stylish_colors = ['#00FFFF', '#FF00FF', '#39FF14', '#FFFF00', '#FF1493', '#00FF7F']
        wedges, texts, autotexts = ax.pie(
            file_counts.values(),
            labels=file_counts.keys(),
            autopct='%1.0f%%',
            startangle=60,
            colors=stylish_colors[:len(file_counts)],
            wedgeprops={'edgecolor': 'black', 'linewidth': 1.3, 'antialiased': True},
            textprops={'fontsize': 16, 'color': 'white', 'weight': 'bold', 'family': 'Arial'}
        )
        for wedge in wedges:
            wedge.set_alpha(0.95)
        for autotext in autotexts:
            autotext.set_fontsize(11)
            autotext.set_color('#1A1A1A')
        fig.patch.set_facecolor('#121212')
        ax.set_facecolor('#121212')
        ax.set_title('Report Distribution', fontsize=28, fontweight='bold', color='#305CDE', pad=25)
        ax.axis('equal')
        with st.container():
            st.pyplot(fig)
    else:
        st.warning("No reports available to display.")

def read_log_file(log_path):
    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as log_file:
                lines = log_file.readlines()
            log_data = []
            for line in lines:
                parts = line.split(" - ", 2)
                if len(parts) == 3:
                    log_data.append({"Timestamp": parts[0], "Level": parts[1], "Message": parts[2].strip()})
            return pd.DataFrame(log_data) if log_data else pd.DataFrame()
        except Exception as e:
            st.error(f"Error reading log file: {str(e)}")
            return pd.DataFrame()
    else:
        st.warning(f"Log file not found at: {log_path}")
        return pd.DataFrame()

def run_scheduled_jobs():
    while True:
        schedule.run_pending()
        current_time = datetime.now()
        completed_jobs = []
        for job in schedule.jobs:
            if hasattr(job, 'next_run') and job.next_run < current_time:
                completed_jobs.append(job)
        for job in completed_jobs:
            schedule.cancel_job(job)
            if "scheduled_tasks" in st.session_state:
                st.session_state["scheduled_tasks"] = [
                    task for task in st.session_state["scheduled_tasks"]
                    if task['next_run'] > current_time
                ]
        time.sleep(1)

def login():
    st.title("🔐 NSE Reports Downloader")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if login_username in st.session_state["users"] and st.session_state["users"][login_username] == login_password:
                st.session_state["logged_in"] = True
                st.success(f"Welcome back, {login_username}!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    with tab2:
        st.subheader("Sign Up")
        signup_username = st.text_input("New Username", key="signup_username")
        signup_password = st.text_input("New Password", type="password", key="signup_password")
        signup_confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        if st.button("Sign Up"):
            if signup_username and signup_password and signup_confirm_password:
                if signup_username in st.session_state["users"]:
                    st.error("Username already exists!")
                elif signup_password != signup_confirm_password:
                    st.error("Passwords do not match!")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters long!")
                else:
                    st.session_state["users"][signup_username] = signup_password
                    st.success(f"Account created for {signup_username}! Please log in.")
            else:
                st.error("Please fill in all fields!")

def dashboard():
    set_background(r"C:\Users\srika\OneDrive\Pictures\Screenshots\Screenshot (167).png")
    st.title("📊 National Stock Exchange of India Limited")
    
    with st.sidebar:
        st.header("Navigation")
        option = st.radio("Select View", ["Home", "Reports", "Logs", "Visualize", "Schedule"], index=0)
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_button"):
            st.session_state["logged_in"] = False
            st.rerun()

    if option == "Home":
        st.subheader("Welcome to the NSE Reports Dashboard 📈")
        st.write("Monitor and download National Stock Exchange reports with ease.")
        
        # Stock Price Analysis from Selected File
        st.subheader("Stock Data Analysis")
        csv_files = [f for f in os.listdir(os.path.join(DOWNLOAD_FOLDER, "csv")) if f.endswith(".csv")]
        if csv_files:
            selected_file = st.selectbox("Select a file to analyze data", csv_files)
            if selected_file:
                downloader = NSEReportsDownloader(DOWNLOAD_FOLDER, CHROMEDRIVER_PATH)
                file_path = os.path.join(DOWNLOAD_FOLDER, "csv", selected_file)
                highest_value, highest_column, lowest_value, lowest_column = downloader.analyze_single_file(file_path)
                if highest_value != float('-inf') and lowest_value != float('inf'):
                    col1, col2 = st.columns(2)
                    with col1:
                        # Updated to show green upward arrow for Highest Value
                        st.metric(
                            label=f"Highest Value",
                            value=f"{highest_value:.2f}",
                            delta=f"{highest_value:.2f}",  # Delta relative to 0 for green arrow
                            delta_color="normal"  # Green for positive delta
                        )
                    with col2:
                        st.metric(
                            label=f"Lowest Value",
                            value=f"{lowest_value:.2f}",
                            delta=f"-{lowest_value:.2f}",  # Negative delta for red arrow
                            delta_color="normal"  # Red for negative delta
                        )
                else:
                    st.info("No numeric data found in the selected file.")
        else:
            st.info("No CSV files available. Please download reports containing numeric data.")

        st.subheader("Notification Preferences")
        if "notification_email" not in st.session_state:
            st.session_state["notification_email"] = ""
        current_email = st.session_state["notification_email"]
        email_input = st.text_input("Enter your email for notifications", value=current_email)
        
        col1, col2 = st.columns([2, 0.7])
        with col1:
            if st.button("Save Preference"):
                st.session_state["notification_email"] = email_input
                st.success(f"Email preference saved: {email_input}")
        with col2:
            if st.button("Test Email Notification"):
                if st.session_state["notification_email"]:
                    send_notification_email(st.session_state["notification_email"], "Test Date", "Test Time")
                    st.success("Test email sent")
                else:
                    st.error("Please save an email address first")

        st.subheader("Manual Download")
        target_date = st.date_input("Select Date to Download Reports Manually", datetime.now())
        if st.button("Download Reports"):
            with st.spinner("Downloading..."):
                progress_bar = st.progress(0)
                def update_progress(progress):
                    progress_bar.progress(progress)
                try:
                    downloader = NSEReportsDownloader(DOWNLOAD_FOLDER, CHROMEDRIVER_PATH, target_date.strftime('%d%m%Y'))
                    downloader.download_reports(progress_callback=update_progress)
                    st.success("Download successful!")
                except Exception as e:
                    st.error(f"Download failed: {str(e)}")
                progress_bar.empty()

    elif option == "Reports":
        file_counts = list_reports(DOWNLOAD_FOLDER)
        st.subheader("Report Summary")
        display_reports_chart(file_counts)
        st.subheader("Search and Filter Reports")
        search_query = st.text_input("Search Reports by Name")
        file_types = st.multiselect("Filter by File Type", list(NSEReportsDownloader(DOWNLOAD_FOLDER, CHROMEDRIVER_PATH).FILE_TYPES.keys()))
        
        if file_counts:
            st.write("**Filtered Reports:**")
            filtered_files = []
            for folder, count in file_counts.items():
                if folder in file_types or not file_types:
                    folder_path = os.path.join(DOWNLOAD_FOLDER, folder)
                    if os.path.exists(folder_path) and os.path.isdir(folder_path):
                        try:
                            files = os.listdir(folder_path)
                            for file in files:
                                if search_query.lower() in file.lower():
                                    filtered_files.append({"Name of the File": file, "Path of the File": folder_path})
                        except OSError as e:
                            st.error(f"Error accessing directory {folder_path}: {str(e)}")
                    else:
                        st.warning(f"Directory not found or inaccessible: {folder_path}")
            
            if filtered_files:
                files_df = pd.DataFrame(filtered_files)
                st.dataframe(files_df, use_container_width=True)
            else:
                st.info("No files match the search criteria.")
        else:
            st.warning("No reports found.")

    elif option == "Logs":
        log_file_path = os.path.join(DOWNLOAD_FOLDER, "logs", f"nse_downloads_{datetime.now().strftime('%Y%m%d')}.log")
        log_content = read_log_file(log_file_path)
        if not log_content.empty:
            st.dataframe(log_content, height=400, use_container_width=True)
        else:
            st.warning("No log data available.")

    elif option == "Visualize":
        st.subheader("Interactive Data Visualization")
        csv_files = [f for f in os.listdir(os.path.join(DOWNLOAD_FOLDER, "csv")) if f.endswith(".csv")]
        if csv_files:
            selected_file = st.selectbox("Select CSV to Visualize", csv_files)
            df = pd.read_csv(os.path.join(DOWNLOAD_FOLDER, "csv", selected_file))
            st.dataframe(df)
            if len(df.columns) >= 2:
                x_col = st.selectbox("Select X-axis", df.columns)
                y_col = st.selectbox("Select Y-axis", df.columns)
                chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Scatter"])
                if chart_type == "Bar":
                    fig = px.bar(df, x=x_col, y=y_col, title=f"{selected_file} - Bar Chart")
                elif chart_type == "Line":
                    fig = px.line(df, x=x_col, y=y_col, title=f"{selected_file} - Line Chart")
                else:
                    fig = px.scatter(df, x=x_col, y=y_col, title=f"{selected_file} - Scatter Chart")
                st.plotly_chart(fig)
            else:
                st.warning("CSV file must have at least two columns for visualization.")
        else:
            st.warning("No CSV files available for visualization.")

    elif option == "Schedule":
        st.subheader("Schedule Downloads")
        if "scheduled_tasks" not in st.session_state:
            st.session_state["scheduled_tasks"] = []

        col1, col2 = st.columns(2)
        with col1:
            sched_time = st.time_input("Set Download Time", value=dtime(9, 0))
        with col2:
            target_date = st.date_input("Select Date for Scheduled Download", datetime.now())
        
        if st.button("Schedule Download"):
            scheduled_datetime = datetime.combine(target_date, sched_time)
            if scheduled_datetime > datetime.now():
                notification_email = st.session_state.get("notification_email", "")

                def scheduled_download():
                    downloader = NSEReportsDownloader(DOWNLOAD_FOLDER, CHROMEDRIVER_PATH, target_date.strftime('%d%m%Y'))
                    downloader.download_reports()
                    if notification_email:
                        send_notification_email(notification_email, target_date.strftime("%d-%m-%Y"), sched_time.strftime("%H:%M"))
                
                job = schedule.every().day.at(sched_time.strftime("%H:%M")).do(scheduled_download)
                st.session_state["scheduled_tasks"].append({
                    "time": sched_time.strftime("%H:%M"),
                    "date": target_date.strftime("%d-%m-%Y"),
                    "next_run": scheduled_datetime,
                    "job": job
                })
                st.success(f"Scheduled daily download at {sched_time.strftime('%H:%M')} for {target_date.strftime('%d-%m-%Y')}")
            else:
                st.error("Cannot schedule a task in the past!")

        if st.session_state["scheduled_tasks"]:
            st.subheader("Scheduled Tasks")
            tasks_df = pd.DataFrame([
                {"Date": task["date"], "Time": task["time"], "Status": "Pending" if task["next_run"] > datetime.now() else "Completed"}
                for task in st.session_state["scheduled_tasks"]
            ])
            st.dataframe(tasks_df, use_container_width=True)

            st.subheader("Cancel Scheduled Tasks")
            tasks_to_cancel = st.multiselect(
                "Select tasks to cancel",
                [f"{task['date']} at {task['time']}" for task in st.session_state["scheduled_tasks"] if task["next_run"] > datetime.now()]
            )
            if st.button("Cancel Selected Tasks"):
                for task_str in tasks_to_cancel:
                    date, time_str = task_str.split(" at ")
                    for task in st.session_state["scheduled_tasks"]:
                        if task["date"] == date and task["time"] == time_str:
                            schedule.cancel_job(task["job"])
                            st.session_state["scheduled_tasks"].remove(task)
                            st.success(f"Cancelled task: {task_str}")
                st.rerun()
        else:
            st.info("No scheduled tasks yet.")

        if "scheduler_thread" not in st.session_state:
            st.session_state["scheduler_thread"] = threading.Thread(target=run_scheduled_jobs, daemon=True)
            st.session_state["scheduler_thread"].start()

def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if st.session_state["logged_in"]:
        dashboard()
    else:
        login()

if __name__ == "__main__":
    main()
