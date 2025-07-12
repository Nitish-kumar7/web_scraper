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

---

## Sample DOCX Content

You can use a simple DOCX file like this for testing:

```
Contact Information:
GitHub: https://github.com/Nitish-kumar7
Portfolio: https://portfolio-website-abdullah-jamess.vercel.app/
Instagram: @nitish5300
Udemy: https://www.udemy.com/certificate/UC-ACJJXULH/
Credly:  https://www.credly.com/badges/a90a689b-0e9b-480d-81a0-a12f717d3de2
Coursera: https://www.coursera.org/account/accomplishments/verify/4V4JWRK3UYZM
```

Just copy this text into a DOCX file and upload it in the app to see how extraction and validation works.

