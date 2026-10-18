
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("overview");

  async function generateReleaseNotes(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);
    setActiveTab("overview");

    try {
      const url = new URL(`${API_URL}/api/release-notes`);
      url.searchParams.set("repo_url", repoUrl.trim());

      const response = await fetch(url);

      const data = await response.json();

      if (!response.ok) {
        const detail = data.detail;

        throw new Error(
          typeof detail === "string"
            ? detail
            : detail?.message ||
                detail?.error ||
                "Unable to generate release notes."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Cannot connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  function formatReleaseNotes() {
    if (!result) return "";

    const notes = result.release_notes;

    const sections = [
      `# Release Notes — ${notes.version}`,
      "",
      "## Overview",
      notes.overview,
      "",
      "## Features",
      ...notes.features.map((item) => `- ${item}`),
      "",
      "## Bug Fixes",
      ...notes.bug_fixes.map((item) => `- ${item}`),
      "",
      "## Enhancements",
      ...notes.enhancements.map((item) => `- ${item}`),
      "",
      "## Maintenance",
      ...notes.maintenance.map((item) => `- ${item}`),
      "",
      "## Summary",
      notes.summary,
    ];

    return sections.join("\n");
  }

  async function copyReleaseNotes() {
    try {
      await navigator.clipboard.writeText(formatReleaseNotes());
      alert("Release notes copied successfully.");
    } catch {
      setError("Unable to copy. Check your browser clipboard permissions.");
    }
  }

  function downloadReleaseNotes() {
    const blob = new Blob([formatReleaseNotes()], {
      type: "text/markdown;charset=utf-8",
    });

    const downloadUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = downloadUrl;
    link.download = `${result.repository.replace("/", "-")}-release-notes.md`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(downloadUrl);
  }

  const notes = result?.release_notes;

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "features", label: "Features" },
    { id: "bug_fixes", label: "Bug fixes" },
    { id: "enhancements", label: "Enhancements" },
    { id: "maintenance", label: "Maintenance" },
  ];

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="ReleaseNotesAI home">
          <span className="brand-mark">R</span>
          <span>
            <strong>ReleaseNotesAI</strong>
            <small>Automated release documentation</small>
          </span>
        </a>

        <div className="header-status">
          <span className="status-dot" />
          AI-powered release notes
        </div>
      </header>

      <main className="main-content">
        <section className="hero">
          <span className="eyebrow">DEVELOPER TOOLKIT</span>
          <h1>Turn commits into clear release notes.</h1>
          <p>
            Analyze a GitHub repository and transform commit history
            into structured, professional release documentation.
          </p>
        </section>

        <section className="generator-card">
          <div className="section-heading">
            <div>
              <h2>Generate release notes</h2>
              <p>Enter a public GitHub repository URL.</p>
            </div>
            <span className="step-label">01 / GENERATE</span>
          </div>

          <form onSubmit={generateReleaseNotes}>
            <label htmlFor="repoUrl">GitHub repository URL</label>

            <div className="input-row">
              <span className="input-prefix">GH</span>
              <input
                id="repoUrl"
                type="url"
                placeholder="https://github.com/owner/repository"
                value={repoUrl}
                onChange={(event) => setRepoUrl(event.target.value)}
                required
              />

              <button
                type="submit"
                className="primary-button"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner" />
                    Analyzing...
                  </>
                ) : (
                  "Generate notes"
                )}
              </button>
            </div>

            <p className="form-hint">
              The backend analyzes the latest 20 commits using GitHub API
              and Gemini AI.
            </p>
          </form>
        </section>

        {loading && (
          <section className="message-card" aria-live="polite">
            <span className="spinner large-spinner" />
            <div>
              <h3>Analyzing your repository</h3>
              <p>Fetching commits and generating structured release notes.</p>
            </div>
          </section>
        )}

        {error && (
          <section className="error-card" role="alert">
            <strong>Unable to complete the request</strong>
            <p>{error}</p>
          </section>
        )}

        {result && notes && (
          <section className="results-section">
            <div className="results-heading">
              <div>
                <span className="eyebrow">02 / RESULTS</span>
                <h2>Release documentation</h2>
                <p className="repository-name">
                  <span className="repository-icon">GH</span>
                  {result.repository}
                </p>
              </div>

              <div className="action-buttons">
                <button
                  className="secondary-button"
                  onClick={copyReleaseNotes}
                  type="button"
                >
                  Copy notes
                </button>
                <button
                  className="primary-button"
                  onClick={downloadReleaseNotes}
                  type="button"
                >
                  Download .md
                </button>
              </div>
            </div>

            <div className="stats-grid">
              <div className="stat-card">
                <span>Commits analyzed</span>
                <strong>{result.commits_analyzed}</strong>
              </div>
              <div className="stat-card">
                <span>Release version</span>
                <strong>{notes.version}</strong>
              </div>
              <div className="stat-card">
                <span>AI model</span>
                <strong className="model-name">{result.model}</strong>
              </div>
            </div>

            <div className="release-card">
              <div className="release-card-heading">
                <div>
                  <span className="eyebrow">RELEASE SUMMARY</span>
                  <h3>Release Notes</h3>
                </div>
                <span className="version-badge">{notes.version}</span>
              </div>

              <div className="tabs" role="tablist" aria-label="Release note sections">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    role="tab"
                    aria-selected={activeTab === tab.id}
                    className={activeTab === tab.id ? "tab active" : "tab"}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="tab-content" role="tabpanel">
                {activeTab === "overview" && (
                  <>
                    <h4>Overview</h4>
                    <p className="overview-text">{notes.overview}</p>
                    <div className="summary-box">
                      <h4>Summary</h4>
                      <p>{notes.summary}</p>
                    </div>
                  </>
                )}

                {activeTab !== "overview" && (
                  <>
                    <h4>
                      {tabs.find((tab) => tab.id === activeTab)?.label}
                    </h4>

                    {notes[activeTab].length > 0 ? (
                      <ul className="change-list">
                        {notes[activeTab].map((item, index) => (
                          <li key={`${activeTab}-${index}`}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="empty-state">
                        No changes were identified in this category.
                      </p>
                    )}
                  </>
                )}
              </div>

              <div className="release-footer">
                Generated from {result.commits_analyzed} GitHub commits
                <span>Model: {result.model}</span>
              </div>
            </div>
          </section>
        )}

        {!result && !loading && !error && (
          <section className="empty-preview">
            <div className="preview-icon">
              <span>RN</span>
            </div>
            <h3>Your release notes will appear here</h3>
            <p>
              Enter a repository URL above to generate your first release
              summary.
            </p>
          </section>
        )}
      </main>

      <footer className="site-footer">
        <span>ReleaseNotesAI</span>
        <span>AI-powered changelog generation</span>
      </footer>
    </div>
  );
}

export default App;
