"""
Udemy certificate validator.
Handles validation of Udemy certificate URLs and metadata extraction.
"""

import re
import os
import time
import random
from datetime import datetime
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from .base_validator import BaseValidator


class UdemyValidator(BaseValidator):
    """Validator for Udemy certificates."""
    
    def __init__(self):
        """Initialize Udemy validator."""
        super().__init__()
        # Udemy certificate URL pattern: /certificate/UC-[A-Z0-9]+/ (HTTPS only)
        self.url_pattern = re.compile(r'^https://(?:www\.)?udemy\.com/certificate/UC-[A-Z0-9]+/?$')
        # List of common user agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
    
    def validate_url_pattern(self, url: str) -> bool:
        """
        Validate Udemy certificate URL pattern.
        
        Args:
            url: The certificate URL to validate
            
        Returns:
            True if URL matches Udemy pattern, False otherwise
        """
        return bool(self.url_pattern.match(url))
    
    def _setup_webdriver(self, use_new_headless=True) -> Optional[webdriver.Chrome]:
        """
        Set up and configure Chrome WebDriver.
        
        Returns:
            Configured Chrome WebDriver instance or None if setup fails
        """
        try:
            chrome_options = Options()
            if use_new_headless:
                chrome_options.add_argument("--headless=new")
            else:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
            chrome_options.add_argument("--disable-site-isolation-trials")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={random.choice(self.user_agents)}")
            chrome_options.add_argument("--single-process")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(60)
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            return None
    
    def _extract_metadata_from_html(self, content: str) -> Tuple[Dict, bool]:
        """
        Extract metadata from HTML content.
        
        Args:
            content: HTML content to parse
            
        Returns:
            Tuple of (metadata dictionary, success boolean)
        """
        metadata = {}
        success = False
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find the certificate description container
            description_div = soup.find('div', {'data-purpose': 'certificate-description'})
            if description_div:
                self.logger.info("Found certificate description div")
                
                # Extract name
                name_element = description_div.find('a', {'data-purpose': 'certificate-recipient-url'})
                if name_element:
                    metadata["name"] = name_element.get_text(strip=True)
                    self.logger.info(f"Found name: {metadata['name']}")
                
                # Extract course title
                course_element = description_div.find('a', {'data-purpose': 'certificate-course-url'})
                if course_element:
                    metadata["course"] = course_element.get_text(strip=True)
                    self.logger.info(f"Found course: {metadata['course']}")
                
                # Extract instructor name
                instructor_element = description_div.find('a', href=re.compile(r'/user/'))
                if instructor_element:
                    metadata["instructor"] = instructor_element.get_text(strip=True)
                    self.logger.info(f"Found instructor: {metadata['instructor']}")
                
                # Extract issue date from the description text
                description_text = description_div.get_text()
                date_match = re.search(r'on (\d{2}/\d{2}/\d{4})', description_text)
                if date_match:
                    date_text = date_match.group(1)
                    metadata["issue_date"] = self._parse_date(date_text)
                    self.logger.info(f"Found date: {metadata['issue_date']}")
                
                success = True
            else:
                self.logger.warning("Could not find certificate description div")
                # Log all divs with data-purpose attributes for debugging
                for div in soup.find_all('div', attrs={'data-purpose': True}):
                    self.logger.debug(f"Found div with data-purpose: {div.get('data-purpose')}")
        
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {str(e)}")
        
        return metadata, success
    
    def extract_metadata(self, url: str) -> Dict:
        """
        Extract metadata from Udemy certificate page.
        
        Args:
            url: The Udemy certificate URL
            
        Returns:
            Dictionary containing extracted metadata
        """
        self.logger.info(f"Extracting metadata from Udemy URL: {url}")
        
        # Get certificate ID from URL
        certificate_id = self._extract_certificate_id(url)
        
        # Initialize metadata with basic information
        metadata = {
            "certificate_id": certificate_id,
            "platform": "Udemy",
            "verification_url": url
        }
        
        max_retries = 3
        retry_delay = 5
        selenium_success = False
        
        for attempt in range(max_retries):
            driver = None
            try:
                self.logger.info(f"Attempt {attempt + 1} of {max_retries}")
                
                # Try new headless first, fallback to old headless if needed
                driver = self._setup_webdriver(use_new_headless=(attempt == 0))
                if not driver:
                    continue
                
                # Navigate to the certificate page
                driver.get(url)
                
                # Wait for the page to load
                time.sleep(retry_delay + random.uniform(1, 3))  # Add some randomness
                
                # Log the page title for debugging
                self.logger.info(f"Page title: {driver.title}")
                
                # Try to find the certificate description
                try:
                    # First wait for body to be present
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Then wait for the certificate description
                    description_element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-purpose="certificate-description"]'))
                    )
                    
                    # Log the found element's text for debugging
                    self.logger.info(f"Found description element: {description_element.text}")
                    
                except TimeoutException:
                    self.logger.warning("Timeout waiting for certificate description, trying to proceed anyway")
                    # Log the page source for debugging
                    self.logger.debug(f"Page source: {driver.page_source}")
                
                # Get the page source
                content = driver.page_source
                
                # Extract metadata from HTML
                extracted_metadata, success = self._extract_metadata_from_html(content)
                
                if success:
                    metadata.update(extracted_metadata)
                    selenium_success = True
                    break
                else:
                    self.logger.warning(f"Failed to extract metadata on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
            
            except WebDriverException as e:
                self.logger.error(f"WebDriver error: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            except Exception as e:
                self.logger.error(f"Error extracting metadata: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception as e:
                        self.logger.error(f"Error closing WebDriver: {str(e)}")
        
        # Fallback: Use requests and BeautifulSoup if Selenium fails
        if not selenium_success:
            try:
                import requests
                self.logger.warning("Selenium failed, using requests/BeautifulSoup fallback for Udemy certificate.")
                headers = {"User-Agent": random.choice(self.user_agents)}
                resp = requests.get(url, headers=headers, timeout=30)
                if resp.status_code == 200:
                    extracted_metadata, success = self._extract_metadata_from_html(resp.text)
                    if success:
                        metadata.update(extracted_metadata)
                else:
                    self.logger.error(f"Fallback HTTP request failed with status {resp.status_code}")
            except Exception as e:
                self.logger.error(f"Fallback requests/BeautifulSoup error: {str(e)}")
        
        self.logger.info(f"Extracted metadata: {metadata}")
        return metadata
    
    def check_certificate_status(self, metadata: Dict) -> str:
        """
        Check the status of the Udemy certificate.
        
        Args:
            metadata: Extracted certificate metadata
            
        Returns:
            Certificate status: "Valid", "Expired", "Revoked", or "Invalid"
        """
        if not metadata:
            return "Invalid"
        
        # Check if certificate has required fields
        required_fields = ["name", "course", "issue_date"]
        if not all(metadata.get(field) for field in required_fields):
            return "Invalid"
        
        # Check issue date (certificates older than 10 years might be suspicious)
        if metadata.get("issue_date"):
            try:
                issue_date = datetime.strptime(metadata["issue_date"], "%Y-%m-%d")
                if issue_date < datetime(2010, 1, 1):
                    return "Invalid"  # Suspiciously old
            except (ValueError, TypeError):
                pass
        
        return "Valid"
    
    def _extract_certificate_id(self, url: str) -> str:
        """
        Extract certificate ID from Udemy URL.
        
        Args:
            url: The Udemy certificate URL
            
        Returns:
            Certificate ID
        """
        match = re.search(r'/certificate/(UC-[A-Z0-9]+)', url)
        return match.group(1) if match else "unknown"
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """
        Parse date from various formats to YYYY-MM-DD.
        
        Args:
            date_text: Date string to parse
            
        Returns:
            Date in YYYY-MM-DD format, or None if parsing fails
        """
        if not date_text:
            return None
        
        # Common date formats
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",  # "06/09/2019" - Udemy format
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_text.strip(), fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If no format matches, try to extract year-month-day pattern
        year_month_day = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', date_text)
        if year_month_day:
            year, month, day = year_month_day.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return None
    
    def _extract_percentage(self, text: str) -> Optional[int]:
        """
        Extract percentage from text.
        
        Args:
            text: Text containing percentage
            
        Returns:
            Percentage as integer, or None if not found
        """
        if not text:
            return None
        
        # Look for percentage pattern
        percentage_match = re.search(r'(\d+)%', text)
        if percentage_match:
            return int(percentage_match.group(1))
        
        return None
    
    def _get_mock_metadata(self, certificate_id: str) -> Dict:
        """
        Get mock metadata for demonstration purposes.
        
        Args:
            certificate_id: The certificate ID
            
        Returns:
            Mock metadata dictionary
        """
        return {
            "name": "Sarah Wilson",
            "course": "Python for Data Science",
            "issue_date": "2023-09-10",
            "instructor": "Jose Portilla",
            "category": "Programming",
            "completion_percentage": 95
        } 

    def validate_certificate(self, url: str, capture_screenshot: bool = False) -> Dict:
        return super().validate_certificate(url, capture_screenshot) 