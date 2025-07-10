#!/usr/bin/env python3
"""
Certificate Validation System
Automated verification of job applicants' credentials from trusted platforms.
"""

import json
import logging
import os
import re
import sys
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urlparse

from cert_validator.validators.base_validator import BaseValidator
from cert_validator.validators.coursera_validator import CourseraValidator
from cert_validator.validators.credly_validator import CredlyValidator
from cert_validator.validators.udemy_validator import UdemyValidator


class CertificateValidator:
    """Main certificate validation orchestrator."""
    
    def __init__(self):
        """Initialize the certificate validator with platform-specific validators."""
        self.validators: Dict[str, BaseValidator] = {
            'coursera.org': CourseraValidator(),
            'www.coursera.org': CourseraValidator(),
            'credly.com': CredlyValidator(),
            'www.credly.com': CredlyValidator(),
            'udemy.com': UdemyValidator(),
            'www.udemy.com': UdemyValidator(),
        }
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging for the validation system."""
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'validation.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _validate_url_format(self, url: str) -> bool:
        """Validate URL format and security."""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme == 'https' and
                parsed.netloc in self.validators and
                len(url) < 2048  # Reasonable URL length limit
            )
        except Exception as e:
            self.logger.error(f"URL validation error: {e}")
            return False
    
    def _get_validator(self, url: str) -> Optional[BaseValidator]:
        """Get the appropriate validator for the given URL."""
        try:
            domain = urlparse(url).netloc
            return self.validators.get(domain)
        except Exception as e:
            self.logger.error(f"Error getting validator: {e}")
            return None
    
    def validate_certificate(self, url: str, capture_screenshot: bool = False) -> Dict:
        """
        Validate a certificate URL and return detailed results.
        
        Args:
            url: The certificate URL to validate
            capture_screenshot: Whether to capture a screenshot of the certificate page
            
        Returns:
            Dictionary containing validation results
        """
        self.logger.info(f"Starting validation for URL: {url}")
        
        # Initialize response structure
        response = {
            "status": "Error",
            "data": {},
            "confidence": 0,
            "screenshot": None,
            "error_message": None
        }
        
        try:
            # Step 1: Validate URL format
            if not self._validate_url_format(url):
                response["status"] = "Invalid"
                response["error_message"] = "Invalid URL format or untrusted domain"
                self.logger.warning(f"Invalid URL format: {url}")
                return response
            
            # Step 2: Get appropriate validator
            validator = self._get_validator(url)
            if not validator:
                response["status"] = "Invalid"
                response["error_message"] = "Unsupported platform"
                self.logger.warning(f"Unsupported platform for URL: {url}")
                return response
            
            # Step 3: Validate URL pattern
            if not validator.validate_url_pattern(url):
                response["status"] = "Invalid"
                response["error_message"] = "Invalid URL pattern for platform"
                self.logger.warning(f"Invalid URL pattern: {url}")
                return response
            
            # Step 4: Extract metadata and validate certificate
            validation_result = validator.validate_certificate(url, capture_screenshot)
            
            # Step 5: Update response with validation results
            response.update(validation_result)
            
            self.logger.info(f"Validation completed for {url}: {response['status']}")
            
        except Exception as e:
            response["status"] = "Error"
            response["error_message"] = str(e)
            self.logger.error(f"Validation error for {url}: {e}")
        
        return response


def main():
    """CLI interface for certificate validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Certificate Validation System')
    parser.add_argument('url', help='Certificate URL to validate')
    parser.add_argument('--screenshot', action='store_true', 
                       help='Capture screenshot of certificate page')
    parser.add_argument('--output', help='Output file for JSON results')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = CertificateValidator()
    
    # Validate certificate
    result = validator.validate_certificate(args.url, args.screenshot)
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main() 