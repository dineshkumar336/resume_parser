"""
Domain Detector Module
Two-stage career domain detection:
  Stage 1: Keyword heuristics (fast, transparent, high-confidence)
  Stage 2: Naive Bayes fallback with multi-domain seed training data
"""
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# ─────────────────────────────────────────────────────────────────
# Stage 1: Keyword Heuristics
# Maps detected keywords → career domain
# Ordered from most-specific to most-generic to avoid false matches
# ─────────────────────────────────────────────────────────────────
DOMAIN_KEYWORDS = {
    "Civil Engineering": [
        "autocad", "revit", "staad", "etabs", "primavera", "structural",
        "rcc", "concrete", "surveying", "levelling", "quantity surveying",
        "site engineer", "site management", "construction management",
        "civil engineer", "civil engineering", "infrastructure development",
        "highway", "road design", "drainage", "irrigation", "geotechnical",
        "bim", "b.e civil", "b.tech civil", "be civil"
    ],
    "Mechanical Engineering": [
        "solidworks", "catia", "ansys", "creo", "unigraphics", "hvac",
        "cfd", "fea", "finite element", "thermodynamics", "fluid mechanics",
        "cnc", "lathe", "milling", "welding", "lean manufacturing",
        "mechanical design", "machine design", "production planning",
        "b.e mechanical", "b.tech mechanical", "me mechanical"
    ],
    "Electrical Engineering": [
        "plc", "scada", "hmi", "eplan", "power systems", "motor drives",
        "vfd", "transformer", "switchgear", "relay", "dcs",
        "instrumentation", "pid", "electrical design",
        "b.e electrical", "b.tech electrical", "ee electrical"
    ],
    "Finance & Accounting": [
        "tally", "tally erp", "sap fico", "chartered accountant", "ca ",
        "cfa", "cpa", "acca", "frm", "balance sheet", "p&l",
        "accounts payable", "accounts receivable", "gst", "tds",
        "income tax", "audit", "statutory audit", "financial modelling",
        "investment banking", "equity research", "credit analysis",
        "budgeting", "forecasting", "ifrs", "gaap"
    ],
    "Marketing": [
        "seo", "sem", "google ads", "facebook ads", "social media marketing",
        "content marketing", "digital marketing", "brand management",
        "performance marketing", "growth hacking", "copywriting",
        "influencer marketing", "affiliate marketing"
    ],
    "Human Resources": [
        "recruitment", "talent acquisition", "onboarding", "payroll",
        "hris", "workday", "darwinbox", "hr policies", "labor law",
        "learning and development", "employer branding", "attrition"
    ],
    "Healthcare": [
        "mbbs", "md ", "bds", "nursing", "bsc nursing", "clinical",
        "patient care", "icu", "critical care", "radiology", "pathology",
        "pharmacy", "pharmacology", "ehr", "emr", "medical coding",
        "clinical research", "pharmacovigilance", "gcp", "adverse event"
    ],
    "UI/UX Design": [
        "figma", "sketch", "adobe xd", "zeplin", "invision",
        "ui design", "ux design", "wireframing", "prototyping",
        "user research", "design thinking", "interaction design",
        "motion graphics", "blender", "cinema 4d"
    ],
    "Sales & Business Development": [
        "b2b sales", "b2c sales", "enterprise sales", "saas sales",
        "business development", "lead generation", "cold calling",
        "account management", "key account", "revenue generation",
        "upselling", "cross selling", "channel sales", "fmcg sales"
    ],
    "Legal": [
        "llb", "llm", "corporate law", "contract drafting", "litigation",
        "arbitration", "intellectual property", "trademark", "patent",
        "gdpr", "sebi", "company law", "competition law", "tax law",
        "labour law", "due diligence"
    ],
    "Data Science": [
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
        "machine learning", "deep learning", "nlp", "computer vision",
        "data science", "mlops", "mlflow", "data engineer", "big data",
        "spark", "hadoop", "tableau", "power bi", "data analyst"
    ],
    "DevOps": [
        "docker", "kubernetes", "jenkins", "terraform", "ansible",
        "gitlab ci", "github actions", "ci/cd", "devops", "helm",
        "argocd", "prometheus", "grafana", "infrastructure as code"
    ],
    "Software Engineering": [
        "software engineer", "backend", "frontend", "full stack",
        "api development", "rest api", "microservices", "web development",
        "mobile development", "react", "angular", "vue", "django",
        "spring boot", "node.js", "java developer", "python developer"
    ],
}


def detect_domain_by_keywords(resume_text: str) -> str | None:
    """
    Stage 1: Scan resume text for domain-specific keywords.
    Returns the best-matching domain name, or None if no match found.
    """
    text_lower = resume_text.lower()
    scores = {}

    for domain, keywords in DOMAIN_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw.lower() in text_lower)
        if hits > 0:
            scores[domain] = hits

    if not scores:
        return None

    best = max(scores, key=scores.get)
    best_hits = scores[best]
    print(f"   [Domain Keywords] '{best}' detected ({best_hits} keyword hits)")
    return best


# ─────────────────────────────────────────────────────────────────
# Stage 2: Naive Bayes with Multi-Domain Seed Training Data
# Only used when keyword heuristics return None
# ─────────────────────────────────────────────────────────────────
NB_SEED_DATA = {
    "Civil Engineering": [
        "autocad revit structural design concrete site engineer construction rcc foundation surveying",
        "civil engineering infrastructure site management quantity surveying primavera etabs project planning",
        "b.e civil structural bim highway drainage irrigation geotechnical levelling estimation"
    ],
    "Mechanical Engineering": [
        "solidworks catia ansys thermodynamics fluid mechanics manufacturing cnc welding machining",
        "mechanical design hvac cfd fea production planning lean manufacturing kaizen quality control",
        "b.e mechanical machine design plc scada motor drives hydraulics pneumatics maintenance"
    ],
    "Electrical Engineering": [
        "plc scada hmi electrical design power systems motor drives vfd transformer relay protection",
        "instrumentation control systems pid embedded systems dcs electrical maintenance switchgear",
        "b.e electrical eplan matlab simulink iot sensors industrial automation panel wiring"
    ],
    "Finance & Accounting": [
        "chartered accountant tally balance sheet audit gst tds income tax financial analysis",
        "ca cfa cpa financial modelling investment banking equity research credit analysis budgeting",
        "accounts payable receivable sap fico ifrs gaap statutory audit internal audit compliance"
    ],
    "Marketing": [
        "seo sem google ads facebook ads social media marketing content marketing digital campaigns",
        "brand management performance marketing growth hacking a/b testing conversion copywriting email",
        "market research consumer behavior product marketing influencer affiliate hubspot analytics"
    ],
    "Human Resources": [
        "recruitment talent acquisition sourcing onboarding employee engagement payroll hris workday",
        "hr policies labor law compliance performance management kpi learning development succession",
        "employer branding background verification exit management darwinbox zoho people attrition"
    ],
    "Healthcare": [
        "mbbs md clinical patient care icu nursing hospital diagnosis treatment radiology pathology",
        "pharmacy pharmacology drug therapy ehr emr medical coding clinical research gcp trials",
        "public health healthcare administration pharmacovigilance adverse event protocol regulatory"
    ],
    "UI/UX Design": [
        "figma sketch adobe xd wireframing prototyping ui design ux design user research usability",
        "design thinking interaction design accessibility responsive motion graphics animation",
        "zeplin invision typography branding visual design component library design system"
    ],
    "Sales & Business Development": [
        "b2b sales enterprise saas business development lead generation cold calling account management",
        "revenue generation targets quota negotiation deal closing crm salesforce pipedrive upselling",
        "channel sales distribution fmcg key account customer acquisition client retention bd"
    ],
    "Legal": [
        "llb corporate law contract drafting litigation arbitration intellectual property trademark patent",
        "sebi gdpr company law competition tax law labour law legal research due diligence compliance",
        "mergers acquisitions regulatory corporate governance corporate secretarial legal documentation"
    ],
    "Data Science": [
        "machine learning deep learning nlp pandas numpy tensorflow pytorch scikit-learn data scientist",
        "data analysis visualization power bi tableau spark hadoop big data data pipeline feature engineering",
        "mlops mlflow airflow model training evaluation metrics stats hypothesis testing regression"
    ],
    "DevOps": [
        "docker kubernetes jenkins terraform ansible ci/cd pipeline infrastructure as code devops sre",
        "gitlab github actions circleci helm argocd prometheus grafana monitoring logging observability",
        "cloud aws azure gcp infrastructure automation deployment containerization orchestration"
    ],
    "Software Engineering": [
        "software engineer web development backend frontend full stack api rest microservices java python",
        "react angular vue django flask spring boot nodejs express typescript javascript developer",
        "system design algorithms data structures oop design patterns code review testing agile"
    ],
    "Cybersecurity": [
        "penetration testing ethical hacking vulnerability assessment siem firewall owasp cissp ceh",
        "network security incident response threat intelligence malware analysis forensics soc",
        "identity access management iam zero trust compliance security audit cloud security"
    ],
    "Product Management": [
        "product manager roadmap backlog grooming user stories stakeholder management prioritization",
        "product strategy market research competitive analysis go to market metrics kpi okr",
        "agile scrum sprint planning product lifecycle a/b testing user feedback analytics"
    ],
}

# Lazily trained NB model
_nb_model = None
_nb_vectorizer = None


def _get_nb_model():
    """Train (or return cached) the multi-domain NB fallback model."""
    global _nb_model, _nb_vectorizer
    if _nb_model is not None:
        return _nb_model, _nb_vectorizer

    print("   [Domain NB] Training multi-domain Naive Bayes classifier...")
    X_train, y_train = [], []
    for domain, sentences in NB_SEED_DATA.items():
        for sentence in sentences:
            X_train.append(sentence)
            y_train.append(domain)

    vectorizer = CountVectorizer(stop_words="english", max_features=2000)
    X_vec = vectorizer.fit_transform(X_train)
    clf = MultinomialNB()
    clf.fit(X_vec, y_train)

    _nb_vectorizer = vectorizer
    _nb_model = clf
    print(f"   [Domain NB] Ready — {len(NB_SEED_DATA)} domains, {len(X_train)} training samples")
    return _nb_model, _nb_vectorizer


def detect_domain_by_nb(resume_text: str) -> str:
    """
    Stage 2: Use Naive Bayes trained on seed data to predict career domain.
    Falls back to 'Software Engineering' on total failure.
    """
    try:
        clf, vectorizer = _get_nb_model()
        vec = vectorizer.transform([resume_text])
        probs = clf.predict_proba(vec)[0]
        classes = clf.classes_
        best_idx = probs.argmax()
        best_domain = classes[best_idx]
        confidence = round(probs[best_idx] * 100, 1)
        print(f"   [Domain NB] Predicted: '{best_domain}' ({confidence}% confidence)")
        return best_domain
    except Exception as e:
        print(f"   [Domain NB ERROR] {e} — defaulting to Software Engineering")
        return "Software Engineering"


# ─────────────────────────────────────────────────────────────────
# Public Entry Point
# ─────────────────────────────────────────────────────────────────
def detect_career_domain(resume_text: str) -> str:
    """
    Two-stage domain detection:
      1. Fast keyword heuristics (high precision)
      2. NB classifier fallback (handles ambiguous resumes)

    Returns a career domain string suitable for use as a JSearch query.
    """
    # Stage 1: Keywords
    domain = detect_domain_by_keywords(resume_text)
    if domain:
        return domain

    # Stage 2: NB Fallback
    print("   [Domain] No keyword match — falling back to NB classifier")
    return detect_domain_by_nb(resume_text)
