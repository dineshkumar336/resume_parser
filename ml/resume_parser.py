"""
Resume Parser Module
Handles PDF text extraction, NLP preprocessing, and skill extraction.
"""
import re
import json
import os
from PyPDF2 import PdfReader


# Load skills database
SKILLS_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "skills_database.json")

def load_skills_database():
    """Load the skills database from JSON file."""
    with open(SKILLS_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_text_from_pdf(pdf_file):
    """Extract raw text from an uploaded PDF file."""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")


def preprocess_text(text):
    """Clean and preprocess resume text for analysis."""
    # Convert to lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    # Remove phone numbers
    text = re.sub(r'[\+]?[\d\s\-\(\)]{10,}', ' ', text)
    # Remove special characters but keep meaningful ones
    text = re.sub(r'[^a-z0-9\s\.\+\#\/\-]', ' ', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_skills(text, skills_db=None):
    """Extract skills from resume text by matching against skills database."""
    if skills_db is None:
        skills_db = load_skills_database()
    
    text_lower = text.lower()
    found_skills = {}
    
    for category, skills_list in skills_db.items():
        matched = []
        for skill in skills_list:
            skill_lower = skill.lower()
            # Use word boundary matching for short skills to avoid false positives
            if len(skill_lower) <= 2:
                # For very short skills like "r", "c", use exact word boundary
                pattern = r'\b' + re.escape(skill_lower) + r'\b'
                if re.search(pattern, text_lower):
                    matched.append(skill)
            else:
                if skill_lower in text_lower:
                    matched.append(skill)
        
        if matched:
            found_skills[category] = matched
    
    return found_skills


def extract_sections(text):
    """Detect which standard resume sections are present."""
    section_keywords = {
        "contact_info": ["email", "phone", "address", "linkedin", "github", "portfolio"],
        "objective": ["objective", "summary", "about me", "career objective", "professional summary"],
        "education": ["education", "academic", "university", "college", "degree", "bachelor", "master", "b.tech", "b.e.", "m.tech", "m.e.", "b.sc", "m.sc", "mba", "phd"],
        "experience": ["experience", "work history", "employment", "internship", "intern", "worked at", "working at"],
        "skills": ["skills", "technical skills", "technologies", "competencies", "proficiencies"],
        "projects": ["project", "projects", "personal project", "academic project", "side project"],
        "certifications": ["certification", "certifications", "certified", "certificate", "credential"],
        "achievements": ["achievement", "achievements", "awards", "honors", "accomplishments", "hackathon", "competition"],
        "publications": ["publication", "publications", "paper", "journal", "conference", "research"],
        "languages": ["languages", "language proficiency"],
        "volunteer": ["volunteer", "volunteering", "community service", "social work"],
        "hobbies": ["hobbies", "interests", "extracurricular"]
    }
    
    text_lower = text.lower()
    found_sections = {}
    
    for section, keywords in section_keywords.items():
        found = any(kw in text_lower for kw in keywords)
        found_sections[section] = found
    
    return found_sections


def extract_action_verbs(text):
    """Check for strong action verbs typically used in effective resumes."""
    action_verbs = [
        "developed", "designed", "implemented", "built", "created", "managed",
        "led", "coordinated", "optimized", "improved", "achieved", "delivered",
        "launched", "maintained", "analyzed", "resolved", "automated", "integrated",
        "collaborated", "mentored", "spearheaded", "streamlined", "engineered",
        "architected", "deployed", "configured", "established", "increased",
        "reduced", "enhanced", "transformed", "migrated", "contributed",
        "published", "presented", "documented", "tested", "debugged",
        "refactored", "scaled", "monitored", "supported", "trained"
    ]
    
    text_lower = text.lower()
    found_verbs = [verb for verb in action_verbs if verb in text_lower]
    return found_verbs


def extract_contact_info(text):
    """Extract contact-related information from resume."""
    info = {}
    
    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        info["email"] = email_match.group()
    
    # Phone
    phone_match = re.search(r'[\+]?[\d][\d\s\-\(\)]{8,15}', text)
    if phone_match:
        info["phone"] = phone_match.group().strip()
    
    # LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
    if linkedin_match:
        info["linkedin"] = linkedin_match.group()
    
    # GitHub
    github_match = re.search(r'github\.com/[\w\-]+', text, re.IGNORECASE)
    if github_match:
        info["github"] = github_match.group()
    
    return info


def count_words(text):
    """Count the number of words in the resume."""
    words = text.split()
    return len(words)


def parse_resume(pdf_file):
    """
    Main function: parse a resume PDF and return structured analysis.
    Returns a dictionary with all extracted information.
    """
    # Extract raw text
    raw_text = extract_text_from_pdf(pdf_file)
    
    if not raw_text or len(raw_text.strip()) < 50:
        raise ValueError("Could not extract meaningful text from the PDF. Please ensure the PDF contains selectable text (not a scanned image).")
    
    # Preprocess
    clean_text = preprocess_text(raw_text)
    
    # Load skills DB
    skills_db = load_skills_database()
    
    # Extract everything
    result = {
        "raw_text": raw_text,
        "clean_text": clean_text,
        "word_count": count_words(raw_text),
        "skills": extract_skills(raw_text, skills_db),
        "sections": extract_sections(raw_text),
        "action_verbs": extract_action_verbs(raw_text),
        "contact_info": extract_contact_info(raw_text),
    }
    
    # Flatten skills for easy access
    all_skills = []
    for category_skills in result["skills"].values():
        all_skills.extend(category_skills)
    result["all_skills"] = list(set(all_skills))
    
    return result
