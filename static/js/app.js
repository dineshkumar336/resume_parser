/**
 * ML Resume Builder - Frontend Application
 * Handles file upload, API communication, and dynamic result rendering.
 */

// ===== DOM Elements =====
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const uploadContainer = document.getElementById('upload-container');
const fileSelected = document.getElementById('file-selected');
const fileName = document.getElementById('file-name');
const fileRemove = document.getElementById('file-remove');
const btnAnalyze = document.getElementById('btn-analyze');
const btnPaste = document.getElementById('btn-paste');
const pasteModal = document.getElementById('paste-modal');
const pasteModalClose = document.getElementById('paste-modal-close');
const resumeTextInput = document.getElementById('resume-text-input');
const btnAnalyzeText = document.getElementById('btn-analyze-text');
const loadingContainer = document.getElementById('loading-container');
const resultsSection = document.getElementById('results-section');
const errorToast = document.getElementById('error-toast');
const toastMessage = document.getElementById('toast-message');
const toastClose = document.getElementById('toast-close');
const navResults = document.getElementById('nav-results');
const navJobs = document.getElementById('nav-jobs');

let selectedFile = null;

// ===== File Upload Handling =====

// Click to upload
uploadZone.addEventListener('click', () => fileInput.click());

// File selected via input
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelected(e.target.files[0]);
    }
});

// Drag and drop
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    if (e.dataTransfer.files.length > 0) {
        handleFileSelected(e.dataTransfer.files[0]);
    }
});

function handleFileSelected(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Please upload a PDF file.');
        return;
    }
    selectedFile = file;
    fileName.textContent = file.name;
    uploadContainer.style.display = 'none';
    fileSelected.style.display = 'flex';
}

// Remove file
fileRemove.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    fileSelected.style.display = 'none';
    uploadContainer.style.display = 'block';
});

// ===== Analyze Button =====
btnAnalyze.addEventListener('click', () => {
    if (!selectedFile) return;
    analyzeFile(selectedFile);
});

// ===== Paste Text =====
btnPaste.addEventListener('click', () => {
    pasteModal.style.display = 'flex';
});

pasteModalClose.addEventListener('click', () => {
    pasteModal.style.display = 'none';
});

pasteModal.addEventListener('click', (e) => {
    if (e.target === pasteModal) pasteModal.style.display = 'none';
});

btnAnalyzeText.addEventListener('click', () => {
    const text = resumeTextInput.value.trim();
    if (text.length < 50) {
        showError('Please enter at least 50 characters of resume text.');
        return;
    }
    pasteModal.style.display = 'none';
    analyzeText(text);
});

// ===== API Calls =====

async function analyzeFile(file) {
    showLoading();
    const formData = new FormData();
    formData.append('resume', file);

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to analyze resume.');
        }

        hideLoading();
        renderResults(data.data);
    } catch (err) {
        hideLoading();
        showError(err.message);
        // Show upload again
        fileSelected.style.display = 'none';
        uploadContainer.style.display = 'block';
    }
}

async function analyzeText(text) {
    showLoading();

    try {
        const response = await fetch('/api/analyze-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to analyze resume.');
        }

        hideLoading();
        renderResults(data.data);
    } catch (err) {
        hideLoading();
        showError(err.message);
        uploadContainer.style.display = 'block';
    }
}

// ===== Loading State =====
let loadingInterval = null;

function showLoading() {
    uploadContainer.style.display = 'none';
    fileSelected.style.display = 'none';
    loadingContainer.style.display = 'block';
    resultsSection.style.display = 'none';

    // Animate loading steps
    const steps = document.querySelectorAll('.loading-step');
    let currentStep = 0;
    
    steps.forEach(s => { s.classList.remove('active', 'done'); });
    steps[0].classList.add('active');

    loadingInterval = setInterval(() => {
        if (currentStep < steps.length - 1) {
            steps[currentStep].classList.remove('active');
            steps[currentStep].classList.add('done');
            currentStep++;
            steps[currentStep].classList.add('active');
        }
    }, 800);
}

function hideLoading() {
    loadingContainer.style.display = 'none';
    if (loadingInterval) {
        clearInterval(loadingInterval);
        loadingInterval = null;
    }
}

// ===== Error Toast =====
function showError(message) {
    toastMessage.textContent = message;
    errorToast.style.display = 'flex';
    setTimeout(() => {
        errorToast.style.display = 'none';
    }, 6000);
}

toastClose.addEventListener('click', () => {
    errorToast.style.display = 'none';
});

// ===== Render Results =====
function renderResults(data) {
    // Show results & nav links
    resultsSection.style.display = 'block';
    navResults.style.display = 'inline-block';
    navJobs.style.display = 'inline-block';

    // Render each section
    renderScore(data.score);
    renderBreakdown(data.score);
    renderSkills(data.extracted_skills, data.all_skills);
    if (data.predicted_categories) {
        renderPredictions(data.predicted_categories);
    }
    renderRecommendations(data.recommendations);
    renderSkillGaps(data.skill_gaps);
    renderJobs(data.top_jobs);

    // Scroll to results
    setTimeout(() => {
        document.getElementById('score-section').scrollIntoView({ behavior: 'smooth' });
    }, 300);
}

// --- Score Circle ---
function renderScore(score) {
    const scoreNumber = document.getElementById('score-number');
    const scoreFill = document.getElementById('score-fill');
    const scoreVerdict = document.getElementById('score-verdict');
    const total = score.total;

    // Add SVG gradient definition if not present
    const svg = document.querySelector('.score-circle');
    if (!svg.querySelector('defs')) {
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
        gradient.setAttribute('id', 'scoreGradient');
        gradient.setAttribute('x1', '0%');
        gradient.setAttribute('y1', '0%');
        gradient.setAttribute('x2', '100%');
        gradient.setAttribute('y2', '100%');

        const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop1.setAttribute('offset', '0%');
        stop1.setAttribute('stop-color', '#8b5cf6');

        const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop2.setAttribute('offset', '100%');
        stop2.setAttribute('stop-color', '#06d6a0');

        gradient.appendChild(stop1);
        gradient.appendChild(stop2);
        defs.appendChild(gradient);
        svg.insertBefore(defs, svg.firstChild);
    }

    // Animate score number
    animateValue(scoreNumber, 0, total, 1500);

    // Animate circle
    const circumference = 2 * Math.PI * 85; // ~534
    const offset = circumference - (total / 100) * circumference;
    setTimeout(() => {
        scoreFill.style.strokeDashoffset = offset;
    }, 100);

    // Set verdict
    if (total >= 80) {
        scoreVerdict.textContent = '🌟 Excellent Resume!';
        scoreVerdict.style.color = '#06d6a0';
    } else if (total >= 60) {
        scoreVerdict.textContent = '👍 Good, Needs Some Improvements';
        scoreVerdict.style.color = '#f59e0b';
    } else if (total >= 40) {
        scoreVerdict.textContent = '⚠️ Needs Significant Work';
        scoreVerdict.style.color = '#f59e0b';
    } else {
        scoreVerdict.textContent = '🔧 Major Improvements Needed';
        scoreVerdict.style.color = '#ef4444';
    }
}

function animateValue(element, start, end, duration) {
    const startTime = performance.now();
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const current = Math.round(start + (end - start) * eased);
        element.textContent = current;
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    requestAnimationFrame(update);
}

// --- Score Breakdown ---
function renderBreakdown(score) {
    const container = document.getElementById('breakdown-list');
    container.innerHTML = '';

    const labels = {
        sections: { name: 'Resume Sections', icon: '📋' },
        skills: { name: 'Skills Detected', icon: '⚡' },
        action_verbs: { name: 'Action Verbs', icon: '✍️' },
        word_count: { name: 'Content Length', icon: '📄' },
        contact_info: { name: 'Contact Info', icon: '📧' }
    };

    const breakdown = score.breakdown;
    const maxScores = score.max_scores;

    for (const [key, info] of Object.entries(labels)) {
        const value = breakdown[key] || 0;
        const max = maxScores[key] || 1;
        const pct = Math.round((value / max) * 100);

        const item = document.createElement('div');
        item.className = 'breakdown-item';
        item.innerHTML = `
            <div class="breakdown-header">
                <span class="breakdown-name">${info.icon} ${info.name}</span>
                <span class="breakdown-score">${value}/${max}</span>
            </div>
            <div class="breakdown-bar">
                <div class="breakdown-fill" style="width: 0%;" data-width="${pct}%"></div>
            </div>
        `;
        container.appendChild(item);
    }

    // Animate bars
    setTimeout(() => {
        container.querySelectorAll('.breakdown-fill').forEach(bar => {
            bar.style.width = bar.dataset.width;
        });
    }, 300);
}

// --- Skills Detected ---
function renderSkills(skillsByCategory, allSkills) {
    const container = document.getElementById('skills-tag-cloud');
    const countEl = document.getElementById('skills-count');
    container.innerHTML = '';

    let delay = 0;
    for (const [category, skills] of Object.entries(skillsByCategory)) {
        for (const skill of skills) {
            const tag = document.createElement('span');
            tag.className = `skill-tag cat-${category}`;
            tag.textContent = skill;
            tag.style.animationDelay = `${delay * 50}ms`;
            container.appendChild(tag);
            delay++;
        }
    }

    countEl.textContent = `${allSkills.length} skills detected across ${Object.keys(skillsByCategory).length} categories`;
}

// --- Career Predictions ---
function renderPredictions(predictions) {
    const container = document.getElementById('prediction-grid');
    const section = document.getElementById('prediction-section');
    container.innerHTML = '';

    if (!predictions || predictions.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';

    predictions.forEach((pred, idx) => {
        const card = document.createElement('div');
        card.className = 'prediction-card';
        card.style.animationDelay = `${idx * 150}ms`;
        // Pass width via CSS var for animation
        card.style.setProperty('--prob-width', `${pred.probability}%`);
        
        card.innerHTML = `
            <div class="pred-header">
                <span class="pred-category">${pred.category}</span>
                <span class="pred-prob">${pred.probability}%</span>
            </div>
            <div class="pred-subtitle">Confidence Match</div>
        `;
        container.appendChild(card);
    });
}

// --- Recommendations ---
function renderRecommendations(recommendations) {
    const container = document.getElementById('recommendations-grid');
    container.innerHTML = '';

    if (recommendations.length === 0) {
        container.innerHTML = `
            <div class="rec-card" style="grid-column: 1/-1; text-align: center; padding: 40px;">
                <div style="font-size: 2rem; margin-bottom: 12px;">🎉</div>
                <h3 style="margin-bottom: 8px;">Great Job!</h3>
                <p style="color: var(--text-secondary);">Your resume looks well-structured. Keep it up!</p>
            </div>
        `;
        return;
    }

    recommendations.forEach((rec, idx) => {
        const card = document.createElement('div');
        card.className = 'rec-card';
        card.style.animationDelay = `${idx * 100}ms`;
        card.innerHTML = `
            <div class="rec-card-header">
                <div class="rec-icon">${rec.icon}</div>
                <div>
                    <div class="rec-title">${rec.title}</div>
                    <span class="rec-priority ${rec.priority}">${rec.priority} priority</span>
                </div>
            </div>
            <p class="rec-message">${rec.message}</p>
        `;
        container.appendChild(card);
    });
}

// --- Skill Gaps ---
function renderSkillGaps(skillGaps) {
    const container = document.getElementById('skill-gap-grid');
    const section = document.getElementById('skill-gap-section');
    container.innerHTML = '';

    if (!skillGaps || skillGaps.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';

    skillGaps.forEach((gap, idx) => {
        const card = document.createElement('div');
        card.className = 'skill-gap-card';
        card.style.animationDelay = `${idx * 80}ms`;
        card.innerHTML = `
            <div class="skill-gap-icon">${gap.demand_count}x</div>
            <div class="skill-gap-info">
                <div class="skill-gap-name">${gap.skill}</div>
                <div class="skill-gap-demand">${gap.message}</div>
            </div>
        `;
        container.appendChild(card);
    });
}

// --- Job Matches ---
function renderJobs(jobs) {
    const container = document.getElementById('jobs-grid');
    container.innerHTML = '';

    if (!jobs || jobs.length === 0) {
        container.innerHTML = `
            <div class="job-card" style="grid-column: 1/-1; text-align: center; padding: 40px;">
                <div style="font-size: 2rem; margin-bottom: 12px;">🔍</div>
                <h3 style="margin-bottom: 8px;">No Matches Found</h3>
                <p style="color: var(--text-secondary);">Try adding more details to your resume.</p>
            </div>
        `;
        return;
    }

    jobs.forEach((job, idx) => {
        const matchClass = job.match_score >= 30 ? 'high' : job.match_score >= 15 ? 'medium' : 'low';
        
        const card = document.createElement('div');
        card.className = 'job-card';
        card.style.animationDelay = `${idx * 100}ms`;

        // Build skills HTML
        const matchedSkillsHtml = job.matched_skills
            .map(s => `<span class="job-skill matched">✓ ${s}</span>`)
            .join('');
        const missingSkillsHtml = job.missing_skills
            .slice(0, 5)
            .map(s => `<span class="job-skill missing">✗ ${s}</span>`)
            .join('');

        card.innerHTML = `
            <div class="job-header">
                <div>
                    <div class="job-title">${job.job_title}</div>
                    <div class="job-company">${job.company}</div>
                </div>
                <div style="display: flex; gap: 4px; flex-direction: column; align-items: flex-end;">
                    <div class="job-match-badge ${matchClass}">Hybrid Match: ${job.match_score}%</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">
                        Semantic: ${job.semantic_score}% | Keyword: ${job.keyword_score}%
                    </div>
                </div>
            </div>
            <div class="job-meta">
                <span class="job-meta-item"><span class="job-meta-icon">📍</span> ${job.location}</span>
                <span class="job-meta-item"><span class="job-meta-icon">📂</span> ${job.category}</span>
                <span class="job-meta-item"><span class="job-meta-icon">📊</span> ${job.experience_level}</span>
                <span class="job-meta-item"><span class="job-meta-icon">💰</span> ${job.salary_range}</span>
            </div>
            <p class="job-description">${job.description}</p>
            <div class="job-skills-section">
                <div class="job-skills-title">Skill Match</div>
                <div class="job-skills-list">
                    ${matchedSkillsHtml}
                    ${missingSkillsHtml}
                </div>
            </div>
            <div class="job-skill-match-bar">
                <div class="job-skill-match-header">
                    <span class="job-skill-match-label">Skill Overlap</span>
                    <span class="job-skill-match-pct">${job.skill_match_pct}%</span>
                </div>
                <div class="job-skill-match-track">
                    <div class="job-skill-match-fill" style="width: 0%;" data-width="${job.skill_match_pct}%"></div>
                </div>
            </div>
        `;
        container.appendChild(card);
    });

    // Animate skill match bars
    setTimeout(() => {
        container.querySelectorAll('.job-skill-match-fill').forEach(bar => {
            bar.style.width = bar.dataset.width;
        });
    }, 500);
}

// ===== Keyboard Shortcuts =====
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && pasteModal.style.display === 'flex') {
        pasteModal.style.display = 'none';
    }
});

// ===== Init =====
console.log('🧠 ResumeAI — ML Resume Builder loaded');
