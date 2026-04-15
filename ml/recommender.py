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

# Path to job dataset
JOBS_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "jobs_dataset.csv")

def load_jobs_dataset():
    """Load the jobs dataset from CSV."""
    return pd.read_csv(JOBS_CSV_PATH)

def predict_category(resume_text, jobs_df):
    """
    Train a Naive Bayes classifier on the fly to predict the candidate's optimal Job Category.
    """
    try:
        # Prepare training data
        X_train = jobs_df["description"].fillna("") + " " + jobs_df["required_skills"].fillna("")
        y_train = jobs_df["category"].fillna("General")
        
        # Convert text to term frequencies
        vectorizer = CountVectorizer(stop_words='english', max_features=3000)
        X_train_vec = vectorizer.fit_transform(X_train)
        
        # Train generic fast Naive Bayes Model
        clf = MultinomialNB()
        clf.fit(X_train_vec, y_train)
        
        # Predict candidate
        resume_vec = vectorizer.transform([resume_text])
        probs = clf.predict_proba(resume_vec)[0]
        
        # Package and format predictions
        classes = clf.classes_
        predictions = []
        for i, prob in enumerate(probs):
            if prob > 0.05:  # Only threshold probabilities > 5%
                predictions.append({
                    "category": classes[i],
                    "probability": round(float(prob) * 100, 1)
                })
        
        # Sort by best matched category
        predictions.sort(key=lambda x: x["probability"], reverse=True)
        return predictions[:3]  # Return top 3 predictions
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

def generate_recommendations(parsed_data):
    """Generate professional improvement recommendations."""
    recommendations = []
    sections = parsed_data.get("sections", {})
    all_skills = parsed_data.get("all_skills", [])
    action_verbs = parsed_data.get("action_verbs", [])
    contact = parsed_data.get("contact_info", {})
    word_count = parsed_data.get("word_count", 0)
    skills_by_category = parsed_data.get("skills", {})
    
    # Example Section Checks
    if not sections.get("objective"):
        recommendations.append({"type": "section", "priority": "medium", "icon": "📝", "title": "Add a Professional Summary", "message": "Include a 2-3 line summary."})
    if not sections.get("projects"):
        recommendations.append({"type": "section", "priority": "high", "icon": "🚀", "title": "Add a Projects Section", "message": "Projects demonstrate practical skills beyond academics."})
    if not sections.get("experience") and not sections.get("projects"):
        recommendations.append({"type": "section", "priority": "high", "icon": "💼", "title": "Add Work Experience", "message": "Include any internships or relevant part-time jobs."})
    
    if len(all_skills) < 5:
        recommendations.append({"type": "skill", "priority": "high", "icon": "⚡", "title": "Add Technical Skills", "message": "List 8-15 relevant skills to improve ATS scoring."})
    if "version_control" not in skills_by_category:
        recommendations.append({"type": "skill", "priority": "medium", "icon": "🔧", "title": "Add Git/Version Control", "message": "Mention Git or GitHub as it is universally expected."})
    
    if len(action_verbs) < 4:
        recommendations.append({"type": "content", "priority": "medium", "icon": "✍️", "title": "Use Stronger Action Verbs", "message": "Start bullet points with verbs like Developed or Led."})
    
    # Priority sorting
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
    return recommendations


def match_jobs(resume_text, top_n=10, jobs_df=None):
    """
    Advanced Job Matcher using a Hybrid ML Approach:
    - 40% TF-IDF: Preserves exact keyword and technology stack matching.
    - 60% Sentence-BERT: Dense Semantic Vectors understand contextual similarity.
    """
    if jobs_df is None:
        jobs_df = load_jobs_dataset()
        
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
            "id": int(job["id"]),
            "job_title": str(job["job_title"]),
            "company": str(job["company"]),
            "location": str(job["location"]),
            "category": str(job["category"]),
            "experience_level": str(job["experience_level"]),
            "salary_range": str(job["salary_range"]),
            "description": str(job["description"]),
            "match_score": round(total_score * 100, 1),
            "semantic_score": round(sem_score * 100, 1),
            "keyword_score": round(key_score * 100, 1),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "skill_match_pct": round(len(matched_skills) / max(len(job_skills), 1) * 100, 1)
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

def analyze_resume(parsed_data):
    """
    Main execution pipeline for the advanced NLP analysis.
    Executes scoring, predictive classification, and hybrid job matching.
    """
    jobs_df = load_jobs_dataset()
    
    # Basic analysis
    score = calculate_resume_score(parsed_data)
    recommendations = generate_recommendations(parsed_data)
    
    # Extract Full Text for Machine Learning Models
    resume_text = parsed_data.get("raw_text", "") + " " + " ".join(parsed_data.get("all_skills", []))
    
    # ADVANCED ML: Predict Job Categories
    predicted_categories = predict_category(resume_text, jobs_df)
    
    # ADVANCED ML: Hybrid Job Matching
    top_jobs = match_jobs(resume_text, top_n=10, jobs_df=jobs_df)
    
    # Skill Gaps
    skill_gaps = get_skill_gap_analysis(parsed_data, top_jobs)
    
    return {
        "score": score,
        "recommendations": recommendations,
        "top_jobs": top_jobs,
        "predicted_categories": predicted_categories,  # New Feature
        "skill_gaps": skill_gaps,
        "extracted_skills": parsed_data.get("skills", {}),
        "all_skills": parsed_data.get("all_skills", []),
        "sections": parsed_data.get("sections", {}),
        "action_verbs": parsed_data.get("action_verbs", []),
        "contact_info": parsed_data.get("contact_info", {}),
        "word_count": parsed_data.get("word_count", 0)
    }
