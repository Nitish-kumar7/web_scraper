# Certificate & Portfolio Validator API

## Overview

This project is a comprehensive Python-based API and CLI tool for:
- **Validating online certificates** (Coursera, Udemy, Credly, EdX, LinkedIn)
- **Extracting portfolio data** from personal websites
- **Scraping GitHub and Instagram profiles**
- **Parsing uploaded DOCX resumes** to extract and validate relevant links and information

It uses FastAPI for the web API, Selenium and BeautifulSoup for web scraping, and supports both synchronous and asynchronous operations.

---

## Features

- **Certificate Validation**: Checks the validity of certificates from major platforms, extracts metadata, and can capture screenshots.
- **Portfolio Scraper**: Extracts name, about, skills, projects, education, contact, and experience from portfolio websites (including JS-rendered sites).
- **GitHub Profile Extraction**: Fetches user info, repositories, and contributions using the GitHub API.
- **Instagram Profile Extraction**: Scrapes public Instagram profile stats.
- **DOCX Resume Parsing**: Upload a DOCX file to extract links, validate certificates, and enrich with scraped data.
- **API Key Authentication**: Secures endpoints with a configurable API key.
- **CLI Support**: Validate a certificate URL directly from the command line.

---

## Setup & Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <your-repo-directory>
```

### 2. Install Dependencies

Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install required packages:
```bash
pip install -r requirements.txt
```

**Main dependencies:**
- fastapi
- uvicorn
- selenium
- webdriver-manager
- beautifulsoup4
- requests
- python-docx
- pdfplumber
- aiohttp
- python-dotenv
- pydantic

### 3. Environment Variables

Create a `.env` file if you want to override defaults. Example:
```
API_KEY=qFvFLN4VeYm3XqxnY0s8p-6isd5FCSF8o5aeuxhyOuw
```

---

## Running the API Server

Start the FastAPI server (default: http://127.0.0.1:8000):
```bash
uvicorn "complete file:app" --host 127.0.0.1 --port 8000 --reload
```

---

## API Usage

### Authentication
All endpoints require an API key via the `access_token` header:
```
access_token: qFvFLN4VeYm3XqxnY0s8p-6isd5FCSF8o5aeuxhyOuw
```

### Endpoints

#### 1. Health Check
```
GET /
```
Response: `{ "message": "Hello World" }`

#### 2. Upload Resume (DOCX) and Extract Data
```
POST /upload/
```
**Form Data:**
- `file`: DOCX file
- `access_token`: API key (header)

**Response:**
- Extracted elements (GitHub, portfolio, Instagram, certificates, etc.)
- Scraped portfolio data
- GitHub and Instagram profile info
- Certificate validation results and summary

#### Example (using curl):
```bash
curl -X POST "http://127.0.0.1:8000/upload/" \
  -H "access_token: qFvFLN4VeYm3XqxnY0s8p-6isd5FCSF8o5aeuxhyOuw" \
  -F "file=@your_resume.docx"
```

---

## CLI Usage

You can also validate a certificate URL directly from the command line:

```bash
python "complete file.py" <certificate_url> [--screenshot] [--output result.json]
```

- `--screenshot`: Capture a screenshot of the certificate page (requires Chrome/Selenium)
- `--output`: Save the result as JSON

---

## Project Structure

- `complete file.py` : Main codebase (API, CLI, validators, scrapers)
- `requirements.txt` : Python dependencies
- `README.md` : This file

---

## Notes & Requirements

- **Selenium/ChromeDriver**: For scraping JS-heavy sites and screenshots, Chrome and ChromeDriver must be installed. `webdriver-manager` will auto-download the driver.
- **API Rate Limits**: GitHub and Instagram scraping may be rate-limited.
- **Supported Certificate Platforms**: Coursera, Udemy, Credly, EdX, LinkedIn Learning.
- **Supported Portfolio Sites**: Any public portfolio (best results with standard HTML structure).

---

## License

MIT License (or specify your license here)

---

## Contact

For questions or support, open an issue or contact the maintainer. 