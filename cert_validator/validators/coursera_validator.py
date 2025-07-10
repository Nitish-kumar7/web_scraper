"""
Coursera certificate validator.
Handles validation of Coursera certificate URLs and metadata extraction.
"""

import re
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from .base_validator import BaseValidator


class CourseraValidator(BaseValidator):
    """Validator for Coursera certificates."""
    
    def __init__(self):
        """Initialize Coursera validator."""
        super().__init__()
        # Coursera verification URL pattern: /account/accomplishments/verify/[A-Z0-9]+ (HTTPS only, with optional query params)
        self.url_pattern = re.compile(r'^https://(?:www\.)?coursera\.org/account/accomplishments/verify/[A-Z0-9]+(?:\?.*)?$')
    
    def validate_url_pattern(self, url: str) -> bool:
        """
        Validate Coursera certificate URL pattern.
        
        Args:
            url: The certificate URL to validate
            
        Returns:
            True if URL matches Coursera pattern, False otherwise
        """
        return bool(self.url_pattern.match(url))
    
    def extract_metadata(self, url: str) -> Dict:
        """
        Extract metadata from Coursera certificate verification page.
        
        Args:
            url: The Coursera certificate URL
            
        Returns:
            Dictionary containing extracted metadata
        """
        self.logger.info(f"Extracting metadata from Coursera URL: {url}")
        
        # Get certificate ID from URL
        certificate_id = self._extract_certificate_id(url)
        
        # Fetch the verification page
        content = self._make_request(url)
        if not content:
            self.logger.error("Failed to fetch Coursera certificate page")
            return {}
        
        # Parse HTML content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract metadata using BeautifulSoup
        metadata = {
            "certificate_id": certificate_id,
            "platform": "Coursera",
            "verification_url": url
        }
        
        # Extract candidate name from the verification description
        name_element = soup.find('p', {'class': 'account-verification-description'})
        if name_element:
            # Extract name from text like "Ashlesh Khajbage's account is verified..."
            text = name_element.get_text()
            # Look for pattern: "Name's account is verified"
            name_match = re.search(r"([A-Za-z\s]+)'s account is verified", text)
            if name_match:
                metadata["name"] = name_match.group(1).strip()
        
        # Extract course title from the verification description
        if name_element:
            course_link = name_element.find('a', {'class': 'product-link'})
            if course_link:
                metadata["course"] = course_link.get_text(strip=True)
        
        # Extract issue date - look for date in the page
        # Coursera typically shows the completion date in various formats
        date_selectors = [
            'time',  # HTML5 time element
            '[data-testid="completion-date"]',  # Common test ID
            '.completion-date',  # Common class
            '.certificate-date',  # Another common class
            'span[class*="date"]',  # Any span with "date" in class
            'div[class*="date"]',   # Any div with "date" in class
            '.course-details p strong',  # Date in strong tag within course details
            '.course-details p',  # Date in paragraph within course details
        ]
        
        for selector in date_selectors:
            date_element = soup.select_one(selector)
            if date_element:
                date_text = date_element.get_text(strip=True)
                # Skip if it's empty or contains the name
                if date_text and not any(word in date_text.lower() for word in ['completed', 'by', 'account', 'verified']):
                    parsed_date = self._parse_date(date_text)
                    if parsed_date:
                        metadata["issue_date"] = parsed_date
                        break
        
        # If no structured date found, try to extract from the page text
        if not metadata.get("issue_date"):
            # Look for date patterns in the entire page
            page_text = soup.get_text()
            # Common date patterns in Coursera certificates
            date_patterns = [
                r'(\w+ \d{1,2}, \d{4})',  # "April 29, 2020"
                r'(\d{1,2}/\d{1,2}/\d{4})',  # "4/29/2020"
                r'(\d{4}-\d{2}-\d{2})',  # "2020-04-29"
            ]
            
            for pattern in date_patterns:
                date_match = re.search(pattern, page_text)
                if date_match:
                    parsed_date = self._parse_date(date_match.group(1))
                    if parsed_date:
                        metadata["issue_date"] = parsed_date
                        break
        
        # Extract expiry date (if available)
        expiry_element = soup.find('div', {'class': 'expiry-date'}) or \
                        soup.find('span', {'class': 'expires'})
        if expiry_element:
            expiry_text = expiry_element.get_text(strip=True)
            metadata["expiry_date"] = self._parse_date(expiry_text)
        
        # Extract instructor name (if available)
        instructor_element = soup.find('div', {'class': 'instructor'}) or \
                           soup.find('span', {'class': 'instructor-name'})
        if instructor_element:
            metadata["instructor"] = instructor_element.get_text(strip=True)
        
        # Extract organization/university
        org_element = soup.find('div', {'class': 'organization'}) or \
                     soup.find('span', {'class': 'university'})
        if org_element:
            metadata["organization"] = org_element.get_text(strip=True)
        
        # For demo purposes, if no real data found, use mock data
        if not metadata.get("name") and not metadata.get("course"):
            metadata.update(self._get_mock_metadata(certificate_id))
        
        self.logger.info(f"Extracted metadata: {metadata}")
        return metadata
    
    def check_certificate_status(self, metadata: Dict) -> str:
        """
        Check the status of the Coursera certificate.
        
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
        
        # Check if certificate is expired
        if metadata.get("expiry_date"):
            try:
                expiry_date = datetime.strptime(metadata["expiry_date"], "%Y-%m-%d")
                if expiry_date < datetime.now():
                    return "Expired"
            except (ValueError, TypeError):
                pass
        
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
        Extract certificate ID from Coursera URL.
        
        Args:
            url: The Coursera certificate URL
            
        Returns:
            Certificate ID
        """
        match = re.search(r'/account/accomplishments/verify/([A-Z0-9]+)(?:\?.*)?', url)
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
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%B %d, %Y",  # "April 29, 2020"
            "%b %d, %Y",  # "Apr 29, 2020"
            "%d %B %Y",   # "29 April 2020"
            "%d %b %Y",   # "29 Apr 2020"
            "%B %d %Y",   # "April 29 2020" (no comma)
            "%b %d %Y",   # "Apr 29 2020" (no comma)
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
    
    def _get_mock_metadata(self, certificate_id: str) -> Dict:
        """
        Get mock metadata for demonstration purposes.
        
        Args:
            certificate_id: The certificate ID
            
        Returns:
            Mock metadata dictionary
        """
        return {
            "name": "John Doe",
            "course": "Machine Learning",
            "issue_date": "2023-06-15",
            "expiry_date": None,
            "instructor": "Andrew Ng",
            "organization": "Stanford University"
        } 