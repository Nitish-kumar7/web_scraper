# Smart Web Scraper

A modern web app to extract and validate portfolio, certificate, and social data from DOCX files or pasted text. Supports GitHub, Instagram, LinkedIn, Coursera, Udemy, Credly, EdX, and more.

---

## 1. Install Dependencies

```bash
# Backend (Python)
pip install -r requirements.txt

# Frontend (React)
cd frontend
npm install
```

---

## 2. Environment Variables

Copy the example file and fill in your keys:

```bash
cp .env.example .env
# Edit .env and add your API keys
```

- `API_KEY`: Any string you want (used for backend authentication)
- `APIFY_API_KEY`: Required for LinkedIn scraping ([Get from Apify](https://console.apify.com/account/integrations))
- `GITHUB_API_TOKEN`: Optional, for higher GitHub API rate limits ([Get from GitHub](https://github.com/settings/tokens))

---

## 3. Run the Backend

```bash
uvicorn complete_file:app --reload
```

---

## 4. Run the Frontend

```bash
cd frontend
npm start
```

---

## 5. Usage

- Open the frontend in your browser (usually at http://localhost:3000)
- Upload a DOCX file or paste text
- The app will extract and validate data from supported platforms

---

## Notes

- LinkedIn scraping requires a free [Apify](https://apify.com) account and API key
- GitHub API token is optional but recommended for heavy use
- No screenshots are created or stored

---

For advanced configuration, troubleshooting, or contributing, see the full documentation or open an issue. 