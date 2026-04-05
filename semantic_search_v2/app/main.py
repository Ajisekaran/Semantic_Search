

from flask import Flask, Response

from app.core.config import settings
from app.core.security import apply_all_headers
from app.api.v1.endpoints.search import search_bp
from app.api.v1.endpoints.auth import auth_bp
from app.api.v1.endpoints.system import system_bp
from app.services.search_service import search_service


def create_app() -> Flask:
    """
    Application factory — creates and configures the Flask app.

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False  

  
    app.register_blueprint(search_bp, url_prefix="/api/v1")
    app.register_blueprint(system_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp,   url_prefix="/api/v1")

 
    @app.after_request
    def after_request(response):
        return apply_all_headers(response)

    
    @app.route("/", methods=["GET"])
    def ui():
        """Serve the built-in search UI at the root URL."""
        return Response(_build_ui_html(), mimetype="text/html")

    
    @app.errorhandler(404)
    def not_found(e):
        from flask import jsonify
        return jsonify({
            "success": False,
            "message": f"Route not found. Available: /api/v1/search, /api/v1/health, /api/v1/index",
            "results": [],
        }), 404

    
    @app.errorhandler(405)
    def method_not_allowed(e):
        from flask import jsonify
        return jsonify({
            "success": False,
            "message": "Method not allowed. This API only supports GET requests.",
            "results": [],
        }), 405

    return app


def _build_ui_html() -> str:
    """
    Returns the full HTML for the search UI.
    Kept separate to keep create_app() clean and readable.
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Semantic Document Search Engine</title>
  <style>
    /* ── Reset & Base ─────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px 60px;
    }

    /* ── Header ───────────────────────────────────── */
    .header {
      text-align: center;
      margin-bottom: 36px;
    }
    .header h1 {
      color: #ffffff;
      font-size: 2.2rem;
      font-weight: 800;
      letter-spacing: -0.5px;
      text-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .header p {
      color: rgba(255,255,255,0.85);
      margin-top: 8px;
      font-size: 0.95rem;
    }
    .badge {
      display: inline-block;
      background: rgba(255,255,255,0.2);
      color: #fff;
      padding: 3px 12px;
      border-radius: 20px;
      font-size: 0.78rem;
      margin-top: 8px;
      border: 1px solid rgba(255,255,255,0.3);
    }

    /* ── Search Box ───────────────────────────────── */
    .search-container {
      width: 100%;
      max-width: 720px;
    }
    .search-box {
      display: flex;
      gap: 10px;
      background: white;
      border-radius: 16px;
      padding: 8px 8px 8px 20px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.18);
    }
    .search-box input {
      flex: 1;
      border: none;
      outline: none;
      font-size: 1.05rem;
      color: #2d3748;
      background: transparent;
    }
    .search-box input::placeholder { color: #a0aec0; }
    .search-box button {
      padding: 12px 24px;
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
      border: none;
      border-radius: 10px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.2s, transform 0.1s;
      white-space: nowrap;
    }
    .search-box button:hover  { opacity: 0.9; }
    .search-box button:active { transform: scale(0.97); }

    /* ── Quick-search chips ───────────────────────── */
    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }
    .chip {
      background: rgba(255,255,255,0.18);
      color: #fff;
      border: 1px solid rgba(255,255,255,0.35);
      border-radius: 20px;
      padding: 5px 14px;
      font-size: 0.82rem;
      cursor: pointer;
      transition: background 0.2s;
    }
    .chip:hover { background: rgba(255,255,255,0.3); }

    /* ── Results Area ─────────────────────────────── */
    .results-area {
      width: 100%;
      max-width: 720px;
      margin-top: 28px;
    }

    /* Status bar */
    .status-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      color: rgba(255,255,255,0.9);
      font-size: 0.88rem;
      margin-bottom: 16px;
      min-height: 22px;
    }
    .spinner {
      width: 16px; height: 16px;
      border: 2px solid rgba(255,255,255,0.4);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.7s linear infinite;
      display: none;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── Result Card ──────────────────────────────── */
    .card {
      background: #ffffff;
      border-radius: 14px;
      padding: 22px 26px;
      margin-bottom: 14px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.10);
      border-left: 5px solid #667eea;
      animation: slideIn 0.25s ease forwards;
      opacity: 0;
    }
    @keyframes slideIn {
      from { opacity: 0; transform: translateY(12px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .card:nth-child(1) { animation-delay: 0.05s; border-left-color: #667eea; }
    .card:nth-child(2) { animation-delay: 0.12s; border-left-color: #764ba2; }
    .card:nth-child(3) { animation-delay: 0.19s; border-left-color: #f093fb; }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 10px;
    }
    .card-left  { display: flex; align-items: center; gap: 10px; }
    .rank-badge {
      background: #667eea;
      color: #fff;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 2px 9px;
      border-radius: 20px;
    }
    .card:nth-child(2) .rank-badge { background: #764ba2; }
    .card:nth-child(3) .rank-badge { background: #f093fb; }
    .doc-name {
      font-weight: 700;
      color: #2d3748;
      font-size: 1rem;
    }
    .score-badge {
      background: #f0fff4;
      color: #276749;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.82rem;
      font-weight: 600;
      border: 1px solid #c6f6d5;
    }
    .snippet {
      color: #4a5568;
      font-size: 0.9rem;
      line-height: 1.7;
    }
    .snippet mark {
      background: #fefcbf;
      border-radius: 3px;
      padding: 0 2px;
    }

    /* ── No Results Box ───────────────────────────── */
    .no-results {
      background: white;
      border-radius: 14px;
      padding: 40px;
      text-align: center;
      box-shadow: 0 4px 20px rgba(0,0,0,0.10);
    }
    .no-results .icon { font-size: 3rem; margin-bottom: 12px; }
    .no-results h3 { color: #2d3748; margin-bottom: 8px; font-size: 1.15rem; }
    .no-results p  { color: #718096; font-size: 0.9rem; line-height: 1.6; }
    .suggestions   { margin-top: 16px; }
    .suggestions span {
      display: inline-block;
      background: #ebf8ff;
      color: #2b6cb0;
      border-radius: 8px;
      padding: 4px 12px;
      margin: 4px;
      font-size: 0.83rem;
      cursor: pointer;
    }
    .suggestions span:hover { background: #bee3f8; }

    /* ── API Docs Box ─────────────────────────────── */
    .api-docs {
      width: 100%;
      max-width: 720px;
      margin-top: 30px;
      background: rgba(255,255,255,0.1);
      border-radius: 14px;
      padding: 20px 26px;
      color: rgba(255,255,255,0.9);
    }
    .api-docs h4 { font-size: 0.9rem; margin-bottom: 12px; letter-spacing: 0.5px; }
    .api-route {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 6px 0;
      font-size: 0.83rem;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .api-route:last-child { border-bottom: none; }
    .method {
      background: rgba(255,255,255,0.2);
      padding: 2px 8px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.75rem;
      min-width: 38px;
      text-align: center;
    }
    .route-path { font-family: monospace; color: #c3ddfd; }
    .route-desc { color: rgba(255,255,255,0.7); font-size: 0.8rem; }
  </style>
</head>
<body>

  <!-- Header -->
  <div class="header">
    <h1>&#128269; Semantic Document Search</h1>
    <p>Custom TF-IDF &amp; Cosine Similarity &mdash; built from scratch</p>
    <span class="badge">&#10003; No sklearn &nbsp;&#10003; No gensim &nbsp;&#10003; No HuggingFace</span>
  </div>

  <!-- Search -->
  <div class="search-container">
    <div class="search-box">
      <input id="query" type="text"
             placeholder="e.g. artificial intelligence in finance..."/>
      <button onclick="doSearch()">&#128269; Search</button>
    </div>

    <!-- Quick search chips -->
    <div class="chips">
      <span class="chip" onclick="quickSearch('machine learning neural networks')">&#129302; Machine Learning</span>
      <span class="chip" onclick="quickSearch('artificial intelligence finance')">&#128176; AI in Finance</span>
      <span class="chip" onclick="quickSearch('climate change renewable energy')">&#127807; Climate & Energy</span>
      <span class="chip" onclick="quickSearch('database SQL optimization')">&#128196; Databases</span>
      <span class="chip" onclick="quickSearch('cybersecurity data privacy')">&#128274; Cybersecurity</span>
      <span class="chip" onclick="quickSearch('blockchain cryptocurrency')">&#128279; Blockchain</span>
    </div>
  </div>

  <!-- Results -->
  <div class="results-area">
    <div class="status-bar">
      <div class="spinner" id="spinner"></div>
      <span id="status-text"></span>
    </div>
    <div id="results"></div>
  </div>

  <!-- API Docs -->
  <div class="api-docs">
    <h4>&#9881;&#65039; API ENDPOINTS</h4>
    <div class="api-route">
      <span class="method">GET</span>
      <span class="route-path">/api/v1/search?q=your+query&amp;top_n=3</span>
      <span class="route-desc">Search documents</span>
    </div>
    <div class="api-route">
      <span class="method">GET</span>
      <span class="route-path">/api/v1/index</span>
      <span class="route-desc">Rebuild TF-IDF index</span>
    </div>
    <div class="api-route">
      <span class="method">GET</span>
      <span class="route-path">/api/v1/health</span>
      <span class="route-desc">Server health &amp; index stats</span>
    </div>
    <div class="api-route">
      <span class="method">GET</span>
      <span class="route-path">/api/v1/auth/status</span>
      <span class="route-desc">Auth status</span>
    </div>
  </div>

<script>
  /* ── Helpers ─────────────────────────────────────── */
  const $ = id => document.getElementById(id);

  function setStatus(msg, loading=false) {
    $('status-text').textContent = msg;
    $('spinner').style.display = loading ? 'block' : 'none';
  }

  function quickSearch(q) {
    $('query').value = q;
    doSearch();
  }

  /* ── Highlight query words in snippet ────────────── */
  function highlight(text, query) {
    const words = query.trim().toLowerCase().split(/\\s+/)
      .filter(w => w.length > 2);
    let result = text;
    words.forEach(word => {
      const re = new RegExp('(' + word + ')', 'gi');
      result = result.replace(re, '<mark>$1</mark>');
    });
    return result;
  }

  /* ── Enter key support ───────────────────────────── */
  $('query').addEventListener('keydown', e => {
    if (e.key === 'Enter') doSearch();
  });

  /* ── Main search function ────────────────────────── */
  async function doSearch() {
    const q = $('query').value.trim();
    if (!q) {
      setStatus('Please enter a search query.');
      return;
    }

    setStatus('Searching...', true);
    $('results').innerHTML = '';

    try {
      const res  = await fetch('/api/v1/search?q=' + encodeURIComponent(q));
      const data = await res.json();

      /* ── No results / unknown word ─────────────── */
      if (!data.results || data.results.length === 0) {
        setStatus('');
        $('results').innerHTML = `
          <div class="no-results">
            <div class="icon">&#128269;&#10060;</div>
            <h3>No matching documents found</h3>
            <p>${data.message || 'No documents matched your query.'}<br/>
               Try using different or broader keywords.</p>
            <div class="suggestions">
              <strong style="color:#718096;font-size:.85rem">Try instead:</strong><br/>
              <span onclick="quickSearch('machine learning')">machine learning</span>
              <span onclick="quickSearch('artificial intelligence')">artificial intelligence</span>
              <span onclick="quickSearch('data science')">data science</span>
              <span onclick="quickSearch('neural networks')">neural networks</span>
            </div>
          </div>`;
        return;
      }

      /* ── Show results ──────────────────────────── */
      const count = data.results.length;
      const total = data.total_documents_searched;
      setStatus(
        `Found ${count} result${count>1?'s':''} from ${total} documents for "${q}"`
      );

      $('results').innerHTML = data.results.map(r => `
        <div class="card">
          <div class="card-header">
            <div class="card-left">
              <span class="rank-badge">#${r.rank}</span>
              <span class="doc-name">&#128196; ${r.document}</span>
            </div>
            <span class="score-badge">&#9733; Score: ${r.score.toFixed(4)}</span>
          </div>
          <div class="snippet">${highlight(r.snippet, q)}...</div>
        </div>
      `).join('');

    } catch (err) {
      setStatus('Error: ' + err.message);
      $('results').innerHTML = `
        <div class="no-results">
          <div class="icon">&#9888;&#65039;</div>
          <h3>Connection Error</h3>
          <p>Could not reach the server. Make sure it is running on port 5000.</p>
        </div>`;
    }
  }

  /* ── Load health stats on page load ─────────────── */
  window.addEventListener('load', async () => {
    try {
      const r = await fetch('/api/v1/health');
      const d = await r.json();
      if (d.stats) {
        setStatus(
          `Index ready: ${d.stats.documents_indexed} documents, ` +
          `${d.stats.unique_terms.toLocaleString()} unique terms`
        );
      }
    } catch { /* server might be starting */ }
  });
</script>
</body>
</html>"""



def init_index():
    """Build the search index. Called once at startup."""
    try:
        search_service.build_index()
    except Exception as e:
        print(f"[WARNING] Could not build index at startup: {e}")
        print("[WARNING] Call GET /api/v1/index to build it manually.")
