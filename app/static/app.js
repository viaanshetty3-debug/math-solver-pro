/* ===== MathSolver Pro - Frontend Logic ===== */

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
    });
});

// ===== Quick Solve Tab =====
function setExample(text) {
    document.getElementById('question-input').value = text;
}

async function solveProblem() {
    const question = document.getElementById('question-input').value.trim();
    if (!question) {
        showToast('Please enter a math problem', 'error');
        return;
    }

    showLoading('Solving your problem...');

    try {
        const formData = new FormData();
        formData.append('question', question);
        formData.append('generate_graph', 'true');

        const response = await fetch('/api/solve', { method: 'POST', body: formData });
        const data = await response.json();

        hideLoading();
        displaySingleResult(data, question);
    } catch (error) {
        hideLoading();
        showToast('An error occurred. Please try again.', 'error');
        console.error(error);
    }
}

function displaySingleResult(data, question) {
    const container = document.getElementById('single-results');
    container.innerHTML = '';
    container.classList.add('show');

    const card = createSolutionCard(question, data, 0);
    container.appendChild(card);

    // Re-render MathJax
    if (window.MathJax) {
        MathJax.typesetPromise([container]);
    }

    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ===== Specialized Solvers =====
let currentSolverType = 'equation';

function selectSolver(type) {
    currentSolverType = type;
    document.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
    event.currentTarget.classList.add('selected');

    // Show/hide relevant fields
    document.querySelectorAll('.solver-fields').forEach(f => f.style.display = 'none');
    const fields = document.getElementById(`fields-${type}`);
    if (fields) fields.style.display = 'block';
}

async function solveSpecialized() {
    showLoading('Computing...');

    try {
        let endpoint, formData = new FormData();

        switch (currentSolverType) {
            case 'equation':
                endpoint = '/api/solve/equation';
                formData.append('equation', document.getElementById('spec-equation').value);
                break;
            case 'derivative':
                endpoint = '/api/solve/derivative';
                formData.append('expression', document.getElementById('spec-derivative-expr').value);
                formData.append('variable', document.getElementById('spec-derivative-var').value || 'x');
                formData.append('order', document.getElementById('spec-derivative-order').value || '1');
                break;
            case 'integral':
                endpoint = '/api/solve/integral';
                formData.append('expression', document.getElementById('spec-integral-expr').value);
                formData.append('variable', document.getElementById('spec-integral-var').value || 'x');
                const lower = document.getElementById('spec-integral-lower').value;
                const upper = document.getElementById('spec-integral-upper').value;
                if (lower) formData.append('lower', lower);
                if (upper) formData.append('upper', upper);
                break;
            case 'limit':
                endpoint = '/api/solve/limit';
                formData.append('expression', document.getElementById('spec-limit-expr').value);
                formData.append('variable', document.getElementById('spec-limit-var').value || 'x');
                formData.append('point', document.getElementById('spec-limit-point').value || '0');
                break;
            case 'system':
                endpoint = '/api/solve/system';
                formData.append('equations', document.getElementById('spec-system-eqs').value);
                const vars = document.getElementById('spec-system-vars').value;
                if (vars) formData.append('variables', vars);
                break;
            case 'matrix':
                endpoint = '/api/solve/matrix';
                formData.append('matrix', document.getElementById('spec-matrix-data').value);
                formData.append('operation', document.getElementById('spec-matrix-op').value);
                break;
            default:
                hideLoading();
                return;
        }

        const response = await fetch(endpoint, { method: 'POST', body: formData });
        const data = await response.json();

        hideLoading();
        displaySpecializedResult(data);
    } catch (error) {
        hideLoading();
        showToast('An error occurred. Please try again.', 'error');
        console.error(error);
    }
}

function displaySpecializedResult(data) {
    const container = document.getElementById('specialized-results');
    container.innerHTML = '';
    container.classList.add('show');

    const card = createSolutionCard(data.input || '', data, 0);
    container.appendChild(card);

    if (window.MathJax) {
        MathJax.typesetPromise([container]);
    }

    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ===== Graph Tab =====
async function plotGraph() {
    const expr = document.getElementById('plot-expression').value.trim();
    if (!expr) {
        showToast('Please enter an expression to plot', 'error');
        return;
    }

    showLoading('Generating graph...');

    try {
        const formData = new FormData();
        formData.append('expression', expr);
        formData.append('x_min', document.getElementById('plot-xmin').value || '-10');
        formData.append('x_max', document.getElementById('plot-xmax').value || '10');
        formData.append('title', document.getElementById('plot-title').value || '');

        const response = await fetch('/api/plot', { method: 'POST', body: formData });
        const data = await response.json();

        hideLoading();

        if (data.success && data.graph_url) {
            const container = document.getElementById('graph-results');
            container.innerHTML = `
                <div class="graph-container">
                    <img src="${data.graph_url}" alt="Graph">
                </div>
                <div class="btn-group" style="margin-top: 16px; justify-content: center;">
                    <a href="${data.graph_url}" download class="btn btn-secondary">
                        <span class="btn-icon">📥</span> Download Image
                    </a>
                </div>
            `;
            container.classList.add('show');
        } else {
            showToast('Failed to generate graph', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('An error occurred', 'error');
    }
}

// ===== PDF Upload Tab =====
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('pdf-input');
let selectedFile = null;

if (uploadZone) {
    uploadZone.addEventListener('click', () => fileInput.click());
    uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('dragover'); });
    uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files[0]) handleFileSelect(e.dataTransfer.files[0]);
    });
}

if (fileInput) {
    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) handleFileSelect(e.target.files[0]);
    });
}

function handleFileSelect(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('Please select a PDF file', 'error');
        return;
    }
    if (file.size > 50 * 1024 * 1024) {
        showToast('File too large (max 50MB)', 'error');
        return;
    }

    selectedFile = file;
    const preview = document.getElementById('file-preview');
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatFileSize(file.size);
    preview.classList.add('show');
}

function removeFile() {
    selectedFile = null;
    fileInput.value = '';
    document.getElementById('file-preview').classList.remove('show');
}

async function solvePDF() {
    if (!selectedFile) {
        showToast('Please select a PDF file first', 'error');
        return;
    }

    showLoading('Processing PDF and solving questions...');

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('generate_graphs', 'true');

        const response = await fetch('/api/solve-pdf', { method: 'POST', body: formData });
        const data = await response.json();

        hideLoading();

        if (data.success) {
            displayPDFResults(data);
        } else {
            showToast(data.error || 'Failed to process PDF', 'error');
            if (data.full_text) {
                const container = document.getElementById('pdf-results');
                container.innerHTML = `
                    <div class="solution-card">
                        <div class="solution-card-body">
                            <h3>Extracted Text (no questions detected):</h3>
                            <pre style="white-space: pre-wrap; font-size: 13px; color: var(--gray-600); margin-top: 12px;">${escapeHtml(data.full_text)}</pre>
                        </div>
                    </div>
                `;
                container.classList.add('show');
            }
        }
    } catch (error) {
        hideLoading();
        showToast('An error occurred', 'error');
        console.error(error);
    }
}

function displayPDFResults(data) {
    const container = document.getElementById('pdf-results');
    container.innerHTML = '';
    container.classList.add('show');

    // Stats header
    const header = document.createElement('div');
    header.className = 'pdf-solutions-header';
    header.innerHTML = `
        <div class="pdf-stats">
            <div class="stat">
                <div class="stat-value">${data.num_questions}</div>
                <div class="stat-label">Questions Found</div>
            </div>
            <div class="stat">
                <div class="stat-value">${data.num_solved}</div>
                <div class="stat-label">Solved</div>
            </div>
        </div>
        <div class="btn-group">
            <a href="${data.pdf_url}" download class="btn btn-success">
                <span class="btn-icon">📄</span> Download Solutions PDF
            </a>
            <button class="btn btn-secondary" onclick="generateCustomPDF()">
                <span class="btn-icon">⚙️</span> Customize PDF
            </button>
        </div>
    `;
    container.appendChild(header);

    // Store solutions data for PDF generation
    window.lastPDFSolutions = data;

    // Solution cards
    const questions = data.questions || [];
    const solutions = data.solutions || [];

    for (let i = 0; i < solutions.length; i++) {
        const qText = questions[i] ? questions[i].text : `Question ${i + 1}`;
        const card = createSolutionCard(qText, solutions[i], i);
        container.appendChild(card);
    }

    if (window.MathJax) {
        MathJax.typesetPromise([container]);
    }

    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function generateCustomPDF() {
    if (!window.lastPDFSolutions) return;

    showLoading('Generating PDF...');

    try {
        const formData = new FormData();
        formData.append('title', 'Math Solutions');
        formData.append('solutions_json', JSON.stringify(window.lastPDFSolutions.solutions));
        formData.append('questions_json', JSON.stringify(
            window.lastPDFSolutions.questions.map(q => q.text)
        ));

        const response = await fetch('/api/generate-pdf', { method: 'POST', body: formData });
        const data = await response.json();

        hideLoading();

        if (data.success) {
            window.open(data.pdf_url, '_blank');
            showToast('PDF generated successfully!', 'success');
        }
    } catch (error) {
        hideLoading();
        showToast('Failed to generate PDF', 'error');
    }
}

// ===== Shared Components =====
function createSolutionCard(question, solution, index) {
    const card = document.createElement('div');
    card.className = 'solution-card';

    const statusIcon = solution.success ? '🟢' : '🔴';
    const solverBadge = solution.solver === 'ai' ? '<span class="badge" style="font-size:11px;margin-left:8px;background:var(--purple-50);color:var(--purple-600);border:1px solid var(--purple-500);">AI</span>' :
                        solution.solver === 'sympy' ? '<span class="badge" style="font-size:11px;margin-left:8px;background:var(--blue-50);color:var(--blue-600);border:1px solid var(--blue-500);">SymPy</span>' : '';

    const header = document.createElement('div');
    header.className = 'solution-card-header';
    header.innerHTML = `
        <h3>${statusIcon} Question ${index + 1} ${solverBadge}</h3>
        <span class="collapse-icon">▼</span>
    `;

    const body = document.createElement('div');
    body.className = 'solution-card-body';

    // Question text
    if (question) {
        body.innerHTML += `<div class="question-text">${escapeHtml(question)}</div>`;
    }

    // Steps
    const steps = solution.steps || [];
    steps.forEach((step, si) => {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'step';
        stepDiv.innerHTML = `
            <div class="step-header">
                <div class="step-number">${si + 1}</div>
                <div class="step-title">${escapeHtml(step.step || '')}</div>
            </div>
            ${step.explanation ? `<div class="step-explanation">${escapeHtml(step.explanation)}</div>` : ''}
            ${step.result ? `<div class="step-result">${step.result}</div>` : ''}
        `;
        body.appendChild(stepDiv);
    });

    // Final answer
    let finalAnswer = solution.final_answer || solution.result || solution.simplified || '';
    const solList = solution.solutions || [];
    if (solList.length > 0) {
        finalAnswer = solList.join(', ');
    }

    if (finalAnswer) {
        body.innerHTML += `
            <div class="final-answer">
                <span class="answer-label">ANSWER:</span>
                <span class="answer-value">${escapeHtml(String(finalAnswer))}</span>
            </div>
        `;
    }

    // Graph
    const graphUrl = solution.graph_url;
    if (graphUrl) {
        body.innerHTML += `
            <div class="graph-container">
                <img src="${graphUrl}" alt="Solution graph" loading="lazy">
            </div>
        `;
    }

    card.appendChild(header);
    card.appendChild(body);

    // Collapse toggle
    header.addEventListener('click', () => {
        header.classList.toggle('collapsed');
        body.classList.toggle('collapsed');
    });

    return card;
}

// ===== Utility Functions =====
function showLoading(text = 'Processing...') {
    const overlay = document.getElementById('loading-overlay');
    overlay.querySelector('.loading-text').textContent = text;
    overlay.classList.add('show');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('show');
}

function showToast(message, type = 'info') {
    // Remove existing toasts
    document.querySelectorAll('.toast').forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Advanced options toggle
document.querySelectorAll('.advanced-toggle').forEach(toggle => {
    toggle.addEventListener('click', () => {
        const target = document.getElementById(toggle.dataset.target);
        if (target) target.classList.toggle('show');
    });
});

// Keyboard shortcut: Ctrl+Enter to solve
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        const activePanel = document.querySelector('.tab-panel.active');
        if (activePanel) {
            const id = activePanel.id;
            if (id === 'tab-solve') solveProblem();
            else if (id === 'tab-specialized') solveSpecialized();
            else if (id === 'tab-graph') plotGraph();
            else if (id === 'tab-pdf') solvePDF();
        }
    }
});
