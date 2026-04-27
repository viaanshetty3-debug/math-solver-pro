"""Math solving engine using SymPy for symbolic computation."""

import re
import traceback
from io import BytesIO
from typing import Any

import sympy
from sympy import (
    Abs,
    E,
    Eq,
    Function,
    I,
    Matrix,
    Rational,
    Symbol,
    acos,
    asin,
    atan,
    binomial,
    ceiling,
    cos,
    cot,
    csc,
    diff,
    exp,
    factor,
    factorial,
    floor,
    gcd,
    integrate,
    lcm,
    limit,
    ln,
    log,
    oo,
    pi,
    sec,
    simplify,
    sin,
    solve,
    sqrt,
    summation,
    symbols,
    tan,
    trigsimp,
)
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


def parse_math_expression(expr_str: str) -> Any:
    """Parse a math expression string into a SymPy expression."""
    transformations = standard_transformations + (
        implicit_multiplication_application,
        convert_xor,
    )
    local_dict = {
        "x": Symbol("x"),
        "y": Symbol("y"),
        "z": Symbol("z"),
        "t": Symbol("t"),
        "n": Symbol("n"),
        "k": Symbol("k"),
        "pi": pi,
        "e": E,
        "i": I,
        "oo": oo,
        "inf": oo,
        "sqrt": sqrt,
        "sin": sin,
        "cos": cos,
        "tan": tan,
        "cot": cot,
        "sec": sec,
        "csc": csc,
        "asin": asin,
        "acos": acos,
        "atan": atan,
        "log": log,
        "ln": ln,
        "exp": exp,
        "abs": Abs,
        "factorial": factorial,
        "floor": floor,
        "ceiling": ceiling,
    }
    try:
        return parse_expr(expr_str, local_dict=local_dict, transformations=transformations)
    except Exception:
        return None


def solve_equation(equation_str: str) -> dict:
    """Solve an equation and return step-by-step solution."""
    steps = []
    try:
        equation_str = equation_str.strip()
        if "=" in equation_str and "==" not in equation_str:
            parts = equation_str.split("=")
            if len(parts) == 2:
                lhs = parse_math_expression(parts[0].strip())
                rhs = parse_math_expression(parts[1].strip())
                if lhs is not None and rhs is not None:
                    eq = Eq(lhs, rhs)
                    steps.append({
                        "step": "Parse the equation",
                        "result": f"$${sympy.latex(eq)}$$",
                        "explanation": f"We have the equation: {equation_str}",
                    })
                    x = Symbol("x")
                    free_syms = eq.free_symbols
                    solve_for = x if x in free_syms else (list(free_syms)[0] if free_syms else x)

                    moved = lhs - rhs
                    steps.append({
                        "step": "Rearrange to standard form",
                        "result": f"$${sympy.latex(moved)} = 0$$",
                        "explanation": "Move all terms to one side of the equation.",
                    })

                    simplified = simplify(moved)
                    if simplified != moved:
                        steps.append({
                            "step": "Simplify",
                            "result": f"$${sympy.latex(simplified)} = 0$$",
                            "explanation": "Simplify the expression.",
                        })

                    factored = factor(moved)
                    if factored != moved and factored != simplified:
                        steps.append({
                            "step": "Factor",
                            "result": f"$${sympy.latex(factored)} = 0$$",
                            "explanation": "Factor the expression if possible.",
                        })

                    solutions = solve(eq, solve_for)
                    if solutions:
                        sol_latex = ", ".join([f"$${sympy.latex(s)}$$" for s in solutions])
                        steps.append({
                            "step": "Solve",
                            "result": sol_latex,
                            "explanation": f"The solutions for {sympy.latex(solve_for)} are:",
                        })

                        for sol in solutions:
                            check = lhs.subs(solve_for, sol) - rhs.subs(solve_for, sol)
                            check_simplified = simplify(check)
                            steps.append({
                                "step": f"Verify: {sympy.latex(solve_for)} = {sympy.latex(sol)}",
                                "result": f"LHS - RHS = $${sympy.latex(check_simplified)}$$",
                                "explanation": f"Substituting {sympy.latex(solve_for)} = {sympy.latex(sol)} back verifies the solution.",
                            })
                    else:
                        steps.append({
                            "step": "Result",
                            "result": "No solutions found",
                            "explanation": "The equation has no solutions in the given domain.",
                        })

                    return {
                        "type": "equation",
                        "input": equation_str,
                        "solutions": [str(s) for s in solutions] if solutions else [],
                        "steps": steps,
                        "latex": sympy.latex(eq),
                        "success": True,
                    }

        expr = parse_math_expression(equation_str)
        if expr is not None:
            steps.append({
                "step": "Parse expression",
                "result": f"$${sympy.latex(expr)}$$",
                "explanation": f"The expression is: {equation_str}",
            })

            simplified = simplify(expr)
            steps.append({
                "step": "Simplify",
                "result": f"$${sympy.latex(simplified)}$$",
                "explanation": "Simplify the expression.",
            })

            try:
                evaluated = expr.evalf()
                if evaluated.is_number:
                    steps.append({
                        "step": "Evaluate numerically",
                        "result": f"$${sympy.latex(evaluated)}$$",
                        "explanation": "Numerical evaluation.",
                    })
            except Exception:
                pass

            return {
                "type": "expression",
                "input": equation_str,
                "simplified": str(simplified),
                "steps": steps,
                "latex": sympy.latex(expr),
                "success": True,
            }

    except Exception as e:
        steps.append({
            "step": "Error",
            "result": str(e),
            "explanation": "An error occurred during computation.",
        })

    return {
        "type": "unknown",
        "input": equation_str,
        "steps": steps,
        "success": len(steps) > 0 and steps[-1].get("step") != "Error",
    }


def compute_derivative(expr_str: str, var: str = "x", order: int = 1) -> dict:
    """Compute derivative with steps."""
    steps = []
    try:
        expr = parse_math_expression(expr_str)
        v = Symbol(var)

        steps.append({
            "step": "Original function",
            "result": f"$$f({var}) = {sympy.latex(expr)}$$",
            "explanation": f"We need to find the {'derivative' if order == 1 else f'order-{order} derivative'} of this function.",
        })

        current = expr
        for i in range(1, order + 1):
            derivative = diff(current, v)
            ord_label = {1: "first", 2: "second", 3: "third"}.get(i, f"{i}th")
            steps.append({
                "step": f"Compute {ord_label} derivative",
                "result": f"$$f{'′' * i}({var}) = {sympy.latex(derivative)}$$",
                "explanation": f"Apply differentiation rules to find the {ord_label} derivative.",
            })

            simplified = simplify(derivative)
            if simplified != derivative:
                steps.append({
                    "step": "Simplify",
                    "result": f"$$f{'′' * i}({var}) = {sympy.latex(simplified)}$$",
                    "explanation": "Simplify the result.",
                })
            current = derivative

        return {
            "type": "derivative",
            "input": expr_str,
            "variable": var,
            "order": order,
            "result": str(simplify(current)),
            "latex": sympy.latex(simplify(current)),
            "steps": steps,
            "success": True,
        }
    except Exception as e:
        return {"type": "derivative", "input": expr_str, "error": str(e), "steps": steps, "success": False}


def compute_integral(expr_str: str, var: str = "x", lower: str = None, upper: str = None) -> dict:
    """Compute integral with steps."""
    steps = []
    try:
        expr = parse_math_expression(expr_str)
        v = Symbol(var)
        is_definite = lower is not None and upper is not None

        if is_definite:
            lower_val = parse_math_expression(lower)
            upper_val = parse_math_expression(upper)
            steps.append({
                "step": "Set up the integral",
                "result": f"$$\\int_{{{sympy.latex(lower_val)}}}^{{{sympy.latex(upper_val)}}} {sympy.latex(expr)} \\, d{var}$$",
                "explanation": f"We need to evaluate the definite integral from {lower} to {upper}.",
            })
        else:
            steps.append({
                "step": "Set up the integral",
                "result": f"$$\\int {sympy.latex(expr)} \\, d{var}$$",
                "explanation": "We need to find the indefinite integral (antiderivative).",
            })

        antideriv = integrate(expr, v)
        steps.append({
            "step": "Find the antiderivative",
            "result": f"$$F({var}) = {sympy.latex(antideriv)}$$",
            "explanation": "Apply integration rules to find the antiderivative.",
        })

        simplified_antideriv = simplify(antideriv)
        if simplified_antideriv != antideriv:
            steps.append({
                "step": "Simplify",
                "result": f"$$F({var}) = {sympy.latex(simplified_antideriv)}$$",
                "explanation": "Simplify the antiderivative.",
            })

        if is_definite:
            result = integrate(expr, (v, lower_val, upper_val))
            steps.append({
                "step": "Apply the Fundamental Theorem of Calculus",
                "result": f"$$F({sympy.latex(upper_val)}) - F({sympy.latex(lower_val)}) = {sympy.latex(result)}$$",
                "explanation": f"Evaluate F({upper}) - F({lower}).",
            })

            try:
                numerical = result.evalf()
                if numerical.is_number:
                    steps.append({
                        "step": "Numerical value",
                        "result": f"$$\\approx {sympy.latex(numerical)}$$",
                        "explanation": "Approximate numerical value.",
                    })
            except Exception:
                pass

            return {
                "type": "definite_integral",
                "input": expr_str,
                "result": str(result),
                "latex": sympy.latex(result),
                "steps": steps,
                "success": True,
            }
        else:
            return {
                "type": "indefinite_integral",
                "input": expr_str,
                "result": str(simplified_antideriv) + " + C",
                "latex": sympy.latex(simplified_antideriv) + " + C",
                "steps": steps,
                "success": True,
            }
    except Exception as e:
        return {"type": "integral", "input": expr_str, "error": str(e), "steps": steps, "success": False}


def compute_limit(expr_str: str, var: str = "x", point: str = "0", direction: str = "") -> dict:
    """Compute limit with steps."""
    steps = []
    try:
        expr = parse_math_expression(expr_str)
        v = Symbol(var)
        p = parse_math_expression(point)

        dir_map = {"left": "-", "right": "+", "-": "-", "+": "+", "": "+-"}
        d = dir_map.get(direction, "+-")

        steps.append({
            "step": "Set up the limit",
            "result": f"$$\\lim_{{{var} \\to {sympy.latex(p)}}} {sympy.latex(expr)}$$",
            "explanation": f"Find the limit of the expression as {var} approaches {point}.",
        })

        try:
            direct = expr.subs(v, p)
            if direct.is_number and not direct.has(sympy.zoo, sympy.nan, oo):
                steps.append({
                    "step": "Direct substitution",
                    "result": f"$$f({sympy.latex(p)}) = {sympy.latex(direct)}$$",
                    "explanation": f"Try substituting {var} = {point} directly.",
                })
        except Exception:
            steps.append({
                "step": "Direct substitution",
                "result": "Indeterminate form",
                "explanation": "Direct substitution gives an indeterminate form. We need other techniques.",
            })

        result = limit(expr, v, p, d)
        steps.append({
            "step": "Evaluate the limit",
            "result": f"$$\\lim_{{{var} \\to {sympy.latex(p)}}} {sympy.latex(expr)} = {sympy.latex(result)}$$",
            "explanation": "The limit evaluates to:",
        })

        return {
            "type": "limit",
            "input": expr_str,
            "result": str(result),
            "latex": sympy.latex(result),
            "steps": steps,
            "success": True,
        }
    except Exception as e:
        return {"type": "limit", "input": expr_str, "error": str(e), "steps": steps, "success": False}


def solve_system(equations_str: list[str], variables_str: list[str] = None) -> dict:
    """Solve a system of equations."""
    steps = []
    try:
        if variables_str:
            vars_list = [Symbol(v.strip()) for v in variables_str]
        else:
            vars_list = None

        eqs = []
        for eq_str in equations_str:
            if "=" in eq_str and "==" not in eq_str:
                parts = eq_str.split("=")
                lhs = parse_math_expression(parts[0].strip())
                rhs = parse_math_expression(parts[1].strip())
                eqs.append(Eq(lhs, rhs))
            else:
                expr = parse_math_expression(eq_str)
                eqs.append(Eq(expr, 0))

        eq_latex = " \\\\ ".join([sympy.latex(eq) for eq in eqs])
        steps.append({
            "step": "System of equations",
            "result": f"$$\\begin{{cases}} {eq_latex} \\end{{cases}}$$",
            "explanation": "We need to solve the following system:",
        })

        if vars_list:
            solutions = solve(eqs, vars_list, dict=True)
        else:
            solutions = solve(eqs, dict=True)

        if solutions:
            for i, sol in enumerate(solutions):
                sol_str = ", ".join([f"{sympy.latex(k)} = {sympy.latex(v)}" for k, v in sol.items()])
                steps.append({
                    "step": f"Solution {i + 1}" if len(solutions) > 1 else "Solution",
                    "result": f"$${sol_str}$$",
                    "explanation": f"{'One of the solutions' if len(solutions) > 1 else 'The solution'} to the system is:",
                })
        else:
            steps.append({
                "step": "Result",
                "result": "No solution found",
                "explanation": "The system has no solution.",
            })

        return {
            "type": "system",
            "input": equations_str,
            "solutions": [
                {str(k): str(v) for k, v in sol.items()} for sol in solutions
            ] if solutions else [],
            "steps": steps,
            "success": True,
        }
    except Exception as e:
        return {"type": "system", "input": equations_str, "error": str(e), "steps": steps, "success": False}


def matrix_operations(matrix_str: str, operation: str = "determinant") -> dict:
    """Perform matrix operations."""
    steps = []
    try:
        rows = matrix_str.strip().split(";")
        matrix_data = []
        for row in rows:
            matrix_data.append([parse_math_expression(x.strip()) for x in row.split(",")])

        M = Matrix(matrix_data)
        steps.append({
            "step": "Input matrix",
            "result": f"$${sympy.latex(M)}$$",
            "explanation": "The given matrix is:",
        })

        if operation == "determinant":
            det = M.det()
            steps.append({
                "step": "Calculate determinant",
                "result": f"$$\\det(A) = {sympy.latex(det)}$$",
                "explanation": "The determinant of the matrix is:",
            })
            return {"type": "matrix", "operation": operation, "result": str(det), "steps": steps, "success": True}

        elif operation == "inverse":
            inv = M.inv()
            steps.append({
                "step": "Calculate inverse",
                "result": f"$$A^{{-1}} = {sympy.latex(inv)}$$",
                "explanation": "The inverse matrix is:",
            })
            return {"type": "matrix", "operation": operation, "result": str(inv), "steps": steps, "success": True}

        elif operation == "eigenvalues":
            eigenvals = M.eigenvals()
            ev_str = ", ".join([f"$${sympy.latex(k)}$$ (multiplicity {v})" for k, v in eigenvals.items()])
            steps.append({
                "step": "Find eigenvalues",
                "result": ev_str,
                "explanation": "The eigenvalues are:",
            })
            return {"type": "matrix", "operation": operation, "result": str(eigenvals), "steps": steps, "success": True}

        elif operation == "rref":
            rref, pivots = M.rref()
            steps.append({
                "step": "Row Reduced Echelon Form",
                "result": f"$${sympy.latex(rref)}$$",
                "explanation": f"RREF with pivot columns: {pivots}",
            })
            return {"type": "matrix", "operation": operation, "result": str(rref), "steps": steps, "success": True}

    except Exception as e:
        return {"type": "matrix", "error": str(e), "steps": steps, "success": False}


def analyze_question(question: str) -> dict:
    """Analyze a math question and attempt to solve it using SymPy."""
    question_lower = question.lower().strip()

    # Try to detect the type of problem
    if any(kw in question_lower for kw in ["derivative", "differentiate", "d/dx", "dy/dx", "f'(x)"]):
        expr_match = re.search(r'(?:of|differentiate|derivative)\s+(.+?)(?:\s+with|\s+at|\s*$)', question_lower)
        if expr_match:
            return compute_derivative(expr_match.group(1).strip())

    if any(kw in question_lower for kw in ["integrate", "integral", "antiderivative"]):
        expr_match = re.search(r'(?:of|integrate|integral)\s+(.+?)(?:\s+from|\s+with|\s+dx|\s*$)', question_lower)
        if expr_match:
            bounds_match = re.search(r'from\s+(\S+)\s+to\s+(\S+)', question_lower)
            if bounds_match:
                return compute_integral(expr_match.group(1).strip(), lower=bounds_match.group(1), upper=bounds_match.group(2))
            return compute_integral(expr_match.group(1).strip())

    if any(kw in question_lower for kw in ["limit", "lim", "approaches", "tends to"]):
        expr_match = re.search(r'(?:of|limit|lim)\s+(.+?)(?:\s+as|\s+when|\s*$)', question_lower)
        point_match = re.search(r'(?:approaches|tends to|to|->|→)\s+(\S+)', question_lower)
        if expr_match:
            point = point_match.group(1) if point_match else "0"
            return compute_limit(expr_match.group(1).strip(), point=point)

    if "=" in question and ("solve" in question_lower or "find" in question_lower):
        eq_match = re.search(r'(?:solve|find\s+\w+\s+(?:for|in))\s+(.+)', question_lower)
        if eq_match:
            return solve_equation(eq_match.group(1).strip())

    if "=" in question:
        return solve_equation(question)

    return solve_equation(question)
