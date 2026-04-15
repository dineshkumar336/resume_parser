# 🧠 Resume Parser — ML-Powered Resume Analyzer & Job Matcher

An advanced Machine Learning-powered Resume Builder that analyzes resumes, scores them, predicts optimal career categories, and recommends the best-matched jobs using a **Hybrid ML Engine** combining **Sentence-BERT** (deep semantic understanding) and **TF-IDF** (keyword precision).

---

## ✨ Features

- **Resume Parsing** — Upload PDF or paste text; extracts skills, sections, contact info, and action verbs using NLP.
- **Resume Scoring (0-100)** — Weighted scoring algorithm evaluating sections, skills, action verbs, content length, and contact information.
- **AI Career Prediction** — A Multinomial Naive Bayes classifier trained on the job dataset predicts your optimal career track with confidence probabilities.
- **Hybrid Job Matching** — Combines:
  - **60% Sentence-BERT** (`all-MiniLM-L6-v2`) for deep semantic context matching.
  - **40% TF-IDF + Cosine Similarity** for precise keyword overlap.
- **Skill Gap Analysis** — Identifies missing in-demand skills based on your top matched jobs.
- **Improvement Recommendations** — Actionable suggestions to strengthen your resume.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, Flask |
| **ML / NLP** | scikit-learn, Sentence-Transformers, PyTorch, NLTK |
| **Frontend** | HTML5, CSS3 (Glassmorphism Dark Theme), Vanilla JS |
| **Data** | pandas, numpy, CSV dataset (102 jobs across 10+ categories) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/resume-parser.git
cd resume-parser

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open your browser at **http://127.0.0.1:5000**.

> **Note:** The first resume analysis will take ~5-10 seconds as the Sentence-BERT neural model loads into memory. Subsequent analyses are near-instant.

---

## 📁 Project Structure

```
resume-parser/
├── app.py                    # Flask backend (API endpoints)
├── generate_dataset.py       # Synthetic job dataset generator
├── requirements.txt          # Python dependencies
├── README.md
├── data/
│   ├── jobs_dataset.csv      # 102 jobs across 10+ categories
│   └── skills_database.json  # 150+ skills in 14 categories
├── ml/
│   ├── __init__.py
│   ├── resume_parser.py      # PDF extraction, NLP skill detection
│   └── recommender.py        # Hybrid ML engine (SBERT + TF-IDF + NB)
└── static/
    ├── index.html            # Single-page frontend
    ├── css/style.css         # Premium dark theme
    └── js/app.js             # Dynamic result rendering
```

---

## 🤖 Machine Learning Pipeline

```
Resume Text
    │
    ├──► TF-IDF Vectorization (keyword features)
    │       └──► Cosine Similarity (40% weight)
    │
    ├──► Sentence-BERT Embeddings (semantic features)
    │       └──► Cosine Similarity (60% weight)
    │
    ├──► Naive Bayes Classification
    │       └──► Career Category Prediction
    │
    └──► Hybrid Ranked Job Matches + Skill Gap Analysis
```

---

## 📸 Screenshots

### Hero Page
Premium dark-mode UI with drag-and-drop upload and text paste support.

### Analysis Dashboard
- Animated score circle with breakdown bars
- AI Career Prediction cards with confidence percentages
- Skill detection tag cloud
- Improvement recommendations
- Job match cards with Semantic vs Keyword score breakdown

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [Sentence-Transformers](https://www.sbert.net/) for semantic embeddings
- [scikit-learn](https://scikit-learn.org/) for TF-IDF and Naive Bayes
- [Flask](https://flask.palletsprojects.com/) for the web framework
