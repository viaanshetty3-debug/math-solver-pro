"""Generate mathematical graphs and diagrams using matplotlib."""

import io
import uuid
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import sympy
from sympy import Symbol, lambdify, pi, sqrt, sin, cos, tan, log, exp

from app.config import GENERATED_DIR
from app.services.math_solver import parse_math_expression


def plot_function(
    expr_str: str,
    x_range: tuple = (-10, 10),
    title: str = None,
    show_grid: bool = True,
    filename: str = None,
) -> str:
    """Plot a mathematical function and save to file."""
    try:
        expr = parse_math_expression(expr_str)
        if expr is None:
            return None

        x = Symbol("x")
        f = lambdify(x, expr, modules=["numpy"])

        fig, ax = plt.subplots(1, 1, figsize=(10, 7), dpi=100)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#fafafa")

        x_vals = np.linspace(float(x_range[0]), float(x_range[1]), 1000)

        try:
            y_vals = f(x_vals)
            y_vals = np.where(np.abs(y_vals) > 1000, np.nan, y_vals)
        except Exception:
            y_vals = np.array([float(expr.subs(Symbol("x"), xi).evalf()) for xi in x_vals])
            y_vals = np.where(np.abs(y_vals) > 1000, np.nan, y_vals)

        ax.plot(x_vals, y_vals, color="#2563eb", linewidth=2.5, label=f"$y = {sympy.latex(expr)}$")

        ax.axhline(y=0, color="#64748b", linewidth=0.8, linestyle="-")
        ax.axvline(x=0, color="#64748b", linewidth=0.8, linestyle="-")

        if show_grid:
            ax.grid(True, alpha=0.3, linestyle="--", color="#94a3b8")

        ax.set_xlabel("x", fontsize=14, color="#334155")
        ax.set_ylabel("y", fontsize=14, color="#334155")
        ax.set_title(title or f"$y = {sympy.latex(expr)}$", fontsize=16, color="#1e293b", pad=15)
        ax.legend(fontsize=12, loc="upper right", framealpha=0.9)

        ax.tick_params(colors="#475569", labelsize=11)
        for spine in ax.spines.values():
            spine.set_color("#cbd5e1")

        plt.tight_layout()

        if not filename:
            filename = f"plot_{uuid.uuid4().hex[:8]}.png"
        filepath = GENERATED_DIR / filename
        fig.savefig(filepath, bbox_inches="tight", facecolor="#ffffff")
        plt.close(fig)

        return str(filepath)
    except Exception as e:
        plt.close("all")
        return None


def plot_equation_solution(equation_str: str, solutions: list, filename: str = None) -> str:
    """Plot equation with solution points highlighted."""
    try:
        if "=" in equation_str:
            parts = equation_str.split("=")
            lhs = parse_math_expression(parts[0].strip())
            rhs = parse_math_expression(parts[1].strip())
        else:
            lhs = parse_math_expression(equation_str)
            rhs = sympy.Integer(0)

        if lhs is None:
            return None

        x = Symbol("x")
        f_lhs = lambdify(x, lhs, modules=["numpy"])
        f_rhs = lambdify(x, rhs, modules=["numpy"])

        sol_vals = []
        for s in solutions:
            try:
                val = float(parse_math_expression(str(s)).evalf())
                sol_vals.append(val)
            except Exception:
                pass

        if sol_vals:
            x_min = min(sol_vals) - 5
            x_max = max(sol_vals) + 5
        else:
            x_min, x_max = -10, 10

        fig, ax = plt.subplots(figsize=(10, 7), dpi=100)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#fafafa")

        x_vals = np.linspace(x_min, x_max, 1000)

        try:
            y_lhs = f_lhs(x_vals)
            y_lhs = np.where(np.abs(y_lhs) > 1000, np.nan, y_lhs)
        except Exception:
            y_lhs = np.zeros_like(x_vals)

        ax.plot(x_vals, y_lhs, color="#2563eb", linewidth=2.5, label=f"$y = {sympy.latex(lhs)}$")

        if not rhs.is_number or rhs != 0:
            try:
                y_rhs = f_rhs(x_vals)
                y_rhs = np.where(np.abs(y_rhs) > 1000, np.nan, y_rhs)
            except Exception:
                y_rhs = np.full_like(x_vals, float(rhs.evalf()))
            ax.plot(x_vals, y_rhs, color="#dc2626", linewidth=2.5, label=f"$y = {sympy.latex(rhs)}$", linestyle="--")

        for sv in sol_vals:
            try:
                y_val = float(lhs.subs(x, sv).evalf())
                ax.plot(sv, y_val, "o", color="#16a34a", markersize=12, zorder=5, markeredgecolor="white", markeredgewidth=2)
                ax.annotate(
                    f"x = {sv:.4g}",
                    (sv, y_val),
                    textcoords="offset points",
                    xytext=(10, 15),
                    fontsize=11,
                    color="#16a34a",
                    fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#16a34a", alpha=0.9),
                )
            except Exception:
                pass

        ax.axhline(y=0, color="#64748b", linewidth=0.8)
        ax.axvline(x=0, color="#64748b", linewidth=0.8)
        ax.grid(True, alpha=0.3, linestyle="--", color="#94a3b8")
        ax.set_xlabel("x", fontsize=14, color="#334155")
        ax.set_ylabel("y", fontsize=14, color="#334155")
        ax.set_title(f"Solutions of ${sympy.latex(lhs)} = {sympy.latex(rhs)}$", fontsize=16, color="#1e293b", pad=15)
        ax.legend(fontsize=12, framealpha=0.9)
        ax.tick_params(colors="#475569", labelsize=11)
        for spine in ax.spines.values():
            spine.set_color("#cbd5e1")

        plt.tight_layout()

        if not filename:
            filename = f"eq_plot_{uuid.uuid4().hex[:8]}.png"
        filepath = GENERATED_DIR / filename
        fig.savefig(filepath, bbox_inches="tight", facecolor="#ffffff")
        plt.close(fig)
        return str(filepath)
    except Exception:
        plt.close("all")
        return None


def plot_derivative(expr_str: str, derivative_str: str, filename: str = None) -> str:
    """Plot a function and its derivative together."""
    try:
        expr = parse_math_expression(expr_str)
        deriv = parse_math_expression(derivative_str)
        if expr is None or deriv is None:
            return None

        x = Symbol("x")
        f = lambdify(x, expr, modules=["numpy"])
        f_prime = lambdify(x, deriv, modules=["numpy"])

        fig, ax = plt.subplots(figsize=(10, 7), dpi=100)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#fafafa")

        x_vals = np.linspace(-10, 10, 1000)

        y_vals = np.array([float(expr.subs(x, xi).evalf()) if abs(float(expr.subs(x, xi).evalf())) < 1000 else np.nan for xi in x_vals])
        dy_vals = np.array([float(deriv.subs(x, xi).evalf()) if abs(float(deriv.subs(x, xi).evalf())) < 1000 else np.nan for xi in x_vals])

        ax.plot(x_vals, y_vals, color="#2563eb", linewidth=2.5, label=f"$f(x) = {sympy.latex(expr)}$")
        ax.plot(x_vals, dy_vals, color="#dc2626", linewidth=2.5, linestyle="--", label=f"$f'(x) = {sympy.latex(deriv)}$")

        ax.axhline(y=0, color="#64748b", linewidth=0.8)
        ax.axvline(x=0, color="#64748b", linewidth=0.8)
        ax.grid(True, alpha=0.3, linestyle="--", color="#94a3b8")
        ax.set_xlabel("x", fontsize=14, color="#334155")
        ax.set_ylabel("y", fontsize=14, color="#334155")
        ax.set_title("Function and its Derivative", fontsize=16, color="#1e293b", pad=15)
        ax.legend(fontsize=12, framealpha=0.9)
        ax.tick_params(colors="#475569", labelsize=11)
        for spine in ax.spines.values():
            spine.set_color("#cbd5e1")

        plt.tight_layout()

        if not filename:
            filename = f"deriv_plot_{uuid.uuid4().hex[:8]}.png"
        filepath = GENERATED_DIR / filename
        fig.savefig(filepath, bbox_inches="tight", facecolor="#ffffff")
        plt.close(fig)
        return str(filepath)
    except Exception:
        plt.close("all")
        return None


def plot_integral(expr_str: str, lower: float = None, upper: float = None, filename: str = None) -> str:
    """Plot a function with shaded area under the curve for definite integrals."""
    try:
        expr = parse_math_expression(expr_str)
        if expr is None:
            return None

        x = Symbol("x")

        fig, ax = plt.subplots(figsize=(10, 7), dpi=100)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#fafafa")

        x_vals = np.linspace(-10, 10, 1000)
        y_vals = np.array([float(expr.subs(x, xi).evalf()) if abs(float(expr.subs(x, xi).evalf())) < 1000 else np.nan for xi in x_vals])

        ax.plot(x_vals, y_vals, color="#2563eb", linewidth=2.5, label=f"$f(x) = {sympy.latex(expr)}$")

        if lower is not None and upper is not None:
            x_fill = np.linspace(lower, upper, 500)
            y_fill = np.array([float(expr.subs(x, xi).evalf()) for xi in x_fill])
            ax.fill_between(x_fill, y_fill, alpha=0.3, color="#2563eb", label=f"Area [{lower}, {upper}]")
            ax.axvline(x=lower, color="#16a34a", linewidth=1.5, linestyle="--", alpha=0.7)
            ax.axvline(x=upper, color="#16a34a", linewidth=1.5, linestyle="--", alpha=0.7)

        ax.axhline(y=0, color="#64748b", linewidth=0.8)
        ax.axvline(x=0, color="#64748b", linewidth=0.8)
        ax.grid(True, alpha=0.3, linestyle="--", color="#94a3b8")
        ax.set_xlabel("x", fontsize=14, color="#334155")
        ax.set_ylabel("y", fontsize=14, color="#334155")
        title = "Definite Integral" if lower is not None else "Function Plot"
        ax.set_title(title, fontsize=16, color="#1e293b", pad=15)
        ax.legend(fontsize=12, framealpha=0.9)
        ax.tick_params(colors="#475569", labelsize=11)
        for spine in ax.spines.values():
            spine.set_color("#cbd5e1")

        plt.tight_layout()

        if not filename:
            filename = f"integral_plot_{uuid.uuid4().hex[:8]}.png"
        filepath = GENERATED_DIR / filename
        fig.savefig(filepath, bbox_inches="tight", facecolor="#ffffff")
        plt.close(fig)
        return str(filepath)
    except Exception:
        plt.close("all")
        return None


def generate_geometry_diagram(shape: str, params: dict, filename: str = None) -> str:
    """Generate geometry diagrams."""
    try:
        fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#fafafa")
        ax.set_aspect("equal")

        if shape == "circle":
            r = params.get("radius", 3)
            circle = plt.Circle((0, 0), r, fill=False, color="#2563eb", linewidth=2.5)
            ax.add_patch(circle)
            ax.plot(0, 0, "o", color="#dc2626", markersize=6)
            ax.plot([0, r], [0, 0], color="#dc2626", linewidth=1.5, linestyle="--")
            ax.annotate(f"r = {r}", (r / 2, 0.2), fontsize=13, color="#dc2626", fontweight="bold")
            ax.set_xlim(-r - 1, r + 1)
            ax.set_ylim(-r - 1, r + 1)
            ax.set_title(f"Circle (r = {r})", fontsize=16, color="#1e293b", pad=15)

        elif shape == "triangle":
            a = params.get("a", 3)
            b = params.get("b", 4)
            c = params.get("c", 5)
            vertices = np.array([[0, 0], [a, 0], [0, b], [0, 0]])
            ax.plot(vertices[:, 0], vertices[:, 1], color="#2563eb", linewidth=2.5)
            ax.fill(vertices[:-1, 0], vertices[:-1, 1], alpha=0.1, color="#2563eb")
            ax.annotate(f"a = {a}", (a / 2, -0.3), fontsize=13, color="#334155", ha="center")
            ax.annotate(f"b = {b}", (-0.4, b / 2), fontsize=13, color="#334155", ha="center")
            margin = max(a, b) * 0.2
            ax.set_xlim(-margin, a + margin)
            ax.set_ylim(-margin, b + margin)
            ax.set_title("Triangle", fontsize=16, color="#1e293b", pad=15)

        elif shape == "rectangle":
            w = params.get("width", 6)
            h = params.get("height", 4)
            rect = patches.Rectangle((0, 0), w, h, fill=True, facecolor="#2563eb", alpha=0.1, edgecolor="#2563eb", linewidth=2.5)
            ax.add_patch(rect)
            ax.annotate(f"w = {w}", (w / 2, -0.3), fontsize=13, color="#334155", ha="center")
            ax.annotate(f"h = {h}", (-0.4, h / 2), fontsize=13, color="#334155", ha="center", rotation=90)
            ax.set_xlim(-1, w + 1)
            ax.set_ylim(-1, h + 1)
            ax.set_title(f"Rectangle ({w} × {h})", fontsize=16, color="#1e293b", pad=15)

        ax.grid(True, alpha=0.3, linestyle="--", color="#94a3b8")
        ax.tick_params(colors="#475569", labelsize=11)
        for spine in ax.spines.values():
            spine.set_color("#cbd5e1")
        plt.tight_layout()

        if not filename:
            filename = f"geom_{uuid.uuid4().hex[:8]}.png"
        filepath = GENERATED_DIR / filename
        fig.savefig(filepath, bbox_inches="tight", facecolor="#ffffff")
        plt.close(fig)
        return str(filepath)
    except Exception:
        plt.close("all")
        return None
