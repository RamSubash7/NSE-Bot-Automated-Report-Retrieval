# nse1.py
import os
import time
import random
import requests
import logging
import shutil
import hashlib
import re
import csv
from datetime import datetime
from urllib.parse import urljoin, parse_qs, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NSEReportsDownloader:
    """NSE Reports Downloader Class"""
    def __init__(self, download_folder=None, chromedriver_path=None, target_date=None):
        if download_folder is None or chromedriver_path is None:
            raise ValueError("Both download_folder and chromedriver_path must be provided")
        self.PAGE_URL = "https://www.nseindia.com/all-reports"
        self.BASE_URL = "https://www.nseindia.com"
        self.DOWNLOAD_FOLDER = download_folder
        self.CHROMEDRIVER_PATH = chromedriver_path
        self.LOGS_FOLDER = os.path.join(download_folder, 'logs')
        os.makedirs(self.LOGS_FOLDER, exist_ok=True)
        self.logger = logging.getLogger('NSEDownloader')
        self.logger.setLevel(logging.INFO)
        log_file = os.path.join(self.LOGS_FOLDER, f'nse_downloads_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        self.target_date = target_date if target_date else datetime.now().strftime('%d%m%Y')
        self.TODAY_DATE = self.target_date
        self.TODAY_DATE_ALT = datetime.strptime(self.target_date, '%d%m%Y').strftime('%d-%m-%Y')
        self.TODAY_DATE_SHORT = datetime.strptime(self.target_date, '%d%m%Y').strftime('%d%b%Y').upper()
        self.REPORT_PATTERNS = {
            'series_change': {'button_text': ['Series', 'Change', 'Report'], 'url_pattern': 'series_change', 'section_id': 'cr_equity_daily_Current'},
            'shortselling': {'button_text': ['Short', 'Selling'], 'url_pattern': 'shortselling', 'section_id': 'cr_equity_daily_Current'}
        }
        self.SPECIFIC_SECTIONS = [
            '//*[@id="cr_equity_daily_Current"]/div/div[1]', '//div[contains(@class, "reportsDownload")]',
            '//div[contains(@class, "row col-12")]', '//div[contains(@class, "col-lg-4 col-md-4 col-sm-6 my-2")]',
            '//div[contains(@class, "tab-pane")]', '//div[contains(@class, "reportSelection")]',
            '//div[contains(@id, "equityArchives")]'
        ]
        self.FILE_TYPES = {
            "csv": ["csv"], "pdf": ["pdf"], "xls": ["xls", "xlsx"], "zip": ["zip"], "dat": ["dat"],
            "dbf": ["dbf"], "txt": ["txt"], "doc": ["doc", "docx"], "xml": ["xml"], "json": ["json"]
        }
        self.setup_directories()

    def setup_directories(self):
        os.makedirs(self.DOWNLOAD_FOLDER, exist_ok=True)
        for folder in self.FILE_TYPES.keys():
            os.makedirs(os.path.join(self.DOWNLOAD_FOLDER, folder), exist_ok=True)

    def get_file_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def handle_duplicate_file(self, file_path):
        if not os.path.exists(file_path):
            return False
        try:
            os.remove(file_path)
            self.logger.info(f"Deleted duplicate file: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting duplicate file: {str(e)}")
            return False

    def setup_driver(self):
        options = Options()
        prefs = {
            "download.default_directory": os.path.abspath(self.DOWNLOAD_FOLDER),
            "download.prompt_for_download": False,
            "safebrowsing.enabled": True,
            "profile.default_content_settings.popups": 0,
            "plugins.always_open_pdf_externally": True,
            "download.extensions_to_open": "doc,docx",
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        service = Service(self.CHROMEDRIVER_PATH)
        return webdriver.Chrome(service=service, options=options)

    def wait_for_page_load(self, driver):
        try:
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container-fluid")))
            time.sleep(5)
        except Exception as e:
            self.logger.error(f"Error waiting for page load: {str(e)}")

    def interact_with_dynamic_elements(self, driver):
        try:
            current_elements = driver.find_elements(By.XPATH, "//button[contains(text(), 'Current') or contains(text(), 'Today')]")
            for elem in current_elements:
                try:
                    driver.execute_script("arguments[0].click();", elem)
                    time.sleep(2)
                except:
                    continue
            expand_elements = driver.find_elements(By.XPATH, "//button[contains(@class, 'collapse') or contains(@data-toggle, 'collapse')]")
            for elem in expand_elements:
                try:
                    driver.execute_script("arguments[0].click();", elem)
                    time.sleep(1)
                except:
                    continue
        except Exception as e:
            self.logger.error(f"Error interacting with dynamic elements: {str(e)}")

    def is_today_report(self, url):
        if not url:
            return False
        url_lower = url.lower()
        if any(date in url_lower for date in [self.TODAY_DATE.lower(), self.TODAY_DATE_ALT.lower(), self.TODAY_DATE_SHORT.lower()]):
            return True
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            for param_values in query_params.values():
                for value in param_values:
                    if any(date.lower() in value.lower() for date in [self.TODAY_DATE, self.TODAY_DATE_ALT, self.TODAY_DATE_SHORT]):
                        return True
        except:
            pass
        return False

    def _extract_section_links(self, section, all_links):
        try:
            links = section.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    href = link.get_attribute("href")
                    data_link = link.get_attribute("data-link")
                    if href and self.is_today_report(href):
                        all_links.add(href)
                    if data_link and self.is_today_report(data_link):
                        all_links.add(data_link)
                except:
                    continue
            buttons = section.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                try:
                    data_link = button.get_attribute("data-link")
                    onclick = button.get_attribute("onclick")
                    if data_link and self.is_today_report(data_link):
                        all_links.add(data_link)
                    if onclick:
                        url_match = re.search(r"['\"](https?://[^'\"]+)['\"]", onclick)
                        if url_match and self.is_today_report(url_match.group(1)):
                            all_links.add(url_match.group(1))
                except:
                    continue
        except Exception as e:
            self.logger.debug(f"Error extracting section links: {str(e)}")

    def _handle_specific_report(self, driver, pattern, all_links):
        try:
            sections = driver.find_elements(By.ID, pattern['section_id'])
            for section in sections:
                try:
                    xpath_condition = " or ".join([f"contains(text(), '{text}')" for text in pattern["button_text"]])
                    xpath_query = f".//*[{xpath_condition}]"
                    elements = section.find_elements(By.XPATH, xpath_query)
                    for elem in elements:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                            time.sleep(1)
                            elem.click()
                            time.sleep(2)
                            download_elements = section.find_elements(By.XPATH, 
                                f".//*[contains(@href, '{pattern['url_pattern']}') or contains(@data-link, '{pattern['url_pattern']}')]")
                            for download_elem in download_elements:
                                href = download_elem.get_attribute("href")
                                data_link = download_elem.get_attribute("data-link")
                                if href and self.is_today_report(href):
                                    all_links.add(href)
                                if data_link and self.is_today_report(data_link):
                                    all_links.add(data_link)
                        except Exception as e:
                            self.logger.debug(f"Error interacting with element: {str(e)}")
                except Exception as e:
                    self.logger.debug(f"Error processing section: {str(e)}")
        except Exception as e:
            self.logger.debug(f"Error handling specific report pattern: {str(e)}")

    def extract_links(self, driver):
        all_links = set()
        wait = WebDriverWait(driver, 10)
        for xpath in self.SPECIFIC_SECTIONS:
            try:
                sections = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
                for section in sections:
                    try:
                        if 'collapse' in section.get_attribute('class', ''):
                            driver.execute_script("arguments[0].classList.remove('collapse')", section)
                            time.sleep(1)
                        self._extract_section_links(section, all_links)
                    except Exception as e:
                        self.logger.debug(f"Error processing section: {str(e)}")
            except Exception as e:
                self.logger.debug(f"Error with xpath {xpath}: {str(e)}")
        for report_type, pattern in self.REPORT_PATTERNS.items():
            try:
                self._handle_specific_report(driver, pattern, all_links)
            except Exception as e:
                self.logger.debug(f"Error handling {report_type}: {str(e)}")
        try:
            all_elements = driver.find_elements(By.XPATH, "//a[@href] | //*[@data-link]")
            for elem in all_elements:
                href = elem.get_attribute("href")
                data_link = elem.get_attribute("data-link")
                if href and self.is_today_report(href):
                    all_links.add(href)
                if data_link and self.is_today_report(data_link):
                    all_links.add(data_link)
        except Exception as e:
            self.logger.debug(f"Error searching for all links: {str(e)}")
        for link in all_links:
            self.logger.debug(f"Found link for download: {link}")
        self.logger.info(f"Total unique links found for {self.TODAY_DATE_ALT}: {len(all_links)}")
        return all_links

    def download_file(self, url, session, cookies, max_retries=3):
        filename = url.split('/')[-1]
        file_path = os.path.join(self.DOWNLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            self.handle_duplicate_file(file_path)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        if url.lower().endswith(('.doc', '.docx')):
            headers.update({'Accept': 'application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document, */*'})
        if 'series_change' in url.lower():
            headers.update({'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json, text/javascript, */*; q=0.01'})
        for attempt in range(max_retries):
            try:
                response = session.get(url, headers=headers, cookies=cookies, stream=True, timeout=60)
                if response.status_code == 200:
                    content_disposition = response.headers.get('Content-Disposition')
                    if content_disposition:
                        filename_match = re.search(r'filename=["\'](.*)["\']', content_disposition)
                        if filename_match:
                            filename = filename_match.group(1)
                            file_path = os.path.join(self.DOWNLOAD_FOLDER, filename)
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    self.logger.info(f"Successfully downloaded {filename}")
                    return True
            except Exception as e:
                self.logger.error(f"Error downloading {filename} (Attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 5))
        return False

    def organize_files(self):
        self.logger.info("Organizing Downloaded Files...")
        for file in os.listdir(self.DOWNLOAD_FOLDER):
            file_path = os.path.join(self.DOWNLOAD_FOLDER, file)
            if os.path.isfile(file_path):
                file_ext = file.split(".")[-1].lower()
                for folder, extensions in self.FILE_TYPES.items():
                    if file_ext in extensions:
                        dest_folder = os.path.join(self.DOWNLOAD_FOLDER, folder)
                        new_path = os.path.join(dest_folder, file)
                        if os.path.exists(new_path):
                            self.handle_duplicate_file(new_path)
                        try:
                            shutil.move(file_path, new_path)
                            self.logger.info(f"Moved {file} to {folder}/")
                        except Exception as e:
                            self.logger.error(f"Error moving file {file}: {str(e)}")
                        break
        self.logger.info("Successfully Organised Files")

    def analyze_single_file(self, file_path):
        """Analyze a single CSV file for highest and lowest values in any numeric column"""
        highest_value = float('-inf')
        lowest_value = float('inf')
        highest_column = None
        lowest_column = None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                # Collect all values for each column
                column_values = {header: [] for header in headers}
                for row in reader:
                    for header in headers:
                        value = row.get(header, '').strip()
                        column_values[header].append(value)
                
                # Find numeric columns and their min/max values
                for header, values in column_values.items():
                    numeric_values = []
                    for value in values:
                        try:
                            num = float(value)
                            numeric_values.append(num)
                        except ValueError:
                            continue
                    
                    if numeric_values:  # If column has numeric values
                        column_max = max(numeric_values)
                        column_min = min(numeric_values)
                        if column_max > highest_value:
                            highest_value = column_max
                            highest_column = header
                        if column_min < lowest_value:
                            lowest_value = column_min
                            lowest_column = header
                
            if highest_column and lowest_column:
                self.logger.info(f"Analyzed {os.path.basename(file_path)}: Highest value {highest_value} in {highest_column}, Lowest value {lowest_value} in {lowest_column}")
            else:
                self.logger.info(f"No numeric columns found in {os.path.basename(file_path)}")
                
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {str(e)}")
        
        return highest_value, highest_column, lowest_value, lowest_column

    def download_reports(self, progress_callback=None):
        driver = None
        session = requests.Session()
        successful_downloads = 0
        try:
            self.logger.info(f"Starting download process for reports dated {self.TODAY_DATE_ALT}...")
            driver = self.setup_driver()
            driver.get(self.PAGE_URL)
            self.wait_for_page_load(driver)
            self.interact_with_dynamic_elements(driver)
            cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
            download_links = self.extract_links(driver)
            if not download_links:
                self.logger.warning("No downloadable links found for the target date's reports!")
                return
            self.logger.info(f"Found {len(download_links)} files to download for {self.TODAY_DATE_ALT}")
            total_links = len(download_links)
            for i, link in enumerate(download_links):
                if link and isinstance(link, str):
                    if self.download_file(link, session, cookies):
                        successful_downloads += 1
                    if progress_callback:
                        progress_callback((i + 1) / total_links)
            self.organize_files()
            self.logger.info(f"Download process completed. Successfully downloaded {successful_downloads} out of {len(download_links)} files.")
        except Exception as e:
            self.logger.error(f"Error during download process: {str(e)}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
if __name__ == "__main__":
    DOWNLOAD_FOLDER = r"C:\Users\srika\Downloads\sprngbrd_project\report_files"
    CHROMEDRIVER_PATH = r"C:\Users\srika\Downloads\sprngbrd_project\chromedriver.exe"
    downloader = NSEReportsDownloader(download_folder=DOWNLOAD_FOLDER, chromedriver_path=CHROMEDRIVER_PATH)
    downloader.download_reports()
