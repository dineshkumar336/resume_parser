"""
Job Scraper Module
Fetches live job listings from the JSearch API (via RapidAPI).
Includes file-based persistent caching and a CSV fallback for resilience.
"""
import os
import time
import json
import hashlib
import requests
import re

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed yet, will use os.environ directly

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
JSEARCH_API_KEY     = os.environ.get("JSEARCH_API_KEY", "")
JOB_SEARCH_LOCATION = os.environ.get("JOB_SEARCH_LOCATION", "India")
CACHE_TTL           = int(os.environ.get("JOB_CACHE_TTL", "3600"))  # 1 hour default

JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"
JSEARCH_HEADERS = {
    "X-RapidAPI-Key": JSEARCH_API_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

# Skills database path (reuse existing one)
SKILLS_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "skills_database.json"
)

# ─────────────────────────────────────────────
# File-Based Persistent Cache
# ─────────────────────────────────────────────
CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "cache"
)
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_filename(category: str, location: str) -> str:
    """Generate a safe filename from category + location."""
    raw = f"{category.strip().lower()}_{location.strip().lower()}"
    safe = hashlib.md5(raw.encode()).hexdigest()[:12]
    label = raw.replace(" ", "_").replace("/", "_")[:30]
    return os.path.join(CACHE_DIR, f"{label}_{safe}.json")


def _get_cached(category: str, location: str):
    """Return cached jobs from disk if still fresh, else None."""
    path = _cache_filename(category, location)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)
        age = time.time() - entry.get("timestamp", 0)
        if age < CACHE_TTL:
            remaining = int(CACHE_TTL - age)
            print(f"   [Cache HIT] '{category}' — {remaining}s remaining (from disk)")
            return entry["jobs"]
        else:
            print(f"   [Cache STALE] '{category}' — expired, will re-fetch")
            os.remove(path)
    except Exception as e:
        print(f"   [Cache READ ERROR] {e}")
    return None


def _set_cache(category: str, location: str, jobs: list):
    """Write jobs to a JSON file on disk."""
    path = _cache_filename(category, location)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"timestamp": time.time(), "jobs": jobs}, f, ensure_ascii=False, indent=2)
        size_kb = os.path.getsize(path) / 1024
        print(f"   [Cache WRITE] '{category}' → {os.path.basename(path)} ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"   [Cache WRITE ERROR] {e}")




# ─────────────────────────────────────────────
# Skills Extractor (reuses skills_database.json)
# ─────────────────────────────────────────────
_skills_db_cache = None

def _load_skills_db():
    global _skills_db_cache
    if _skills_db_cache is None:
        try:
            with open(SKILLS_DB_PATH, "r", encoding="utf-8") as f:
                _skills_db_cache = json.load(f)
        except Exception:
            _skills_db_cache = {}
    return _skills_db_cache


def extract_skills_from_description(description: str) -> list:
    """Extract known skills from a job description using word-boundary regex matching."""
    if not description:
        return []
    skills_db = _load_skills_db()
    
    # Pad description with spaces to help boundary matching at edges
    text = " " + description.lower().replace("\n", " ").replace("\r", " ") + " "
    
    found = []
    
    # Fast filtering out special characters
    for category_skills in skills_db.values():
        for skill in category_skills:
            skill_lower = skill.lower()
            if skill_lower in found:
                continue
                
            # For skills with special characters (like C++, C#), word boundary \b fails.
            # Handle them explicitly:
            if not skill_lower.isalnum() and " " not in skill_lower:
                if f" {skill_lower} " in text or f" {skill_lower}," in text or f" {skill_lower}." in text or f"/{skill_lower}/" in text or f"({skill_lower})" in text:
                    found.append(skill_lower)
            else:
                # Regular alphanumeric word boundary handling.
                # Escape the skill to be safe (e.g., if it has dots like node.js)
                escaped_skill = re.escape(skill_lower)
                pattern = r'\b' + escaped_skill + r'\b'
                if re.search(pattern, text):
                    found.append(skill_lower)
                    
    return found


# ─────────────────────────────────────────────
# JSearch API Fetcher
# ─────────────────────────────────────────────
def fetch_live_jobs(career_category: str, location: str = None, num_results: int = 15) -> list:
    """
    Fetch live job listings from JSearch API.
    Returns a list of standardized job dicts (same schema as CSV rows).
    """
    if not JSEARCH_API_KEY or JSEARCH_API_KEY == "your_rapidapi_key_here":
        raise ValueError("JSEARCH_API_KEY not configured in .env file.")

    location = location or JOB_SEARCH_LOCATION

    # Check cache first
    cached = _get_cached(career_category, location)
    if cached is not None:
        return cached

    print(f"   [JSearch] Fetching live '{career_category}' jobs in '{location}'...")

    params = {
        "query": f"{career_category} jobs",
        "location": location,
        "num_pages": "1",
        "page": "1",
        "date_posted": "month",
        "employment_types": "FULLTIME,PARTTIME,CONTRACTOR,INTERN"
    }

    try:
        response = requests.get(
            JSEARCH_URL,
            headers=JSEARCH_HEADERS,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        raise ConnectionError("JSearch API timed out. Falling back to local dataset.")
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(f"JSearch API error {e.response.status_code}: {e.response.text[:200]}")
    except Exception as e:
        raise ConnectionError(f"JSearch API request failed: {str(e)}")

    raw_jobs = data.get("data", [])
    if not raw_jobs:
        raise ValueError(f"JSearch returned 0 results for '{career_category}' in '{location}'.")

    print(f"   [JSearch] Got {len(raw_jobs)} raw listings. Processing...")

    jobs = []
    for i, raw in enumerate(raw_jobs[:num_results]):
        description = raw.get("job_description", "") or ""
        required_skills = extract_skills_from_description(description)

        # Standardize into the same schema our existing recommender expects
        job = {
            "id":               i + 1,
            "job_title":        raw.get("job_title", "Unknown Role"),
            "company":          raw.get("employer_name", "Unknown Company"),
            "location":         (raw.get("job_city") or raw.get("job_country") or location),
            "category":         career_category,
            "experience_level": _parse_experience_level(raw),
            "salary_range":     _parse_salary(raw),
            "description":      description[:800],   # cap length for SBERT performance
            "required_skills":  ", ".join(required_skills) if required_skills else career_category,
            "source":           "live",
            # Extra live-only fields surfaced in UI
            "job_apply_link":   raw.get("job_apply_link", ""),
            "employer_logo":    raw.get("employer_logo", ""),
            "job_posted_at":    raw.get("job_posted_at_datetime_utc", ""),
        }
        jobs.append(job)

    _set_cache(career_category, location, jobs)
    print(f"   [JSearch] Processed {len(jobs)} standardized job listings.")
    return jobs


# ─────────────────────────────────────────────
# Helper Parsers
# ─────────────────────────────────────────────
def _parse_experience_level(raw: dict) -> str:
    level = raw.get("job_required_experience", {})
    if isinstance(level, dict):
        yr = level.get("required_experience_in_months", 0) or 0
        if yr < 12:   return "Entry Level"
        if yr < 36:   return "Junior"
        if yr < 60:   return "Mid Level"
        return "Senior"
    return "Not Specified"


def _parse_salary(raw: dict) -> str:
    lo = raw.get("job_min_salary")
    hi = raw.get("job_max_salary")
    curr = raw.get("job_salary_currency", "USD")
    period = raw.get("job_salary_period", "YEAR")
    if lo and hi:
        return f"{curr} {int(lo):,}–{int(hi):,} / {period.lower()}"
    if lo:
        return f"{curr} {int(lo):,}+ / {period.lower()}"
    return "Not Disclosed"


# ─────────────────────────────────────────────
# Public Entry Point (with CSV Fallback)
# ─────────────────────────────────────────────
def get_jobs_with_fallback(career_category: str) -> tuple:
    """
    Try fetching live jobs from JSearch. If that fails for any reason,
    fall back to the local CSV and filter by category-like terms.

    Returns:
        (list_of_job_dicts, is_live: bool)
    """
    try:
        jobs = fetch_live_jobs(career_category)
        if jobs:
            return jobs, True
    except Exception as e:
        print(f"   [JSearch FALLBACK] {e}")

    # ── Fallback: local CSV ──
    print("   [JSearch FALLBACK] Using local jobs_dataset.csv")
    try:
        import pandas as pd
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "jobs_dataset.csv"
        )
        df = pd.read_csv(csv_path)
        # Filter loosely by category keyword
        mask = df["category"].str.contains(career_category.split()[0], case=False, na=False)
        filtered = df[mask]
        if filtered.empty:
            filtered = df  # return everything if no match
        jobs = []
        for _, row in filtered.iterrows():
            jobs.append({
                "id":               int(row.get("id", 0)),
                "job_title":        str(row.get("job_title", "")),
                "company":          str(row.get("company", "")),
                "location":         str(row.get("location", "")),
                "category":         str(row.get("category", "")),
                "experience_level": str(row.get("experience_level", "")),
                "salary_range":     str(row.get("salary_range", "")),
                "description":      str(row.get("description", "")),
                "required_skills":  str(row.get("required_skills", "")),
                "source":           "fallback",
                "job_apply_link":   "",
                "employer_logo":    "",
                "job_posted_at":    "",
            })
        return jobs, False
    except Exception as e2:
        print(f"   [FALLBACK FAILED] {e2}")
        return [], False
