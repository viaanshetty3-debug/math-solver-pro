# MathSolver Pro

A free, powerful math-solving web application with detailed step-by-step explanations, graph generation, and PDF support.

## Features

- **Quick Solve**: Type any math problem and get detailed step-by-step solutions with explanations
- **Specialized Solvers**: Dedicated tools for equations, derivatives, integrals, limits, systems of equations, and matrix operations
- **Graph Generation**: Plot functions, visualize solutions, and generate beautiful mathematical graphs
- **PDF Upload**: Upload exam papers or math worksheets — the app extracts questions and solves them all
- **PDF Export**: Download clean, professionally formatted solution PDFs with all explanations and graphs
- **LaTeX Rendering**: Beautiful mathematical notation using MathJax throughout the interface

## Tech Stack

- **Backend**: Python / FastAPI
- **Math Engine**: SymPy (symbolic computation)
- **Graphs**: Matplotlib + NumPy
- **PDF Processing**: PyMuPDF (extraction) + ReportLab (generation)
- **Frontend**: Vanilla HTML/CSS/JS with MathJax
- **AI Enhancement**: Optional OpenAI integration for complex word problems

## Quick Start

### Prerequisites
- Python 3.10+

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd math-solver-app

# Install dependencies
pip install -e .

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000` in your browser.

### Optional: AI Enhancement

For enhanced word problem solving, set an OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

The app works fully without this — SymPy handles all symbolic math. The AI is only used as an optional enhancement for complex word problems.

## Usage

### Quick Solve
Type any math problem in natural language or mathematical notation:
- `x^2 - 5x + 6 = 0` — Solve equations
- `derivative of x^3 * sin(x)` — Compute derivatives
- `integrate x^2 from 0 to 3` — Evaluate integrals
- `limit of sin(x)/x as x approaches 0` — Find limits

### Specialized Solvers
Use the dedicated tools for more control:
- **Equations**: Enter any equation to solve
- **Derivatives**: Specify expression, variable, and order
- **Integrals**: Indefinite or definite integrals with bounds
- **Limits**: One-sided or two-sided limits
- **Systems**: Multiple equations solved simultaneously
- **Matrices**: Determinant, inverse, eigenvalues, RREF

### PDF Upload
1. Upload a PDF containing math questions
2. The app extracts and identifies all questions
3. Each question is solved with detailed explanations
4. Download a formatted PDF with all solutions

### Graph Generation
Plot any mathematical function with customizable ranges.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/solve` | POST | Solve any math problem |
| `/api/solve/equation` | POST | Solve an equation |
| `/api/solve/derivative` | POST | Compute derivative |
| `/api/solve/integral` | POST | Compute integral |
| `/api/solve/limit` | POST | Compute limit |
| `/api/solve/system` | POST | Solve system of equations |
| `/api/solve/matrix` | POST | Matrix operations |
| `/api/plot` | POST | Generate function plot |
| `/api/upload-pdf` | POST | Upload and parse PDF |
| `/api/solve-pdf` | POST | Upload PDF, solve all questions |
| `/api/generate-pdf` | POST | Generate solution PDF |

## License

MIT
