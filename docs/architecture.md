\# ReleaseNotesAI — System Architecture



\## 1. Overview



ReleaseNotesAI is an AI-powered application that generates structured release notes from GitHub commit history. It combines a React frontend, a Python FastAPI backend, the GitHub REST API, and Google's Gemini API.



The application retrieves recent repository commits, categorizes changes, and uses an AI model to produce human-readable release notes.



\## 2. Technology Stack



| Component | Technology | Purpose |

|---|---|---|

| Frontend | React.js | User interface for submitting repository URLs and viewing release notes |

| Frontend tooling | Vite | Development server and production build |

| Backend | Python, FastAPI | API endpoints and application logic |

| Version control integration | GitHub REST API | Retrieves commit information and changed-file metadata |

| AI integration | Google Gemini API | Generates structured release notes |

| Backend testing | pytest, FastAPI TestClient | Tests application functions and API behavior |

| Continuous integration | GitHub Actions | Runs automated backend tests and frontend quality checks |



\## 3. High-Level Architecture



```text

+---------------------------+

|       User / Developer    |

+-------------+-------------+

&#x20;             |

&#x20;             v

+---------------------------+

|      React Frontend       |

| Repository URL Input      |

| Release Notes Dashboard   |

| Copy and Download Options |

+-------------+-------------+

&#x20;             |

&#x20;             | HTTP Request

&#x20;             v

+---------------------------+

|       FastAPI Backend     |

| URL Validation            |

| Commit Retrieval          |

| Change Categorization     |

| Release Notes Generation  |

| Response Validation       |

+------+--------------------+

&#x20;      |

&#x20;      +--------------------+

&#x20;      |                    |

&#x20;      v                    v

+----------------+  +------------------+

| GitHub REST API|  | Google Gemini API|

| Commits        |  | AI-generated     |

| File Metadata  |  | Release Notes    |

+----------------+  +------------------+



&#x20;             CI Pipeline

&#x20;                 |

&#x20;                 v

&#x20;       +---------------------+

&#x20;       |    GitHub Actions   |

&#x20;       | Backend Tests       |

&#x20;       | Frontend Lint/Build |

&#x20;       +---------------------+

```



\## 4. Frontend Architecture



The frontend is implemented using React.js and Vite.



The user enters a GitHub repository URL through the dashboard. The frontend sends a request to the FastAPI backend and displays the generated release notes after receiving a successful response.



The interface organizes release notes into sections such as:



\- Overview

\- Features

\- Bug Fixes

\- Enhancements

\- Maintenance



The interface also supports copying the generated notes and downloading them as a Markdown file.



\## 5. Backend Architecture



The backend is implemented in Python using FastAPI. Its main application file is `src/backend/main.py`.



The backend is responsible for:



1\. Accepting repository URLs from the frontend.

2\. Validating the supplied GitHub repository URL.

3\. Retrieving recent commits through the GitHub REST API.

4\. Extracting available commit information, including messages, authors, dates, and SHA identifiers.

5\. Retrieving changed-file metadata where available.

6\. Categorizing commits into change types.

7\. Sending relevant change information to the Gemini model.

8\. Validating the generated release-note structure.

9\. Returning the result to the frontend.



The application exposes a home endpoint, a commit retrieval endpoint, and a release-note generation endpoint.



\## 6. External API Integration



\### GitHub REST API



The GitHub REST API provides repository commit information. The current implementation retrieves up to 20 recent commits and requests associated changed-file metadata.



A GitHub access token can be configured locally to support authenticated API requests. The token must be stored in an environment file and must never be committed to the repository.



\### Google Gemini API



The Gemini API is used to generate release notes from the collected commit information and file metadata.



The application uses a configured Gemini model and validates the generated response before returning it. If AI generation fails, the application should report or handle the error according to its implemented fallback logic.



AI-generated descriptions should be reviewed by a developer before being treated as definitive documentation.



\## 7. API Endpoints



| Method | Endpoint | Purpose |

|---|---|---|

| GET | `/` | Checks the backend home endpoint |

| GET | `/api/commits` | Retrieves repository commit information |

| GET | `/api/release-notes` | Generates structured release notes |



The commit and release-note endpoints accept a repository URL through the `repo\_url` query parameter.



Interactive API documentation is available through FastAPI Swagger UI at `/docs` while the backend is running locally.



\## 8. Continuous Integration



GitHub Actions automates project verification when changes are pushed to the configured branch or submitted through a pull request targeting that branch.



The workflow installs the required Python dependencies and executes the backend tests. The project workflow also includes frontend linting and production-build checks.



These checks help identify code issues before changes are accepted into the main branch.



\## 9. Testing



The backend test suite covers:



\- Valid GitHub repository URL parsing

\- GitHub URL validation failures

\- Commit categorization

\- Release-note schema validation

\- Missing required release-note fields

\- Home endpoint behavior

\- Invalid repository request handling



The frontend is checked using the configured lint command and production build command.



\## 10. Security Considerations



\- Store GitHub and Gemini credentials in a local `.env` file.

\- Exclude `.env` and virtual-environment directories from version control.

\- Never include real API keys in source code, screenshots, documentation, or commits.

\- Keep dependencies and credentials appropriately managed.

\- Review generated release notes before publishing them.



\## 11. Current Limitations



\- The application currently focuses on recent commit history rather than a complete comparison between two releases.

\- Commit categorization uses predefined rules and may not always identify the intended change type correctly.

\- AI-generated summaries may require human review.

\- GitHub API requests and AI generation depend on network availability, API limits, and valid credentials.

\- Changed-file metadata does not necessarily provide the full source-code diff for a commit.



\## 12. Future Enhancements



Potential improvements include:



\- Comparing two Git tags or release versions

\- Supporting private repositories with secure authorization

\- Adding user-configurable release-note templates

\- Improving commit categorization

\- Adding version-selection and export options

\- Introducing broader integration tests

\- Deploying the application to a hosting platform



\## 13. Conclusion



ReleaseNotesAI combines repository data retrieval, rule-based categorization, AI-generated summaries, a React user interface, automated tests, and continuous integration. Its architecture separates the user interface, backend processing, external services, and quality checks to support future improvements and maintainability.

