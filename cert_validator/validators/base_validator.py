"""
Base validator class for certificate validation.
Defines the interface that all platform-specific validators must implement.
"""

import abc
import logging
import os
import re
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urlparse


class BaseValidator(abc.ABC):
    """Abstract base class for certificate validators."""
    
    def __init__(self):
        """Initialize the base validator."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abc.abstractmethod
    def validate_url_pattern(self, url: str) -> bool:
        """
        Validate if the URL matches the expected pattern for this platform.
        
        Args:
            url: The certificate URL to validate
            
        Returns:
            True if URL pattern is valid, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def extract_metadata(self, url: str) -> Dict:
        """
        Extract metadata from the certificate page.
        
        Args:
            url: The certificate URL
            
        Returns:
            Dictionary containing extracted metadata
        """
        pass
    
    @abc.abstractmethod
    def check_certificate_status(self, metadata: Dict) -> str:
        """
        Check the status of the certificate based on metadata.
        
        Args:
            metadata: Extracted certificate metadata
            
        Returns:
            Certificate status: "Valid", "Expired", "Revoked", or "Invalid"
        """
        pass
    
    def validate_certificate(self, url: str, capture_screenshot: bool = False) -> Dict:
        """
        Main validation method that orchestrates the validation process.
        
        Args:
            url: The certificate URL to validate
            capture_screenshot: (Unused, for compatibility)
            
        Returns:
            Dictionary containing validation results
        """
        self.logger.info(f"Validating certificate: {url}")
        
        try:
            # Extract metadata
            metadata = self.extract_metadata(url)
            
            if not metadata:
                return {
                    "status": "Invalid",
                    "data": {},
                    "confidence": 0,
                    "error_message": "Failed to extract metadata"
                }
            
            # Check certificate status
            status = self.check_certificate_status(metadata)
            
            # Determine confidence score
            confidence = self._calculate_confidence(metadata, status)
            
            return {
                "status": status,
                "data": metadata,
                "confidence": confidence,
                "error_message": None
            }
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return {
                "status": "Error",
                "data": {},
                "confidence": 0,
                "error_message": str(e)
            }
    
    def _calculate_confidence(self, metadata: Dict, status: str) -> int:
        """
        Calculate confidence score based on metadata quality and status.
        
        Args:
            metadata: Extracted certificate metadata
            status: Certificate status
            
        Returns:
            Confidence score (0-100)
        """
        base_confidence = 80  # Base confidence for scraped data
        
        # Reduce confidence for invalid/error statuses
        if status in ["Invalid", "Error"]:
            return 0
        elif status == "Expired":
            base_confidence -= 20
        elif status == "Revoked":
            base_confidence -= 40
        
        # Adjust based on metadata completeness
        required_fields = ["name", "course", "issue_date"]
        missing_fields = sum(1 for field in required_fields if not metadata.get(field))
        
        if missing_fields == 0:
            base_confidence += 10
        elif missing_fields == 1:
            base_confidence -= 10
        else:
            base_confidence -= 30
        
        return max(0, min(100, base_confidence))
    
    def _make_request(self, url: str, max_retries: int = 3, use_selenium: bool = False) -> Optional[str]:
        """
        Make HTTP request with retry logic, optionally using Selenium.
        
        Args:
            url: URL to request
            max_retries: Maximum number of retry attempts
            use_selenium: Whether to use Selenium for fetching the page content
            
        Returns:
            Response content as string, or None if failed
        """
        import requests
        from time import sleep
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for attempt in range(max_retries):
            try:
                if not use_selenium:
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    return response.text
                else:
                    self.logger.info(f"Attempting to fetch with Selenium (attempt {attempt + 1}): {url}")
                    from selenium import webdriver
                    from selenium.webdriver.chrome.options import Options
                    from selenium.webdriver.common.by import By
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC

                    chrome_options = Options()
                    chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--no-sandbox")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    chrome_options.add_argument("--window-size=1920,1080")

                    driver = webdriver.Chrome(options=chrome_options)
                    try:
                        driver.get(url)
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        return driver.page_source
                    finally:
                        driver.quit()
            except requests.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed (requests): {e}")
                if attempt < max_retries - 1:
                    sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"All requests attempts failed for {url}")
            except Exception as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed (selenium/general): {e}")
                if attempt < max_retries - 1:
                    sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"All attempts failed for {url}")
                    return None
        
        return None 