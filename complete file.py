# --- IMPORTS ---
import os
import re
import io
import sys
import time
import json
import zipfile
import shutil
import logging
import platform
import random
import pdfplumber
import docx
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse, urljoin
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Request, BackgroundTasks, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from apify_client import ApifyClient
import asyncio
from bs4 import BeautifulSoup
import aiohttp
from fastapi.security.api_key import APIKeyHeader
from docx import Document
import tempfile
from cert_validator.validate_certificate import CertificateValidator

# --- INLINED CONFIGS ---
PATTERNS = {
  "certificate_patterns": {
    "udemy": r"https?://(www\.)?udemy\.com/certificate/[A-Za-z0-9_-]+/?",
    "credly": r"https?://(www\.)?credly\.com/badges/[A-Za-z0-9_-]+/?",
    "coursera": r"https?://(www\.)?coursera\.org/account/accomplishments/verify/[A-Za-z0-9_-]+/?"
  }
}

REGEX_CONFIG = {
  "extract_elements_patterns": {
    "github": r"github\.com/([A-Za-z0-9_-]+)",
    "portfolio": r"(https?://[\w\.-]+\.(?:vercel\.app|netlify\.app|github\.io|dev|me|xyz|app|site|portfolio|com|in)[^\s]*)",
    "instagram": r"Instagram:\s*@?([A-Za-z0-9_.-]+)",
    "udemy": r"(https?://www\.udemy\.com/certificate/[A-Za-z0-9_-]+)",
    "linkedin": r"(https?://www\.linkedin\.com/(in|learning/certificates)/[A-Za-z0-9_-]+)",
    "credly": r"(https?://www\.credly\.com/badges/[A-Za-z0-9_-]+)",
    "coursera": r"(https?://www\.coursera\.org/account/accomplishments/verify/[A-Za-z0-9_-]+)"
  },
  "date_patterns": [
    r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})",
    r"(\d{2}/\d{2}/\d{4})"
  ],
  "github_username": r"github\.com/([A-Za-z0-9_-]+)",
  "validator_url_patterns": {
    "edx": r"https?://(www\.)?edx\.org/certificates/[A-Za-z0-9_-]+/?",
    "udemy": r"https?://(www\.)?udemy\.com/certificate/[A-Za-z0-9_-]+/?",
    "linkedin": r"https?://(www\.)?linkedin\.com/learning/certificates/[A-Za-z0-9_-]+/?",
    "credly": r"https?://(www\.)?credly\.com/badges/[A-Za-z0-9_-]+/?",
    "coursera": r"https?://(www\.)?coursera\.org/account/accomplishments/verify/[A-Za-z0-9_-]+/?",
    "linkedin": r"^https://(?:www\.)?linkedin\.com/(learning/certificates|in)/[A-Za-z0-9_-]+/?$",
    "credly": r"^https://(?:www\.)?credly\.com/(?:org/[^/]+/badge/[^/]+|badges/[A-Za-z0-9_-]+)/?$",
    "coursera": r"^https://(?:www\.)?coursera\.org/account/accomplishments/verify/[A-Za-z0-9_-]+/?$"
  },
  "extract_certificate_id": {
    "udemy": r"/certificate/(UC-[A-Z0-9]+)",
    "credly": r"/badges/([A-Za-z0-9_-]+)",
    "coursera": r"/account/accomplishments/verify/([A-Z0-9]+)(?:\\?.*)?",
    "linkedin": r"/certificates/([a-z0-9-]+)",
    "edx": r"/certificates/([a-z0-9]+)"
  },
  "percentage_pattern": r"(\d+(?:\.\d+)?)%",
  "decimal_pattern": r"(\d+\.\d+)",
  "integer_pattern": r"(\d+)",
  "followers_pattern": r"([\d,]+) followers",
  "following_pattern": r"([\d,]+) following",
  "posts_pattern": r"([\d,]+) posts",
  "account_verified_pattern": r"([A-Za-z\s]+)'s account is verified",
  "time_pattern": r"(\d+)\s*hours?\s*(\d+)?\s*minutes?",
  "hours_pattern": r"(\d+)\s*hours?",
  "minutes_pattern": r"(\d+)\s*minutes?"
}

SELECTORS_CONFIG = {
  "date_selectors": [
    "time",
    "[data-testid=\"completion-date\"]",
    ".completion-date",
    ".certificate-date",
    "span[class*=\"date\"]",
    "div[class*=\"date\"]",
    ".course-details p strong",
    ".course-details p"
  ],
  "portfolio_fallback_tags": ["p"],
  "portfolio_keywords": ["about", "developer", "engineer", "student", "enthusiast", "portfolio"],
  "portfolio_exclude_keywords": ["copyright", "privacy", "terms", "cookie", "all rights", "responsibilities", "experience", "projects", "skills", "education", "contact"],
  "portfolio_list_exclude_keywords": ["projects", "skills", "experience", "education", "contact", "resume", "certificates", "terms", "conditions", "icon", "hackathons", "internships"],
  "user_agents": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
  ],
  "mock_metadata": {
    "name": "Demo User",
    "course": "Demo Course",
    "issue_date": "2022-01-01"
  },
  "udemy": {
    "title": "div.certificate-title, h1",
    "description": "div.certificate-description, [data-purpose=\"certificate-description\"]",
    "user_name": "div.user-name",
    "issue_date": "div.issue-date, span.issue-date"
  },
  "credly": {
    "badge_name": "h1.badge-title, div.BadgeTitle",
    "issuer": "div.IssuerName",
    "issue_date": "div.IssuedOn-date, div.IssuedOn",
    "skills": "div.SkillsList, ul.skills-list"
  },
  "coursera": {
    "name": "p.account-verification-description",
    "course": "a.product-link",
    "date": "span.completion-date, time, .certificate-date"
  },
  "linkedin": {
    "name": ".profile-topcard-person-entity__name, h1.text-heading-xlarge",
    "certificate": ".certificate-card, .certification-list__item"
  },
  "edx": {
    "name": "h1.certificate-title, h1",
    "date": "span.certificate-date, time"
  },
  "platform_names": {
    "coursera": "Coursera",
    "udemy": "Udemy",
    "credly": "Credly",
    "edx": "EdX",
    "linkedin": "LinkedIn Learning"
  },
  "status_strings": {
    "valid": "Valid",
    "invalid": "Invalid",
    "expired": "Expired",
    "error": "Error"
  },
  "skill_keywords": [
    "full stack", "ai", "web", "typescript", "next.js", "python", "modern ai", "agentic ai", "mentoring", "problem solving",
    "javascript", "react", "node", "machine learning", "deep learning", "data science", "html", "css", "docker", "cloud",
    "api", "database", "sql", "mongodb", "express", "django", "flask", "fastapi", "github", "git", "linux", "devops"
  ],
  "experience_keywords": [
    "student", "leader", "mentoring", "competition", "troubleshoot", "support", "scored", "matriculation",
    "distinction", "foundation", "performance", "contributions"
  ],
  "portfolio_name_selectors": [
    "h1", "header h1", ".name", ".profile-name", ".user-name", ".hero-title", ".profileHeader-name", "title"
],
"portfolio_about_selectors": [
    ".about", "#about", ".bio", ".description", ".profile-about", ".about-me", "section[aria-label='About']"
],
"portfolio_about_max_length": 500,
"portfolio_about_fallback_tags": ["p", "div"],
"portfolio_about_keywords": ["about", "developer", "engineer", "enthusiast", "student", "portfolio"],
"portfolio_skills_selectors": [
    ".skills", "#skills", ".skill-list", ".skills-list", ".tech-stack", ".stack", ".tags", ".chip", ".badge", ".skill", ".technology", ".technologies", ".skills-section", ".skills__list", ".skills__item", ".skills-container", ".skills-content", ".skills-block", ".skillsGroup", ".skills-section__list", ".skills-section__item", "[data-section='skills']", "[data-testid='skills']"
],
"portfolio_project_selectors": [
    ".project", ".projects-list .project", ".project-card", ".portfolio-project", ".work", ".projectItem", ".projects__item", ".projects-section__item", ".project-block", ".project-entry", ".project-list__item", ".project-section__item", "[data-section='projects']", "[data-testid='projects']"
],
"portfolio_project_title_selectors": [
    ".project-title", "h3", "h2", ".title"
],
"portfolio_project_desc_selectors": [
    ".project-description", ".desc", "p", ".description"
],
"portfolio_project_link_selectors": [
    "a", ".project-link", ".external-link"
],
"portfolio_project_fallback_domains": [
    "github.com", "vercel.app", "netlify.app", "replit.com"
],
"portfolio_education_selectors": [
    ".education", "#education", ".edu", ".education-list", ".degree", ".school", ".university", ".college", ".institute", "#resume", ".education-block", ".academic", ".academics", ".education-section", ".education__item", ".education-entry", ".education-list__item", ".education-section__item", "[data-section='education']", "[data-testid='education']"
],
"portfolio_contact_selectors": {
    "email": ["a[href^='mailto:']", ".email", "#email"],
    "linkedin": ["a[href*='linkedin.com']", ".linkedin"],
    "github": ["a[href*='github.com']", ".github"],
    "twitter": ["a[href*='twitter.com']", ".twitter"],
    "website": ["a[href^='http']", ".website", ".site"]
},
"portfolio_skill_flexible_keywords": [
    "skill", "stack", "tech", "tools", "technology", "technologies", "competence", "expertise", "proficiency", "abilities", "capabilities"
],
"portfolio_project_flexible_keywords": [
    "project", "work", "portfolio", "case-study", "case_study", "case study", "side-project", "sideproject", "side project", "creation", "build", "demo"
],
"portfolio_education_flexible_keywords": [
    "education", "degree", "school", "university", "college", "institute", "resume", "academic", "academics", "study", "studies", "formation", "diploma", "certification"
],
"portfolio_education_keywords": [
    "bachelor", "master", "phd", "university", "college", "institute", "school", "degree", "resume", "academic", "studies", "diploma", "certification", "course", "formation"
],
"portfolio_education_exclude_keywords": [
    "work", "project", "application", "email", "copywrite", "copyright", "linkedin", "latest", "side", "freelance", "management", "urban", "commercial", "application", "tools", "skills", "contact", "discover", "value", "team", "view", "certificates", "explore", "chat"
],
"portfolio_education_min_length": 6,
"portfolio_education_max_length": 100,
"portfolio_skill_min_length": 2,
"portfolio_skill_max_length": 40,
"portfolio_split_delimiters": ["\n", ",", "|", "•", "-", "\u2022", ";", ".", " and ", " with ", "  "]
}
# --- END INLINED CONFIGS ---

# --- PROJECT ROOT SETUP ---
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- LOGGING SETUP ---
import logging
log_dir = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'validation.log')),
        logging.StreamHandler()
    ])
logger = logging.getLogger(__name__)

# --- ENVIRONMENT ---
from dotenv import load_dotenv
load_dotenv()

# --- CERTIFICATE VALIDATOR API (from certificate_validator_api.py) ---
class CertificateValidationError(Exception):
    """Custom exception for certificate validation errors."""
    pass

class CertificateValidatorAPI:
    """API wrapper for certificate validation functionality."""
    def __init__(self):
        if CertificateValidator is None:
            raise CertificateValidationError("CertificateValidator not available")
        self.validator = CertificateValidator()
        self.logger = logging.getLogger(__name__)
    def validate_certificates(self, certificate_urls: List[str]) -> Dict[str, Dict]:
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

certificate_validator = None

def get_certificate_validator() -> Optional[CertificateValidatorAPI]:
    global certificate_validator
    if certificate_validator is None:
        try:
            certificate_validator = CertificateValidatorAPI()
        except Exception as e:
            logging.error(f"Failed to initialize certificate validator: {e}")
            return None
    return certificate_validator

def main():
    """CLI interface for certificate validation."""
    import argparse
    parser = argparse.ArgumentParser(description='Certificate Validation System')
    parser.add_argument('url', help='Certificate URL to validate')
    parser.add_argument('--screenshot', action='store_true', help='Capture screenshot of certificate page')
    parser.add_argument('--output', help='Output file for JSON results')
    args = parser.parse_args()
    validator = CertificateValidator()
    result = validator.validate_certificate(args.url, args.screenshot)
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))

# --- PORTFOLIO SCRAPER LOGIC (from portfolio_scraper.py, functions only) ---

def clean_text(text: str) -> Optional[str]:
    if not text:
        return None
    return ' '.join(text.split())

def extract_text_from_tags(soup, selectors: List[str], max_length: int = 500, fallback_tags: List[str] = None, keywords: List[str] = None, exclude_keywords: List[str] = None) -> Optional[str]:
    if exclude_keywords is None:
        exclude_keywords = get_config(SELECTORS_CONFIG, "portfolio_exclude_keywords")
    if fallback_tags is None:
        fallback_tags = get_config(SELECTORS_CONFIG, "portfolio_fallback_tags")
    if keywords is None:
        keywords = get_config(SELECTORS_CONFIG, "portfolio_keywords")
    extracted_texts = []
    for selector in selectors:
        tags = soup.select(selector)
        for tag in tags:
            text = clean_text(tag.get_text())
            if text and len(text) <= max_length and (not keywords or any(kw.lower() in text.lower() for kw in keywords)) and not any(ex_kw.lower() in text.lower() for ex_kw in exclude_keywords):
                extracted_texts.append(text)
    if not extracted_texts and fallback_tags:
        for tag_name in fallback_tags:
            tags = soup.find_all(tag_name)
            for tag in tags:
                text = clean_text(tag.get_text())
                if text and len(text) <= max_length and not any(ex_kw.lower() in text.lower() for ex_kw in exclude_keywords) and (not keywords or any(kw.lower() in text.lower() for kw in keywords)):
                    extracted_texts.append(text)
    return " ".join(list(dict.fromkeys(extracted_texts)))[:max_length] if extracted_texts else None

def extract_single_text(soup, selectors: List[str], max_length: int = 500) -> Optional[str]:
    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            text = clean_text(tag.get_text())
            if text and len(text) <= max_length:
                return text
    return None

def extract_list_from_tags(soup, selectors: List[str], separator: str = ',') -> List[str]:
    items = []
    exclude_keywords = set(get_config(SELECTORS_CONFIG, "portfolio_list_exclude_keywords"))
    for selector in selectors:
        elements = soup.select(selector)
        for elem in elements:
            text = None
            if elem.name == 'img':
                text = clean_text(elem.get('alt'))
            else:
                text = clean_text(elem.get_text() or elem.get('alt') or elem.get('title'))
            if not text or any(ex_kw.lower() in text.lower() for ex_kw in exclude_keywords):
                continue
            if separator in text:
                items.extend([clean_text(item) for item in text.split(separator) if clean_text(item) and not any(ex_kw.lower() in item.lower() for ex_kw in exclude_keywords)])
            elif len(text.split()) <= 5 and text not in items:
                items.append(text)
    return list(dict.fromkeys([item for item in items if item]))

def extract_link_from_tags(soup, selectors: List[str], base_url: str) -> Optional[str]:
    for selector in selectors:
        tag = soup.select_one(selector)
        if tag and tag.get('href'):
            href = tag['href']
            if href.startswith('mailto:'):
                return href.replace('mailto:', '')
            return urljoin(base_url, href)
    return None

def _find_flexible_tags(soup, keywords, tag_names=None):
    """Find tags where class or id contains any of the keywords (config-driven, no regex)."""
    if tag_names is None:
        tag_names = ["div", "section", "ul", "li", "span", "p"]
    found = []
    for tag in soup.find_all(tag_names):
        classes = ' '.join(tag.get('class', []))
        id_ = tag.get('id', '')
        for kw in keywords:
            if kw.lower() in classes.lower() or kw.lower() in id_.lower():
                found.append(tag)
                break
    return found

def _split_and_clean(text, delimiters=None):
    if not text:
        return []
    if delimiters is None:
        delimiters = get_config(SELECTORS_CONFIG, "portfolio_split_delimiters", default=["\n", ",", "|", "•", "-", "\u2022"])
    # Replace all delimiters with newlines, then split
    for delim in delimiters:
        text = text.replace(delim, "\n")
    items = text.split("\n")
    return [i.strip() for i in items if i and len(i.strip()) > 1]

def parse_portfolio(html_content: str, url: str) -> dict:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # --- Name ---
    name_selectors = get_config(SELECTORS_CONFIG, "portfolio_name_selectors")
    name = extract_single_text(soup, name_selectors)
    if not name:
        og_name = soup.find('meta', property='og:site_name') or soup.find('meta', property='og:title')
        if og_name and og_name.get('content'):
            name = og_name['content'].strip()
        else:
            twitter_name = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_name and twitter_name.get('content'):
                name = twitter_name['content'].strip()

    # --- About/Description ---
    about_selectors = get_config(SELECTORS_CONFIG, "portfolio_about_selectors")
    about_max_length = get_config(SELECTORS_CONFIG, "portfolio_about_max_length")
    about_fallback_tags = get_config(SELECTORS_CONFIG, "portfolio_about_fallback_tags")
    about_keywords = get_config(SELECTORS_CONFIG, "portfolio_about_keywords")
    about = extract_text_from_tags(
        soup,
        selectors=about_selectors,
        max_length=about_max_length,
        fallback_tags=about_fallback_tags,
        keywords=about_keywords
    )
    if not about:
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            about = og_desc['content'].strip()
        else:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                about = meta_desc['content'].strip()

    # --- Skills ---
    skills = []
    # 1. Try explicit selectors
    skills_selectors = get_config(SELECTORS_CONFIG, "portfolio_skills_selectors")
    skills = extract_list_from_tags(soup, skills_selectors)
    # 2. Try flexible tag search for skills
    if not skills:
        skill_tags = _find_flexible_tags(soup, get_config(SELECTORS_CONFIG, "portfolio_skill_flexible_keywords"))
        for tag in skill_tags:
            skills += _split_and_clean(tag.get_text(" ", strip=True))
    # 3. Try about section
    if not skills and about:
        skills += _split_and_clean(about)
    # 4. Try project descriptions
    if not skills:
        project_tags = _find_flexible_tags(soup, get_config(SELECTORS_CONFIG, "portfolio_project_flexible_keywords"))
        for tag in project_tags:
            skills += _split_and_clean(tag.get_text(" ", strip=True))
    # 5. Filter by known skill keywords
    skill_keywords = set([kw.lower() for kw in get_config(SELECTORS_CONFIG, "skill_keywords")])
    skills = [s for s in set(skills) if any(kw in s.lower() for kw in skill_keywords)]

    # For skills
    skill_min_length = get_config(SELECTORS_CONFIG, "portfolio_skill_min_length", default=2)
    skill_max_length = get_config(SELECTORS_CONFIG, "portfolio_skill_max_length", default=40)
    skills = [
        s for s in set(skills)
        if skill_min_length <= len(s) <= skill_max_length
    ]

    # --- Projects ---
    projects = []
    # 1. Try explicit selectors
    project_selectors = get_config(SELECTORS_CONFIG, "portfolio_project_selectors")
    project_title_selectors = get_config(SELECTORS_CONFIG, "portfolio_project_title_selectors")
    project_desc_selectors = get_config(SELECTORS_CONFIG, "portfolio_project_desc_selectors")
    project_link_selectors = get_config(SELECTORS_CONFIG, "portfolio_project_link_selectors")
    for selector in project_selectors:
        for div in soup.select(selector):
            title = extract_single_text(div, project_title_selectors)
            desc = extract_single_text(div, project_desc_selectors)
            link = extract_link_from_tags(div, project_link_selectors, url)
            if title or desc or link:
                projects.append({
                    "title": title,
                    "description": desc,
                    "link": link
                })
    # 2. Try flexible tag search for projects
    if not projects:
        project_tags = _find_flexible_tags(soup, get_config(SELECTORS_CONFIG, "portfolio_project_flexible_keywords"))
        for tag in project_tags:
            for a in tag.find_all('a', href=True):
                title = a.text.strip() or a.get('title')
                desc = tag.get_text(" ", strip=True)
                projects.append({
                    "title": title,
                    "description": desc,
                    "link": a['href']
                })
    # 3. Fallback: look for links to known project domains
    if not projects:
        fallback_project_domains = get_config(SELECTORS_CONFIG, "portfolio_project_fallback_domains")
        for a in soup.find_all('a', href=True):
            if any(domain in a['href'] for domain in fallback_project_domains):
                title = a.text.strip() or a.get('title')
                desc = None
                parent = a.find_parent(['div', 'li'])
                if parent:
                    desc = parent.get_text(" ", strip=True)
                projects.append({
                    "title": title,
                    "description": desc,
                    "link": a['href']
                })
    # Deduplicate projects by link
    seen_links = set()
    deduped_projects = []
    for proj in projects:
        link = proj.get("link")
        if link and link not in seen_links:
            deduped_projects.append(proj)
            seen_links.add(link)
    projects = deduped_projects

    # --- Education ---
    education = []
    education_selectors = get_config(SELECTORS_CONFIG, "portfolio_education_selectors")
    education = extract_list_from_tags(soup, education_selectors)

    if not education:
        edu_flex_keywords = get_config(SELECTORS_CONFIG, "portfolio_education_flexible_keywords")
        edu_tags = _find_flexible_tags(soup, edu_flex_keywords)
        for tag in edu_tags:
            education += _split_and_clean(tag.get_text(" ", strip=True))

    if not education and about:
        edu_keywords = get_config(SELECTORS_CONFIG, "portfolio_education_keywords")
        education += [line for line in _split_and_clean(about) if any(kw in line.lower() for kw in edu_keywords)]

    # Filter out unwanted items using config
    edu_exclude = [kw.lower() for kw in get_config(SELECTORS_CONFIG, "portfolio_education_exclude_keywords", default=[])]
    edu_min_length = get_config(SELECTORS_CONFIG, "portfolio_education_min_length", default=6)
    edu_max_length = get_config(SELECTORS_CONFIG, "portfolio_education_max_length", default=100)
    education = [
        e for e in dict.fromkeys([e for e in education if edu_min_length <= len(e) <= edu_max_length])
        if not any(ex_kw in e.lower() for ex_kw in edu_exclude)
    ]

    # --- Contact ---
    contact = {}
    contact_selectors = get_config(SELECTORS_CONFIG, "portfolio_contact_selectors")
    for key, sel in contact_selectors.items():
        val = extract_link_from_tags(soup, sel, url)
        if val:
            contact[key] = val

    # --- Experience ---
    experience = []
    experience_keywords = get_config(SELECTORS_CONFIG, "experience_keywords")
    # From about/education
    for line in [about] + education:
        if line and any(word in line.lower() for word in experience_keywords):
            experience.append(line.strip())
    # From projects
    for proj in projects:
        desc = proj.get("description")
        if desc and len(desc.split()) > 3:
            experience.append(desc.strip())
    # Remove duplicates and short lines
    experience = [e for e in dict.fromkeys(experience) if len(e.split()) > 3]

    return {
        "name": name,
        "about": about,
        "skills": skills,
        "experience": experience,
        "projects": projects,
        "education": education,
        "contact": contact
    }

def fetch_portfolio_with_selenium(url: str) -> dict:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    import os
    debug_file = 'selenium_portfolio_debug.html'
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        # Wait for the page to load (adjust as needed)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(8)  # Give JS more time to render
        html = driver.page_source
        # Save for debugging
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html)
        result = parse_portfolio(html, url)
        # If nothing extracted, return debug info
        if not any([result.get('name'), result.get('about'), result.get('skills'), result.get('projects'), result.get('education'), result.get('contact')]):
            return {"error": "Portfolio extraction returned no data. See debug HTML.", "debug_html": os.path.abspath(debug_file)}
        return result
    except Exception as e:
        if driver:
            try:
                driver.quit()
            except:
                pass
        return {"error": f"Selenium error: {str(e)}", "debug_html": os.path.abspath(debug_file)}
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def fetch_portfolio(url: str) -> dict:
    # Try Selenium first for JS-rendered content
    try:
        result = fetch_portfolio_with_selenium(url)
        # If Selenium worked and didn't just return an error, use it
        if result and not result.get('error'):
            return result
    except Exception:
        pass
    # Fallback to requests + BeautifulSoup
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        portfolio_info = parse_portfolio(response.text, url)
        return portfolio_info
    except Exception as e:
        return {"error": str(e)}

# --- GITHUB EXTRACTOR LOGIC (from github_extractor.py, functions only) ---

class GitHubAPIError(Exception):
    pass

async def fetch_github_profile(username: str) -> dict:
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos"
    events_url = f"https://api.github.com/users/{username}/events/public"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Portfolio-Extractor"
    }

    async with aiohttp.ClientSession() as session:
        # --- Profile Info ---
        async with session.get(user_url, headers=headers) as resp:
            if resp.status != 200:
                return {"error": f"GitHub API returned status {resp.status}"}
            profile = await resp.json()

        # --- Repositories ---
        repos = []
        page = 1
        while True:
            async with session.get(repos_url, headers=headers, params={"page": page, "per_page": 100}) as resp:
                if resp.status != 200:
                    break
                page_repos = await resp.json()
                if not page_repos:
                    break
                for repo in page_repos:
                    repos.append({
                        "name": repo["name"],
                        "description": repo["description"],
                        "language": repo["language"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "open_issues": repo["open_issues_count"],
                        "watchers": repo["watchers_count"],
                        "size": repo["size"],
                        "created_at": repo["created_at"],
                        "updated_at": repo["updated_at"],
                        "pushed_at": repo["pushed_at"],
                        "url": repo["html_url"],
                        "homepage": repo["homepage"],
                        "topics": repo.get("topics", []),
                        "license": repo["license"]["name"] if repo["license"] else None,
                        "default_branch": repo["default_branch"],
                        "is_fork": repo["fork"],
                        "archived": repo["archived"]
                    })
                if len(page_repos) < 100:
                    break
                page += 1

        # --- Contributions (from events) ---
        async with session.get(events_url, headers=headers, params={"per_page": 100}) as resp:
            contributions = {
                "commits": 0,
                "pull_requests": 0,
                "issues": 0,
                "repositories_contributed_to": set()
            }
            if resp.status == 200:
                events = await resp.json()
                for event in events:
                    if event["type"] == "PushEvent":
                        contributions["commits"] += len(event["payload"]["commits"])
                        contributions["repositories_contributed_to"].add(event["repo"]["name"])
                    elif event["type"] == "PullRequestEvent":
                        contributions["pull_requests"] += 1
                        contributions["repositories_contributed_to"].add(event["repo"]["name"])
                    elif event["type"] == "IssuesEvent":
                        contributions["issues"] += 1
                        contributions["repositories_contributed_to"].add(event["repo"]["name"])
            contributions["repositories_contributed_to"] = list(contributions["repositories_contributed_to"])

        # --- Assemble Output ---
        return {
            "username": profile.get("login"),
            "name": profile.get("name"),
            "bio": profile.get("bio"),
            "location": profile.get("location"),
            "company": profile.get("company"),
            "blog": profile.get("blog"),
            "email": profile.get("email"),
            "twitter_username": profile.get("twitter_username"),
            "public_repos": profile.get("public_repos"),
            "public_gists": profile.get("public_gists"),
            "followers": profile.get("followers"),
            "following": profile.get("following"),
            "created_at": profile.get("created_at"),
            "updated_at": profile.get("updated_at"),
            "avatar_url": profile.get("avatar_url"),
            "hireable": profile.get("hireable"),
            "repositories": repos,
            "contributions": contributions
        }

app = FastAPI(
    title="Your API Title",
    description="Your API Description"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# --- API KEY AUTHORIZATION (single source of truth) ---
API_KEY = "qFvFLN4VeYm3XqxnY0s8p-6isd5FCSF8o5aeuxhyOuw"
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

def extract_elements(text):
    patterns = get_config(REGEX_CONFIG, "extract_elements_patterns")
    github = re.search(patterns["github"], text, re.IGNORECASE)
    portfolio = re.search(patterns["portfolio"], text, re.IGNORECASE)
    instagram = re.search(patterns["instagram"], text, re.IGNORECASE)
    udemy = re.search(patterns["udemy"], text, re.IGNORECASE)
    linkedin = re.search(patterns["linkedin"], text, re.IGNORECASE)
    credly = re.search(patterns["credly"], text, re.IGNORECASE)
    coursera = re.search(patterns["coursera"], text, re.IGNORECASE)

    return {
        "github": github.group(0) if github else None,
        "portfolio": portfolio.group(0) if portfolio else None,
        "instagram": instagram.group(1) if instagram else None,
        "udemy": udemy.group(0) if udemy else None,
        "linkedin": linkedin.group(0) if linkedin else None,
        "credly": credly.group(0) if credly else None,
        "coursera": coursera.group(0) if coursera else None,
    }

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    # 1. Save and read the uploaded file
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 2. Extract text from DOCX
    doc = Document(tmp_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    os.remove(tmp_path)

    # 3. Extract elements (github, portfolio, instagram, etc.)
    elements = extract_elements(text)

    # 3a. Scrape Instagram profile if username found
    instagram_profile = None
    if elements.get("instagram"):
        instagram_profile = parse_instagram(elements["instagram"])

    # 3b. Scrape portfolio site if URL found
    portfolio_data = None
    if elements.get("portfolio"):
        portfolio_data = fetch_portfolio(elements["portfolio"])

    # --- Extract skills and experience if missing ---
    if portfolio_data:
        # Extract skills if empty
        if not portfolio_data.get("skills"):
            skills_set = set()
            about = portfolio_data.get("about", "")
            education = " ".join(portfolio_data.get("education", []))
            projects = " ".join([p.get("description", "") or "" for p in portfolio_data.get("projects", [])])
            text_blob = f"{about} {education} {projects}".lower()
            # Common skill keywords
            skill_keywords = get_config(SELECTORS_CONFIG, "skill_keywords")
            for kw in skill_keywords:
                if kw in text_blob:
                    skills_set.add(kw.title())
            portfolio_data["skills"] = sorted(skills_set)
        # Extract experience if empty
        if not portfolio_data.get("experience"):
            experience = []
            about = portfolio_data.get("about", "")
            education = portfolio_data.get("education", [])
            projects = portfolio_data.get("projects", [])
            experience_keywords = get_config(SELECTORS_CONFIG, "experience_keywords")
            # From about/education
            for line in ([about] + education):
                if any(word in line.lower() for word in experience_keywords):
                    experience.append(line.strip())
            # From projects
            for proj in projects:
                desc = proj.get("description")
                if desc and len(desc.split()) > 3:
                    experience.append(desc.strip())
            # Remove duplicates and short lines
            experience = [e for e in dict.fromkeys(experience) if len(e.split()) > 3]
            portfolio_data["experience"] = experience

    # 3c. Scrape GitHub profile if username or URL found
    github_profile = None
    if elements.get("github"):
        github_url = elements["github"]
        github_username = extract_github_username(github_url)
        if github_username:
            github_profile = await fetch_github_profile(github_username)

    # 4. Collect certificate URLs from both elements and text extraction
    certificate_urls = set(extract_certificate_urls(text))
    for key in ["udemy", "credly", "coursera", "edx", "linkedin"]:
        url = elements.get(key)
        if url:
            certificate_urls.add(url)
    # Filter out any non-URLs (e.g., 'www.')
    certificate_urls = {url for url in certificate_urls if isinstance(url, str) and url.startswith("http")}

    # 5. Validate each certificate URL using the orchestrator
    validator = CertificateValidator()
    certificates = {url: validator.validate_certificate(url) for url in certificate_urls}

    # 6. Build summary
    total_certificates = len(certificates)
    valid_certificates = sum(1 for c in certificates.values() if c.get("status") == "Valid")
    invalid_certificates = sum(1 for c in certificates.values() if c.get("status") == "Invalid")
    certificate_summary = {
        "total_certificates": total_certificates,
        "valid_certificates": valid_certificates,
        "invalid_certificates": invalid_certificates,
        "validation_rate": int(100 * valid_certificates / total_certificates) if total_certificates else 0
    }

    # 7. Return your response
    return {
        "elements": elements,
        "instagram_profile": instagram_profile,
        "portfolio_data": portfolio_data,
        "github_profile": github_profile,
        "certificates": certificates,
        "certificate_summary": certificate_summary,
    }

def parse_instagram(username: str) -> dict:
    import requests
    from bs4 import BeautifulSoup
    import re
    from datetime import datetime

    url = f"https://www.instagram.com/{username}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            content = desc["content"]
            # Example: '169 followers, 214 following, 1 posts – See Instagram photos and videos from  (@nitish5300)'
            followers = re.search(r"([\d,]+) followers", content, re.IGNORECASE)
            following = re.search(r"([\d,]+) following", content, re.IGNORECASE)
            posts = re.search(r"([\d,]+) posts", content, re.IGNORECASE)
            return {
                "bio": content,
                "followers": int(followers.group(1).replace(',', '')) if followers else None,
                "following": int(following.group(1).replace(',', '')) if following else None,
                "posts_count": int(posts.group(1).replace(',', '')) if posts else None,
                "username": username,
                "timestamp": str(datetime.now())
            }
        else:
            return {"error": "Could not find profile meta description"}
    except Exception as e:
        return {"error": str(e)}

def parse_coursera(url: str) -> dict:
    import requests
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and "coursera" in resp.text.lower():
            return {"status": "Valid", "platform": "Coursera", "verification_url": url}
        else:
            return {"status": "Invalid", "platform": "Coursera", "verification_url": url}
    except Exception as e:
        return {"status": "Invalid", "platform": "Coursera", "verification_url": url, "error": str(e)}

def parse_credly(url: str) -> dict:
    import requests
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and "badge" in resp.text.lower():
            return {"status": "Valid", "platform": "Credly", "verification_url": url}
        else:
            return {"status": "Invalid", "platform": "Credly", "verification_url": url}
    except Exception as e:
        return {"status": "Invalid", "platform": "Credly", "verification_url": url, "error": str(e)}

def parse_udemy(url: str) -> dict:
    import requests
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and "Certificate" in resp.text:
            return {"status": "Valid", "platform": "Udemy", "verification_url": url}
        else:
            return {"status": "Invalid", "platform": "Udemy", "verification_url": url}
    except Exception as e:
        return {"status": "Invalid", "platform": "Udemy", "verification_url": url, "error": str(e)}

def parse_edx(url: str) -> dict:
    import requests
    from bs4 import BeautifulSoup

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Course title
        course_title = None
        for h1 in soup.find_all("h1"):
            if "certificate" not in h1.text.lower():
                course_title = h1.text.strip()
                break

        # Recipient name
        recipient = None
        for div in soup.find_all("div"):
            if "awarded to" in div.text.lower():
                recipient = div.text.replace("Awarded to", "").strip()
                break

        # Issue date
        issue_date = None
        for div in soup.find_all("div"):
            if "issued" in div.text.lower():
                issue_date = div.text.strip()
                break

        return {
            "course_title": course_title,
            "recipient": recipient,
            "issue_date": issue_date
        }
    except Exception as e:
        return {"error": str(e)}

def extract_github_username(url):
    pattern = get_config(REGEX_CONFIG, "github_username")
    match = re.search(pattern, url)
    return match.group(1) if match else None

def extract_certificate_urls(text):
    urls = []
    for pattern in PATTERNS["certificate_patterns"].values():
        urls += re.findall(pattern, text)
    return urls

def extract_name(soup):
    for selector in get_config(SELECTORS_CONFIG, "name_selectors"):
        tag = soup.select_one(selector)
        if tag and tag.get_text(strip=True):
            return clean_text(tag.get_text())
    # Fallback: largest h1/h2
    candidates = soup.find_all(['h1', 'h2'])
    if candidates:
        return clean_text(max(candidates, key=lambda t: len(t.get_text())).get_text())
    return None

# --- LOAD CONFIGS FOR REGEX AND SELECTORS ---
# CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
# with open(os.path.join(CONFIG_DIR, 'regex_config.json'), 'r', encoding='utf-8') as f:
#     REGEX_CONFIG = json.load(f)
# with open(os.path.join(CONFIG_DIR, 'selectors_config.json'), 'r', encoding='utf-8') as f:
#     SELECTORS_CONFIG = json.load(f)

# Helper to get config value with error handling
def get_config(config, *keys, default=None):
    try:
        for key in keys:
            config = config[key]
        return config
    except (KeyError, TypeError):
        if default is not None:
            return default
        raise KeyError(f"Missing config value for: {'/'.join(keys)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
