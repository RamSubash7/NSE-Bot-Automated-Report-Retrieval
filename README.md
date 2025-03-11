# NSE-Bot-Automated-Report-Retrieval
#Documentation
Project Title- NSEBot: Automated Report Retrieval

Introduction
Overview
The "NSE Reports Downloader and Dashboard" is a Python-based application designed to
automate the downloading of reports from the National Stock Exchange of India (NSE)
website and provide an interactive dashboard for managing and visualizing these reports.
The primary objective is to streamline access to financial data, enhance data analysis
capabilities, and improve user experience through a graphical interface. This project is
significant for financial analysts, researchers, and enthusiasts who require timely NSE data
for decision-making.

Project Scope
Boundaries
● Included: Automated downloading of NSE reports for a specified date, file
organization by type (e.g., CSV, PDF), basic CSV data analysis (highest/lowest
values), and a Streamlit dashboard with features like login, report visualization,
scheduling, and email notifications.
● Excluded: Real-time stock price monitoring, advanced data analytics beyond
min/max values, integration with external financial APIs, and mobile app support.
Limitations and Constraints
● Dependency on the NSE website’s structure, which may break if the site updates.
● Requires a local ChromeDriver executable and internet connectivity.
● Limited to files available on the NSE "All Reports" page
(https://www.nseindia.com/all-reports).
● Email credentials are hardcoded, posing a security risk in production.

Requirements
Functional Requirements
● Users can download NSE reports manually or schedule downloads for a specific date
and time.
● Downloaded files are organized into folders based on file type (e.g., csv, pdf).
● The dashboard supports user authentication (login/signup), report filtering, and
visualization of CSV data.
● Email notifications are sent upon completion of scheduled downloads.
● Logs are generated to track download progress and errors.
Non-Functional Requirements
● The system should handle at least 50 report downloads per session without crashing.
● Response time for manual downloads should be under 5 minutes.
● The interface should be user-friendly and visually appealing.
● Logs must be persistent and readable for debugging.

User Stories
● As a financial analyst, I want to download NSE reports for a specific date so that I
can analyze market trends.
● As a user, I want to schedule downloads and receive notifications so that I don’t miss
daily updates.
● As an admin, I want to visualize report data interactively to quickly identify key
metrics.

Technical Stack
Programming Languages
● Python: Core language for both the downloader and dashboard.
Frameworks/Libraries
● Selenium: For web scraping and automation of report downloads.
● Streamlit: For building the interactive web-based dashboard.
● Pandas: For CSV data processing and analysis.
● Matplotlib: For static pie chart visualization of report distribution.
● Plotly: For interactive data visualizations (bar, line, scatter charts).
● Requests: For HTTP requests during file downloads.
● Schedule: For scheduling download tasks.
Tools/Platforms
● ChromeDriver: WebDriver for Selenium to interact with Chrome.
● SMTP (Gmail): For sending email notifications.
● Windows OS: Development and testing environment (inferred from file paths).

Architecture/Design
System Architecture
The system consists of two main components:
1. NSEReportsDownloader (nse1.py):
○ Uses Selenium to scrape report links from the NSE website.
○ Downloads files using requests with session management and organizes
them into folders.
○ Provides a method to analyze CSV files.
2. Streamlit Dashboard (strmsm.py):
○ Frontend interface for user interaction.
○ Integrates with the downloader for manual and scheduled tasks.
○ Handles visualization, authentication, and notifications.

High-Level Interaction
● User → Streamlit Dashboard → NSEReportsDownloader → NSE Website →
Downloaded Files → Dashboard Visualization.
● Web Automation Module: Automates report downloads using Selenium, with dynamic
interaction and evasion techniques.
● File Management Module: Handles file extraction, organizes files by type, and
manages duplicates using file hash checks.
● UI Module: Provides a dashboard with tabs for Home, Reports, Logs, Visualization,
and Scheduling.
● Notification Module: Sends detailed email alerts using SMTP, including download
status and log summaries.
● Scheduler Module: Automates downloads using the Schedule library, with options for
manual execution.
● Analytics Module: Analyzes CSV files to identify highest and lowest values and
visualizes data using Streamlit and Plotly.

Design Decisions
● Selenium: Chosen for its ability to handle dynamic content and JavaScript-heavy
websites.
● Streamlit: Selected for rapid UI development and built-in visualization support.
● File-Based Storage: Opted for simplicity over a database due to small data volume.
Trade-Offs
● Selenium vs. API: Selenium was used despite potential fragility because no public
NSE API was available, trading reliability for functionality.
● Hardcoded Credentials: Sacrificed security for ease of setup in a prototype phase.

Development
Technologies and Frameworks
● Selenium automates browser interactions to scrape and download reports.
● Streamlit provides a reactive UI with minimal setup.
● Pandas processes CSV files for analysis and visualization.
Coding Standards
● Followed PEP 8 for Python code style (e.g., consistent indentation, meaningful
variable names).
● Used docstrings and comments for key methods (e.g., NSEReportsDownloader).
● Modular design with separate files for downloader and dashboard logic.
Challenges and Solutions
● Dynamic Website: NSE’s JavaScript-driven content required Selenium with waits
and dynamic element handling (interact_with_dynamic_elements).
● File Duplicates: Handled by checking and removing existing files before
downloading (handle_duplicate_file).
● Scheduling: Implemented a background thread with schedule library to run tasks
without blocking the UI.

Testing
Testing Approach
● Unit Tests: Tested analyze_single_file with sample CSV files to verify min/max value
extraction.
● Integration Tests: Verified downloader-dashboard integration by manually triggering
downloads and checking file organization.
● System Tests: Ran the full application to ensure login, download, and visualization
worked end-to-end.
Results
● Successfully downloaded reports for the selected date, and organized them.
● Identified and fixed a bug where duplicate files weren’t deleted due to permissions
(added error handling in handle_duplicate_file).
● Visualization failed for CSVs with non-numeric data; mitigated by adding checks in
analyze_single_file.

Deployment
Deployment Process
● Local Deployment:
1. Install dependencies: pip install selenium streamlit pandas matplotlib plotly
requests schedule.
2. Download and place ChromeDriver.
3. Run python nse1.py for standalone downloader or streamlit run strmsm.py for
the dashboard.

Instructions
● Environment: Windows 10/11 with Python 3.8+.
● Setup: Ensure DOWNLOAD_FOLDER and CHROMEDRIVER_PATH match your
system paths.
● Run: Use a terminal to execute the scripts.

User Guide
Instructions
1. Login: Use admin/password or sign up with a new account.
2. Manual Download: Go to "Home", select a date, and click "Download Reports".
3. Schedule Download: In "Schedule", set a time/date and click "Schedule Download".
4. View Reports: Navigate to "Reports" to filter and see downloaded files.
5. Visualize: In "Visualize", select a CSV and choose chart options.
Troubleshooting
● Download Fails: Check internet connection and ChromeDriver path.
● Visualization Errors: Ensure CSV has numeric columns.
● Email Not Sent: Verify SMTP credentials and internet access.

Conclusion
Outcomes
The project successfully automates NSE report downloads, organizes files, and provides an
interactive dashboard for data management and visualization. It achieved its goal of
simplifying access to financial data.

Lessons Learned
● Selenium’s dependency on website structure highlights the need for robust error
handling.
● Hardcoding sensitive data (e.g., email passwords) is impractical for production use.
● Streamlit is powerful for quick prototypes but limited for complex state management.
Areas for Improvement
● Replace Selenium with an API if available.
● Use environment variables for credentials.
● Add advanced analytics (e.g., trend analysis, predictive modeling).

References
● NSE Website: https://www.nseindia.com/all-reports
● Streamlit Docs: https://docs.streamlit.io/
● Selenium Docs: https://www.selenium.dev/documentation/
● Python Docs: https://docs.python.org/3/
