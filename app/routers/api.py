"""API routes for the math solver app."""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.config import GENERATED_DIR, MAX_FILE_SIZE, UPLOAD_DIR
from app.services.ai_solver import solve_question
from app.services.graph_generator import (
    generate_geometry_diagram,
    plot_derivative,
    plot_equation_solution,
    plot_function,
    plot_integral,
)
from app.services.math_solver import (
    analyze_question,
    compute_derivative,
    compute_integral,
    compute_limit,
    matrix_operations,
    solve_equation,
    solve_system,
)
from app.services.pdf_generator import generate_solution_pdf
from app.services.pdf_processor import process_pdf

router = APIRouter(prefix="/api", tags=["math"])


@router.post("/solve")
async def solve_math_problem(
    question: str = Form(...),
    generate_graph: bool = Form(default=True),
):
    """Solve a single math problem with detailed steps."""
    result = await solve_question(question)

    # Generate graph if applicable
    graph_url = None
    if generate_graph and result.get("success"):
        problem_type = result.get("type", "")
        if problem_type == "equation" and result.get("solutions"):
            graph_path = plot_equation_solution(
                result.get("input", question),
                result.get("solutions", []),
            )
            if graph_path:
                graph_url = f"/api/image/{Path(graph_path).name}"
                result["graph_path"] = graph_path

        elif problem_type == "derivative":
            input_expr = result.get("input", "")
            deriv_result = result.get("result", "")
            if input_expr and deriv_result:
                graph_path = plot_derivative(input_expr, deriv_result)
                if graph_path:
                    graph_url = f"/api/image/{Path(graph_path).name}"
                    result["graph_path"] = graph_path

        elif problem_type in ("definite_integral", "indefinite_integral"):
            input_expr = result.get("input", "")
            if input_expr:
                graph_path = plot_integral(input_expr)
                if graph_path:
                    graph_url = f"/api/image/{Path(graph_path).name}"
                    result["graph_path"] = graph_path

        elif result.get("needs_graph") and result.get("graph_expression"):
            graph_path = plot_function(result["graph_expression"])
            if graph_path:
                graph_url = f"/api/image/{Path(graph_path).name}"
                result["graph_path"] = graph_path

    result["graph_url"] = graph_url
    return result


@router.post("/solve/equation")
async def solve_equation_endpoint(equation: str = Form(...)):
    """Solve a specific equation."""
    result = solve_equation(equation)
    if result.get("solutions"):
        graph_path = plot_equation_solution(equation, result["solutions"])
        if graph_path:
            result["graph_url"] = f"/api/image/{Path(graph_path).name}"
            result["graph_path"] = graph_path
    return result


@router.post("/solve/derivative")
async def solve_derivative_endpoint(
    expression: str = Form(...),
    variable: str = Form(default="x"),
    order: int = Form(default=1),
):
    """Compute derivative of an expression."""
    result = compute_derivative(expression, variable, order)
    if result.get("success") and result.get("result"):
        graph_path = plot_derivative(expression, result["result"])
        if graph_path:
            result["graph_url"] = f"/api/image/{Path(graph_path).name}"
            result["graph_path"] = graph_path
    return result


@router.post("/solve/integral")
async def solve_integral_endpoint(
    expression: str = Form(...),
    variable: str = Form(default="x"),
    lower: str = Form(default=None),
    upper: str = Form(default=None),
):
    """Compute integral of an expression."""
    result = compute_integral(expression, variable, lower, upper)
    if result.get("success"):
        lower_f = float(lower) if lower else None
        upper_f = float(upper) if upper else None
        graph_path = plot_integral(expression, lower_f, upper_f)
        if graph_path:
            result["graph_url"] = f"/api/image/{Path(graph_path).name}"
            result["graph_path"] = graph_path
    return result


@router.post("/solve/limit")
async def solve_limit_endpoint(
    expression: str = Form(...),
    variable: str = Form(default="x"),
    point: str = Form(default="0"),
    direction: str = Form(default=""),
):
    """Compute limit of an expression."""
    return compute_limit(expression, variable, point, direction)


@router.post("/solve/system")
async def solve_system_endpoint(
    equations: str = Form(...),
    variables: str = Form(default=None),
):
    """Solve a system of equations."""
    eq_list = [e.strip() for e in equations.split("\n") if e.strip()]
    var_list = [v.strip() for v in variables.split(",")] if variables else None
    return solve_system(eq_list, var_list)


@router.post("/solve/matrix")
async def solve_matrix_endpoint(
    matrix: str = Form(...),
    operation: str = Form(default="determinant"),
):
    """Perform matrix operation."""
    return matrix_operations(matrix, operation)


@router.post("/plot")
async def plot_function_endpoint(
    expression: str = Form(...),
    x_min: float = Form(default=-10),
    x_max: float = Form(default=10),
    title: str = Form(default=None),
):
    """Plot a mathematical function."""
    graph_path = plot_function(expression, x_range=(x_min, x_max), title=title)
    if graph_path:
        return {"graph_url": f"/api/image/{Path(graph_path).name}", "success": True}
    return {"error": "Failed to generate plot", "success": False}


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file containing math questions."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    file_id = uuid.uuid4().hex[:12]
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(content)

    result = process_pdf(str(file_path))
    result["file_id"] = file_id
    result["filename"] = file.filename

    return result


@router.post("/solve-pdf")
async def solve_pdf_questions(
    file: UploadFile = File(...),
    generate_graphs: bool = Form(default=True),
):
    """Upload a PDF, extract questions, solve them all, and return solutions."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    file_id = uuid.uuid4().hex[:12]
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(content)

    # Process PDF
    pdf_data = process_pdf(str(file_path))
    questions = pdf_data.get("questions", [])

    if not questions:
        return {
            "error": "No questions found in the PDF",
            "full_text": pdf_data.get("full_text", ""),
            "success": False,
        }

    # Solve each question
    solutions = []
    question_texts = []
    for q in questions:
        q_text = q.get("text", "")
        question_texts.append(q_text)
        solution = await solve_question(q_text)

        # Generate graph if applicable
        if generate_graphs and solution.get("success"):
            if solution.get("type") == "equation" and solution.get("solutions"):
                graph_path = plot_equation_solution(q_text, solution["solutions"])
                if graph_path:
                    solution["graph_url"] = f"/api/image/{Path(graph_path).name}"
                    solution["graph_path"] = graph_path
            elif solution.get("needs_graph") and solution.get("graph_expression"):
                graph_path = plot_function(solution["graph_expression"])
                if graph_path:
                    solution["graph_url"] = f"/api/image/{Path(graph_path).name}"
                    solution["graph_path"] = graph_path

        solutions.append(solution)

    # Generate solution PDF
    pdf_path = generate_solution_pdf(
        title=f"Solutions: {file.filename}",
        solutions=solutions,
        question_texts=question_texts,
    )

    return {
        "questions": questions,
        "solutions": solutions,
        "pdf_url": f"/api/download/{Path(pdf_path).name}",
        "num_questions": len(questions),
        "num_solved": sum(1 for s in solutions if s.get("success")),
        "success": True,
    }


@router.post("/generate-pdf")
async def generate_pdf(
    title: str = Form(default="Math Solutions"),
    solutions_json: str = Form(...),
    questions_json: str = Form(default="[]"),
):
    """Generate a PDF from solutions data."""
    import json

    try:
        solutions = json.loads(solutions_json)
        questions = json.loads(questions_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")

    pdf_path = generate_solution_pdf(
        title=title,
        solutions=solutions,
        question_texts=questions if questions else None,
    )

    return {
        "pdf_url": f"/api/download/{Path(pdf_path).name}",
        "success": True,
    }


@router.get("/image/{filename}")
async def get_image(filename: str):
    """Serve a generated image."""
    filepath = GENERATED_DIR / filename
    if not filepath.exists():
        # Also check uploads
        filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(str(filepath))


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Download a generated file (PDF, etc)."""
    filepath = GENERATED_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        str(filepath),
        media_type="application/pdf",
        filename=filename,
    )
