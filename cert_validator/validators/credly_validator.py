"""
Credly badge validator.
Handles validation of Credly badge URLs and metadata extraction.
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


class CredlyValidator(BaseValidator):
    """Validator for Credly badges."""
    
    def __init__(self):
        """Initialize Credly validator."""
        super().__init__()
        # Credly badge URL patterns:
        # 1. /org/[org]/badge/[badge-name]
        # 2. /badges/[uuid]
        self.url_pattern = re.compile(r'^https://(?:www\.)?credly\.com/(?:org/[^/]+/badge/[^/]+|badges/[a-f0-9-]+)/?$')
        # List of common user agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
    
    def validate_url_pattern(self, url: str) -> bool:
        """
        Validate Credly badge URL pattern.
        
        Args:
            url: The badge URL to validate
            
        Returns:
            True if URL matches Credly pattern, False otherwise
        """
        return bool(self.url_pattern.match(url))
    
    def _setup_webdriver(self) -> Optional[webdriver.Chrome]:
        """
        Set up and configure Chrome WebDriver.
        
        Returns:
            Configured Chrome WebDriver instance or None if setup fails
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
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
            
            # Add additional preferences
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            # Try to initialize WebDriver with automatic driver management
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set page load timeout
            driver.set_page_load_timeout(30)
            
            # Execute CDP commands to prevent detection
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
            
            # Extract badge name
            badge_name = soup.find('h1')
            if badge_name:
                metadata["badge_name"] = badge_name.get_text(strip=True)
                self.logger.info(f"Found badge name: {metadata['badge_name']}")
            
            # Extract organization (issuer)
            org_name = None
            # Try to find any element containing 'Issued by' and extract the following text
            issued_by_elem = soup.find(string=re.compile(r'Issued by', re.I))
            if issued_by_elem:
                # The organization name may be immediately after 'Issued by' in the same string
                match = re.search(r'Issued by\s*(.*)', issued_by_elem, re.I)
                if match and match.group(1).strip():
                    org_name = match.group(1).strip()
                else:
                    # Or it may be in the next sibling or parent
                    parent = issued_by_elem.parent
                    if parent:
                        # Check next sibling
                        next_sib = parent.find_next_sibling()
                        if next_sib and next_sib.get_text(strip=True):
                            org_name = next_sib.get_text(strip=True)
                        else:
                            # Or just use the parent's text after 'Issued by'
                            text = parent.get_text(separator=' ', strip=True)
                            match2 = re.search(r'Issued by\s*(.*)', text, re.I)
                            if match2 and match2.group(1).strip():
                                org_name = match2.group(1).strip()
            if org_name:
                metadata["organization"] = org_name
                self.logger.info(f"Found organization: {metadata['organization']}")
            
            # Extract skills
            skills_section = soup.find('h2', string='Skills')
            if skills_section:
                skills_list = skills_section.find_next('ul')
                if skills_list:
                    skills = [li.get_text(strip=True) for li in skills_list.find_all('li')]
                    metadata["skills"] = skills
                    self.logger.info(f"Found skills: {skills}")
            
            # Extract earning criteria
            criteria_section = soup.find('h2', string='Earning Criteria')
            if criteria_section:
                criteria_list = criteria_section.find_next('ul')
                if criteria_list:
                    criteria = [li.get_text(strip=True) for li in criteria_list.find_all('li')]
                    metadata["earning_criteria"] = criteria
                    self.logger.info(f"Found earning criteria: {criteria}")
            
            # Check if we found the essential information
            if metadata.get("badge_name") and metadata.get("organization"):
                success = True
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {str(e)}")
        
        return metadata, success
    
    def extract_metadata(self, url: str) -> Dict:
        """
        Extract metadata from Credly badge page.
        
        Args:
            url: The Credly badge URL
            
        Returns:
            Dictionary containing extracted metadata
        """
        self.logger.info(f"Extracting metadata from Credly URL: {url}")
        
        # Initialize metadata with basic information
        metadata = {
            "platform": "Credly",
            "verification_url": url
        }
        
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            driver = None
            try:
                self.logger.info(f"Attempt {attempt + 1} of {max_retries}")
                
                # Set up WebDriver
                driver = self._setup_webdriver()
                if not driver:
                    continue
                
                # Navigate to the badge page
                driver.get(url)
                
                # Wait for the page to load
                time.sleep(retry_delay + random.uniform(1, 3))  # Add some randomness
                
                # Log the page title for debugging
                self.logger.info(f"Page title: {driver.title}")
                
                # Try to find the badge content
                try:
                    # First wait for body to be present
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Then wait for the badge name
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h1"))
                    )
                    
                except TimeoutException:
                    self.logger.warning("Timeout waiting for badge content, trying to proceed anyway")
                    # Log the page source for debugging
                    self.logger.debug(f"Page source: {driver.page_source}")
                
                # Get the page source
                content = driver.page_source
                
                # Extract metadata from HTML
                extracted_metadata, success = self._extract_metadata_from_html(content)
                
                if success:
                    metadata.update(extracted_metadata)
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
        
        self.logger.info(f"Extracted metadata: {metadata}")
        return metadata
    
    def check_certificate_status(self, metadata: Dict) -> str:
        """
        Check the status of the Credly badge.
        
        Args:
            metadata: Extracted badge metadata
            
        Returns:
            Badge status: "Valid", "Expired", "Revoked", or "Invalid"
        """
        if not metadata:
            return "Invalid"
        
        # Check if badge has required fields
        required_fields = ["badge_name", "organization"]
        if not all(metadata.get(field) for field in required_fields):
            return "Invalid"
        
        return "Valid" 

    def validate_certificate(self, url: str, capture_screenshot: bool = False) -> Dict:
        return super().validate_certificate(url, capture_screenshot) 