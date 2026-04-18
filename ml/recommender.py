"""
Resume Recommender Module
Advanced ML Engine:
1. Career Predictive Category classification (Naive Bayes)
2. Hybrid Semantic Job Matching (Sentence-BERT + TF-IDF Cosine Similarity)
3. Resume scoring & recommendations
"""
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from ml.job_scraper import get_jobs_with_fallback
from ml.domain_detector import detect_career_domain

# Global Sentence Transformer Model cache for lazy loading
_sent_model = None

def get_sentence_model():
    """Lazy-load the Sentence-BERT model to save memory/time on simple API startup."""
    global _sent_model
    if _sent_model is None:
        print("\n>>> Initializing Advanced ML Semantic Engine (SentenceTransformers)...")
        from sentence_transformers import SentenceTransformer
        _sent_model = SentenceTransformer('all-MiniLM-L6-v2')
        print(">>> Semantic Engine Ready!")
    return _sent_model

# Path to job dataset (kept as fallback)
JOBS_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "jobs_dataset.csv")

def load_jobs_dataset():
    """Load the jobs dataset from CSV (fallback only)."""
    return pd.read_csv(JOBS_CSV_PATH)

def predict_category(resume_text, jobs_df=None):
    """
    Predict the candidate's optimal career categories using the multi-domain
    Naive Bayes model from domain_detector (covers 15+ domains, not just IT).
    Returns top-3 predictions with probability scores for the UI cards.
    """
    try:
        from ml.domain_detector import NB_SEED_DATA, _get_nb_model
        clf, vectorizer = _get_nb_model()

        resume_vec = vectorizer.transform([resume_text])
        probs = clf.predict_proba(resume_vec)[0]
        classes = clf.classes_

        predictions = []
        for i, prob in enumerate(probs):
            if prob > 0.05:  # Only show predictions > 5% confidence
                predictions.append({
                    "category": classes[i],
                    "probability": round(float(prob) * 100, 1)
                })

        predictions.sort(key=lambda x: x["probability"], reverse=True)
        return predictions[:3]
    except Exception as e:
        print(f"Prediction fallback due to error: {e}")
        return []

def calculate_resume_score(parsed_data):
    """Calculate an overall resume quality score (0-100)."""
    score = 0
    details = {}
    
    # --- Section Score (30 pts) ---
    sections = parsed_data.get("sections", {})
    critical_sections = ["education", "experience", "skills", "projects"]
    nice_to_have = ["objective", "certifications", "achievements"]
    
    section_score = 0
    present_critical = sum(1 for s in critical_sections if sections.get(s, False))
    section_score += (present_critical / len(critical_sections)) * 20
    
    present_nice = sum(1 for s in nice_to_have if sections.get(s, False))
    section_score += (present_nice / len(nice_to_have)) * 10
    
    score += section_score
    details["sections"] = round(section_score, 1)
    
    # --- Skills Score (25 pts) ---
    all_skills = parsed_data.get("all_skills", [])
    skill_count = len(all_skills)
    
    if skill_count >= 15: skill_score = 25
    elif skill_count >= 10: skill_score = 20
    elif skill_count >= 5: skill_score = 15
    elif skill_count >= 3: skill_score = 10
    elif skill_count >= 1: skill_score = 5
    else: skill_score = 0
    
    score += skill_score
    details["skills"] = skill_score
    
    # --- Action Verbs (15 pts) ---
    action_verbs = parsed_data.get("action_verbs", [])
    verb_count = len(action_verbs)
    
    if verb_count >= 10: verb_score = 15
    elif verb_count >= 7: verb_score = 12
    elif verb_count >= 4: verb_score = 8
    elif verb_count >= 2: verb_score = 5
    else: verb_score = 2
    
    score += verb_score
    details["action_verbs"] = verb_score
    
    # --- Word Count (15 pts) ---
    word_count = parsed_data.get("word_count", 0)
    
    if 300 <= word_count <= 800: word_score = 15
    elif 200 <= word_count < 300: word_score = 10
    elif 800 < word_count <= 1200: word_score = 12
    elif word_count > 1200: word_score = 8
    else: word_score = 3
    
    score += word_score
    details["word_count"] = word_score
    
    # --- Contact Info (15 pts) ---
    contact = parsed_data.get("contact_info", {})
    contact_score = 0
    if contact.get("email"): contact_score += 5
    if contact.get("phone"): contact_score += 3
    if contact.get("linkedin"): contact_score += 4
    if contact.get("github"): contact_score += 3
    
    score += contact_score
    details["contact_info"] = contact_score
    
    return {
        "total": min(round(score), 100),
        "breakdown": details,
        "max_scores": {
            "sections": 30,
            "skills": 25,
            "action_verbs": 15,
            "word_count": 15,
            "contact_info": 15
        }
    }

def generate_recommendations(parsed_data, top_category="Software Engineering"):
    """Generate professional improvement recommendations tailored to the career domain."""
    recommendations = []
    sections = parsed_data.get("sections", {})
    all_skills = parsed_data.get("all_skills", [])
    action_verbs = parsed_data.get("action_verbs", [])
    contact = parsed_data.get("contact_info", {})
    word_count = parsed_data.get("word_count", 0)
    skills_by_category = parsed_data.get("skills", {})
    
    # IT/Tech-specific flags
    is_tech = top_category in ["Software Engineering", "Data Science", "DevOps", "UI/UX Design"]
    
    # Example Section Checks
    if not sections.get("objective"):
        recommendations.append({"type": "section", "priority": "medium", "title": "Add a Professional Summary", "message": "Include a 2-3 line summary."})
    
    if is_tech and not sections.get("projects"):
        recommendations.append({"type": "section", "priority": "high", "title": "Add a Projects Section", "message": "Projects demonstrate practical skills beyond academics."})
    
    if not sections.get("experience") and not (is_tech and sections.get("projects")):
        recommendations.append({"type": "section", "priority": "high", "title": "Add Work Experience", "message": "Include any internships, clinicals, or relevant jobs."})
    
    if len(all_skills) < 5:
        recommendations.append({"type": "skill", "priority": "high", "title": "Add Professional Skills", "message": "List 8-15 relevant skills to improve ATS scoring."})
    
    if is_tech and "version_control" not in skills_by_category:
        recommendations.append({"type": "skill", "priority": "medium", "title": "Add Git/Version Control", "message": "Mention Git or GitHub as it is universally expected in tech."})
    
    if len(action_verbs) < 4:
        recommendations.append({"type": "content", "priority": "medium", "title": "Use Stronger Action Verbs", "message": "Start bullet points with verbs like Developed or Led."})
    
    # Priority sorting
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
    return recommendations


def match_jobs(resume_text, top_n=10, jobs_list=None):
    """
    Advanced Job Matcher using a Hybrid ML Approach:
    - 40% TF-IDF: Preserves exact keyword and technology stack matching.
    - 60% Sentence-BERT: Dense Semantic Vectors understand contextual similarity.
    Accepts a list of job dicts (live or from CSV).
    """
    if not jobs_list:
        # Fallback: load from CSV
        jobs_df = load_jobs_dataset()
        jobs_list = jobs_df.to_dict(orient='records')

    jobs_df = pd.DataFrame(jobs_list)

    jobs_df["combined_text"] = (
        jobs_df["job_title"].fillna("") + " " +
        jobs_df["description"].fillna("") + " " +
        jobs_df["required_skills"].fillna("") + " " +
        jobs_df["category"].fillna("")
    )

    corpus = [resume_text] + jobs_df["combined_text"].tolist()

    # --- 1. TF-IDF VECTORIZATION (Keyword Math) ---
    tfidf_vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2)
    )
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
    tfidf_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # --- 2. DENSE SEMANTIC EMBEDDINGS (Sentence Transformers) ---
    model = get_sentence_model()
    embeddings = model.encode(corpus, show_progress_bar=False)
    semantic_sims = cosine_similarity([embeddings[0]], embeddings[1:]).flatten()

    # --- 3. HYBRID SCORING ---
    hybrid_scores = (tfidf_sims * 0.4) + (semantic_sims * 0.6)

    top_indices = hybrid_scores.argsort()[::-1][:top_n]

    results = []
    for idx in top_indices:
        job = jobs_df.iloc[idx]
        total_score = float(hybrid_scores[idx])
        sem_score = float(semantic_sims[idx])
        key_score = float(tfidf_sims[idx])

        if total_score < 0.05: continue

        # Skill analysis
        job_skills = set(s.strip().lower() for s in str(job["required_skills"]).split(","))
        resume_lower = resume_text.lower()
        matched_skills = [s for s in job_skills if s in resume_lower]
        missing_skills = [s for s in job_skills if s not in resume_lower]

        results.append({
            "id":               int(job.get("id", idx)),
            "job_title":        str(job["job_title"]),
            "company":          str(job["company"]),
            "location":         str(job["location"]),
            "category":         str(job["category"]),
            "experience_level": str(job["experience_level"]),
            "salary_range":     str(job["salary_range"]),
            "description":      str(job["description"]),
            "match_score":      round(total_score * 100, 1),
            "semantic_score":   round(sem_score * 100, 1),
            "keyword_score":    round(key_score * 100, 1),
            "matched_skills":   matched_skills,
            "missing_skills":   missing_skills,
            # Live-job extras (empty string if from CSV fallback)
            "job_apply_link":   str(job.get("job_apply_link", "")),
            "employer_logo":    str(job.get("employer_logo", "")),
            "job_posted_at":    str(job.get("job_posted_at", "")),
            "source":           str(job.get("source", "fallback")),
        })

    return results

def get_skill_gap_analysis(parsed_data, top_jobs):
    """Analyze skill gaps based on top matched jobs."""
    all_skills = set(s.lower() for s in parsed_data.get("all_skills", []))
    missing_skill_freq = {}
    for job in top_jobs:
        for skill in job.get("missing_skills", []):
            skill = skill.strip()
            if skill and skill not in all_skills:
                missing_skill_freq[skill] = missing_skill_freq.get(skill, 0) + 1
                
    sorted_skills = sorted(missing_skill_freq.items(), key=lambda x: x[1], reverse=True)
    return [
        {"skill": k, "demand_count": v, "message": f"'{k.title()}' appears in {v} of your top matching jobs"}
        for k, v in sorted_skills[:10]
    ]

def print_terminal_report(res):
    print("\n========================================")
    print("RESUME PARSER — RESULTS")
    print("========================================\n")
    
    # Contact
    print("CONTACT")
    contact = res.get("contact_info", {})
    if contact:
        for k, v in contact.items():
            print(f"  {k:<9} : {v}")
    else:
        print("  (none detected)")
    print()
    
    # Education
    print("EDUCATION")
    edu_content = res.get("section_content", {}).get("education")
    if edu_content:
        for line in edu_content.split('\n'):
            print(f"  {line}")
    elif res.get("sections", {}).get("education"):
        print("  (detected)")
    else:
        print("  (none detected)")
    print()
    
    # Experience
    print("EXPERIENCE")
    exp_content = res.get("section_content", {}).get("experience")
    if exp_content:
        for line in exp_content.split('\n'):
            print(f"  {line}")
    elif res.get("sections", {}).get("experience"):
        print("  (detected)")
    else:
        print("  (none detected)")
    print()
    
    # Skills
    print("SKILLS")
    skills = res.get("extracted_skills", {})
    if skills:
        for k, v in skills.items():
            k_str = k if len(k) <= 12 else k[:12]
            print(f"  {k_str:<12}: {', '.join(v)}")
    else:
        print("  (none detected)")
    print()
    
    # Projects
    print("PROJECTS")
    proj_content = res.get("section_content", {}).get("projects")
    if proj_content:
        for line in proj_content.split('\n'):
            print(f"  {line}")
    elif res.get("sections", {}).get("projects"):
        print("  (detected)")
    else:
        print("  (none detected)")
    print()
    
    # ML PREDICTIONS
    preds = res.get("predicted_categories", [])
    print(f"AI CAREER PREDICTIONS ({len(preds)} found)")
    if preds:
        for p in preds:
            print(f"  [NB    ] {p['category']:<20} conf: {p['probability']/100:.3f}")
    else:
        print("  (none)")
    print()
    
    # JOB MATCHES
    top_jobs = res.get("top_jobs", [])
    print(f"HYBRID JOB MATCHES ({len(top_jobs[:5])} displayed)")
    if top_jobs:
        for i, job in enumerate(top_jobs[:5]):
            title = job['job_title']
            if len(title) > 25:
                title = title[:22] + "..."
            print(f"  {i+1}. {title:<25} | Score: {job['match_score']:>4}%  (SBERT: {job['semantic_score']:>4}%, TF-IDF: {job['keyword_score']:>4}%)")
    else:
        print("  (none)")
    print()
    
    # ATS SCORE
    score = res.get("score", {})
    total = score.get("total", 0)
    print(f"ATS SCORE: {total}/100")
    
    def bar(val, max_val, length=20):
        val = int(val)
        max_val = int(max_val)
        if max_val == 0: max_val = 1
        filled = int((val / max_val) * length)
        # Ensure filled doesn't exceed length
        filled = min(filled, length)
        return '█' * filled + '░' * (length - filled)
        
    breakdown = score.get("breakdown", {})
    max_s = score.get("max_scores", {})
    
    print(f"  contact   {bar(breakdown.get('contact_info', 0), max_s.get('contact_info', 15))}  {int(breakdown.get('contact_info', 0))}")
    print(f"  skills    {bar(breakdown.get('skills', 0), max_s.get('skills', 25))}  {int(breakdown.get('skills', 0))}")
    print(f"  sections  {bar(breakdown.get('sections', 0), max_s.get('sections', 30))}  {int(breakdown.get('sections', 0))}")
    print(f"  action_vb {bar(breakdown.get('action_verbs', 0), max_s.get('action_verbs', 15))}  {int(breakdown.get('action_verbs', 0))}")
    print(f"  words     {bar(breakdown.get('word_count', 0), max_s.get('word_count', 15))}  {int(breakdown.get('word_count', 0))}")
    
    print()
    
    # Missing/Recommendations
    recs = res.get("recommendations", [])
    if recs:
        missing_titles = [r['title'] for r in recs]
        print(f"Missing: {', '.join(missing_titles)}")
    else:
        print("Missing: (none! great job)")
    print("\n")


def analyze_resume(parsed_data):
    """
    Main execution pipeline for the advanced NLP analysis.
    Executes scoring, predictive classification, and hybrid job matching.
    Now uses live JSearch API jobs, with CSV fallback.
    """
    print(f"\n[{'-'*10} ANALYZING RESUME {'-'*10}]")
    jobs_df = load_jobs_dataset()   # used only for Naive Bayes training

    # Extract Full Text for Machine Learning Models
    resume_text = parsed_data.get("raw_text", "") + " " + " ".join(parsed_data.get("all_skills", []))

    # TWO-STAGE DOMAIN DETECTION (for job search query)
    # Stage 1: Keyword heuristics → Stage 2: Multi-domain NB fallback
    print("-> Detecting career domain...")
    top_category = detect_career_domain(resume_text)

    # Basic analysis
    score = calculate_resume_score(parsed_data)
    print(f"-> Resume Score Calculated: {score['total']}/100")

    recommendations = generate_recommendations(parsed_data, top_category)
    print(f"-> Generated {len(recommendations)} improvement recommendations.")

    # ADVANCED ML: Predict Job Categories (for UI display cards)
    print("-> Running Naive Bayes Career Prediction...")
    predicted_categories = predict_category(resume_text, jobs_df)
    if predicted_categories:
        print(f"   NB Top Prediction: {predicted_categories[0]['category']} ({predicted_categories[0]['probability']}%)")

    # LIVE JOB FETCHING — uses top predicted category as search query
    print(f"-> Fetching live jobs for category: '{top_category}'...")
    live_jobs, is_live = get_jobs_with_fallback(top_category)
    source_label = "Live (JSearch API)" if is_live else "Fallback (Local CSV)"
    print(f"   Job Source: {source_label} — {len(live_jobs)} listings")

    # ADVANCED ML: Hybrid Job Matching on live jobs
    print("-> Running Hybrid Job Matching (SBERT + TF-IDF)...")
    top_jobs = match_jobs(resume_text, top_n=10, jobs_list=live_jobs)
    print(f"   Found {len(top_jobs)} relevant job matches.")

    # Skill Gaps
    print("-> Analyzing Skill Gaps based on matches...")
    skill_gaps = get_skill_gap_analysis(parsed_data, top_jobs)
    print(f"[{'-'*10} ANALYSIS COMPLETE {'-'*10}]\n")
    
    result = {
        "score":               score,
        "recommendations":     recommendations,
        "top_jobs":            top_jobs,
        "predicted_categories": predicted_categories,
        "skill_gaps":          skill_gaps,
        "extracted_skills":    parsed_data.get("skills", {}),
        "all_skills":          parsed_data.get("all_skills", []),
        "sections":            parsed_data.get("sections", {}),
        "section_content":     parsed_data.get("section_content", {}),
        "action_verbs":        parsed_data.get("action_verbs", []),
        "contact_info":        parsed_data.get("contact_info", {}),
        "word_count":          parsed_data.get("word_count", 0),
        "jobs_source":         "live" if is_live else "fallback",
        "top_category":        top_category,
    }
    
    print_terminal_report(result)
    
    return result
