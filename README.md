# ReleaseNotesAI — AI-Powered Automated Release Notes Generation

ReleaseNotesAI is an AI-powered application that generates structured, human-readable release notes from GitHub commit history. It combines a FastAPI backend, the GitHub REST API, Google's Gemini API, and a React frontend to simplify release documentation.

## Team Members

| University ID | Name |
|---|---|
| 2420030746 | T. Manideep |
| 2420030524 | Rudraksh Rayaprol |
| 2420030701 | P. Roshan |
| 2420030695 | S. Uttej |

**Project Guide:** Mr. Rajkumar Patil

## Abstract

Software development teams make frequent code changes and maintain commit histories using version control systems such as Git. Preparing release notes manually from these commits can be time-consuming and may lead to incomplete or inconsistent documentation.

ReleaseNotesAI retrieves recent commits from a GitHub repository, extracts relevant commit metadata, categorizes changes, and uses an AI model to generate structured release notes. The output organizes changes into features, bug fixes, enhancements, and maintenance updates, helping developers and stakeholders understand what changed in a release.

The project applies software engineering and DevOps practices through automated testing, version control, and continuous integration. Its goal is to reduce manual documentation effort and improve the consistency and readability of release notes.

## Key Features

- **GitHub integration:** Retrieve recent commit history from a public or accessible GitHub repository.
- **Commit categorization:** Classify commits into features, bug fixes, enhancements, and maintenance.
- **AI-generated release notes:** Generate structured release notes using Google's Gemini API.
- **Changed-file metadata:** Retrieve available file-change metadata to provide additional context for generation.
- **Interactive dashboard:** Enter a repository URL and view generated release notes in a React interface.
- **Copy and download:** Copy generated notes or download them as a Markdown file.
- **REST API:** Expose backend functionality through FastAPI endpoints.
- **Automated quality checks:** Run backend tests, frontend linting, and a frontend production build through GitHub Actions.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | React, Vite, JavaScript, CSS |
| Version control data | GitHub REST API |
| AI generation | Google Gemini API |
| Backend testing | pytest, FastAPI TestClient |
| Frontend linting | Oxlint |
| CI/CD | GitHub Actions |

## System Workflow

1. The user enters a GitHub repository URL in the frontend.
2. The frontend sends a request to the FastAPI backend.
3. The backend validates the repository URL and retrieves recent commits through the GitHub API.
4. Commit messages are categorized, and available changed-file metadata is collected.
5. The backend sends the relevant information to Gemini to generate structured release notes.
6. The generated result is validated and returned to the frontend.
7. The user reviews, copies, or downloads the release notes.

## Project Structure

```text
KLH-CSE-2026-2420030746-ReleaseNotesAI/
├── .github/
│   └── workflows/
│       └── backend-tests.yml
├── src/
│   └── backend/
│       ├── main.py
│       ├── requirements.txt
│       └── tests/
│           └── test_main.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

Generated files, virtual environments, and installed frontend dependencies are excluded from version control where appropriate.

## Prerequisites

Install the following before running the application:

- Python 3.13
- Node.js 22 or a compatible version
- npm
- Git
- A GitHub personal access token with the permissions needed to read the repositories you want to analyze
- A Google Gemini API key

API keys must be kept private and must never be committed to GitHub.

## Configuration

### Backend environment variables

Create a `.env` file inside `src/backend/`:

```env
GITHUB_TOKEN=your_github_token
GEMINI_API_KEY=your_gemini_api_key
```

Replace the example values with your own credentials. Do not share or commit this file.

## Running the Backend

From the project root, open a terminal and run:

```powershell
cd src/backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

On Windows, the commands above use the virtual environment's Python executable directly, avoiding the need to activate the environment.

The backend runs at:

- API root: http://localhost:8000/
- Interactive API documentation: http://localhost:8000/docs

## Running the Frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm ci
npm run dev
```

Vite displays the local development URL in the terminal, typically:

http://localhost:5173/

Keep the backend running while using the frontend. The frontend currently calls the backend at `http://127.0.0.1:8000`.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check whether the backend is running |
| GET | `/api/commits?repo_url=...` | Retrieve and categorize repository commits |
| GET | `/api/release-notes?repo_url=...` | Generate structured release notes |

For request parameters and response details, start the backend and open `/docs`.

## Testing and Quality Checks

### Backend tests

From `src/backend/`, run:

```powershell
.\venv\Scripts\python.exe -m pytest tests -v
```

The current backend test suite contains 11 tests covering repository URL parsing, commit categorization, release-note validation, and API behavior.

### Frontend lint

From `frontend/`, run:

```powershell
npm run lint
```

### Frontend production build

From `frontend/`, run:

```powershell
npm run build
```

The GitHub Actions workflow runs backend tests and frontend lint/build checks on pushes to `main` and pull requests targeting `main`.

## Security Notes

- Keep `.env` files out of version control.
- Never hardcode API keys or access tokens in source code.
- Do not commit virtual environments or `node_modules/`.
- Use only the repository permissions required for your work.

## Current Implementation Status

The backend API, GitHub commit retrieval, rule-based commit categorization, Gemini-powered release-note generation, React dashboard, backend unit tests, and GitHub Actions quality checks have been implemented and tested.

Further improvements can include stronger integration testing, additional release-version handling, deployment configuration, and expanded documentation.

## Repository

GitHub: https://github.com/Manideep30746/KLH-CSE-2026-2420030746-ReleaseNotesAI
