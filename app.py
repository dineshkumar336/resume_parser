"""
ML Resume Builder - Flask Backend
Serves the frontend and provides API endpoints for resume analysis.
"""
import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from ml.resume_parser import parse_resume
from ml.recommender import analyze_resume, load_jobs_dataset

app = Flask(__name__, static_folder="static", static_url_path="")

# Configure upload settings
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max file size
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---- Frontend Routes ----

@app.route("/")
def serve_index():
    """Serve the main frontend page."""
    return send_from_directory("static", "index.html")


# ---- API Routes ----

@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Analyze an uploaded resume PDF.
    Accepts: multipart/form-data with 'resume' file field
    Returns: JSON with score, recommendations, job matches, and skill analysis
    """
    # Check if file was uploaded
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded. Please upload a PDF file."}), 400
    
    file = request.files["resume"]
    
    if file.filename == "":
        return jsonify({"error": "No file selected. Please choose a PDF file."}), 400
    
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported. Please upload a .pdf file."}), 400
    
    try:
        # Parse the resume
        parsed_data = parse_resume(file)
        
        # Run full analysis
        results = analyze_resume(parsed_data)
        
        return jsonify({
            "success": True,
            "data": results
        })
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error analyzing resume: {e}", file=sys.stderr)
        return jsonify({"error": "An unexpected error occurred while analyzing the resume. Please try again."}), 500


@app.route("/api/analyze-text", methods=["POST"])
def analyze_text():
    """
    Analyze plain text resume content (for paste functionality).
    Accepts: JSON with 'text' field
    Returns: Same as /api/analyze
    """
    data = request.get_json()
    
    if not data or not data.get("text"):
        return jsonify({"error": "No resume text provided."}), 400
    
    text = data["text"].strip()
    
    if len(text) < 50:
        return jsonify({"error": "Resume text is too short. Please provide a more detailed resume."}), 400
    
    try:
        # Create a mock parsed_data structure from plain text
        from ml.resume_parser import preprocess_text, extract_skills, extract_sections, extract_action_verbs, extract_contact_info, count_words, load_skills_database
        
        skills_db = load_skills_database()
        
        parsed_data = {
            "raw_text": text,
            "clean_text": preprocess_text(text),
            "word_count": count_words(text),
            "skills": extract_skills(text, skills_db),
            "sections": extract_sections(text),
            "action_verbs": extract_action_verbs(text),
            "contact_info": extract_contact_info(text),
        }
        
        all_skills = []
        for category_skills in parsed_data["skills"].values():
            all_skills.extend(category_skills)
        parsed_data["all_skills"] = list(set(all_skills))
        
        results = analyze_resume(parsed_data)
        
        return jsonify({
            "success": True,
            "data": results
        })
    
    except Exception as e:
        print(f"Error analyzing text: {e}", file=sys.stderr)
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    """Return the full job dataset for browsing."""
    try:
        jobs_df = load_jobs_dataset()
        category = request.args.get("category")
        level = request.args.get("level")
        
        if category:
            jobs_df = jobs_df[jobs_df["category"].str.lower() == category.lower()]
        if level:
            jobs_df = jobs_df[jobs_df["experience_level"].str.lower() == level.lower()]
        
        jobs = jobs_df.to_dict(orient="records")
        return jsonify({"success": True, "data": jobs, "total": len(jobs)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Return available job categories and experience levels."""
    try:
        jobs_df = load_jobs_dataset()
        categories = sorted(jobs_df["category"].unique().tolist())
        levels = sorted(jobs_df["experience_level"].unique().tolist())
        
        return jsonify({
            "success": True,
            "categories": categories,
            "experience_levels": levels
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Generate dataset if it doesn't exist
    dataset_path = os.path.join("data", "jobs_dataset.csv")
    if not os.path.exists(dataset_path):
        print("Generating job dataset...")
        from generate_dataset import main as gen_main
        gen_main()
        print("Dataset generated!")
    
    print("\n>>> ML Resume Builder <<<")
    print("=" * 40)
    print("Open in browser: http://127.0.0.1:5000")
    print("=" * 40 + "\n")
    
    # Run server (use_reloader=False prevents watchdog from crashing ML models)
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)
