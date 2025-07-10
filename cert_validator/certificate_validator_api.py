"""
Certificate Validation API Integration
Provides certificate validation functionality for FastAPI applications.
"""

import sys
import os
from typing import Dict, List, Optional
import logging

# Add the cert_validator directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'cert_validator'))

try:
    from validate_certificate import CertificateValidator
except ImportError as e:
    logging.error(f"Failed to import CertificateValidator: {e}")
    CertificateValidator = None

class CertificateValidationError(Exception):
    """Custom exception for certificate validation errors."""
    pass

class CertificateValidatorAPI:
    """API wrapper for certificate validation functionality."""
    
    def __init__(self):
        """Initialize the certificate validator API."""
        if CertificateValidator is None:
            raise CertificateValidationError("CertificateValidator not available")
        
        self.validator = CertificateValidator()
        self.logger = logging.getLogger(__name__)
    
    def validate_certificates(self, certificate_urls: List[str]) -> Dict[str, Dict]:
        """
        Validate multiple certificate URLs.
        
        Args:
            certificate_urls: List of certificate URLs to validate
            
        Returns:
            Dictionary mapping URLs to validation results
        """
        if not certificate_urls:
            return {}
        
        results = {}
        
        for url in certificate_urls:
            try:
                self.logger.info(f"Validating certificate: {url}")
                result = self.validator.validate_certificate(url, capture_screenshot=False)
                results[url] = result
            except Exception as e:
                self.logger.error(f"Error validating certificate {url}: {e}")
                results[url] = {
                    "status": "Error",
                    "data": {},
                    "confidence": 0,
                    "screenshot": None,
                    "error_message": str(e)
                }
        
        return results
    
    def validate_single_certificate(self, url: str) -> Dict:
        """
        Validate a single certificate URL.
        
        Args:
            url: Certificate URL to validate
            
        Returns:
            Validation result dictionary
        """
        try:
            self.logger.info(f"Validating single certificate: {url}")
            return self.validator.validate_certificate(url, capture_screenshot=False)
        except Exception as e:
            self.logger.error(f"Error validating certificate {url}: {e}")
            return {
                "status": "Error",
                "data": {},
                "confidence": 0,
                "screenshot": None,
                "error_message": str(e)
            }

# Global instance for reuse
certificate_validator = None

def get_certificate_validator() -> Optional[CertificateValidatorAPI]:
    """Get or create the certificate validator instance."""
    global certificate_validator
    
    if certificate_validator is None:
        try:
            certificate_validator = CertificateValidatorAPI()
        except Exception as e:
            logging.error(f"Failed to initialize certificate validator: {e}")
            return None
    
    return certificate_validator 