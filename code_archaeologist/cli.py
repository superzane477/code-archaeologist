"""
CLI entry point for Code Archaeologist
"""
import click
from pathlib import Path
from typing import Optional
import sys
from datetime import datetime
import os

from . import __version__
from .scanners import FileScanner, DependencyScanner, TechStackDetector
from .detectors import LanguageDetector
from .analyzers import PythonAnalyzer, JSAnalyzer, GenericAnalyzer
from .reporters import HTMLReporter
from .llm import LLMClient, PromptBuilder
from .utils.config import Config


def calculate_health_score(data: dict) -> tuple[int, str]:
    """Calculate overall health score based on all metrics"""
    score = 100
    
    vuln_count = len(data.get("vulnerabilities", []))
    score -= vuln_count * 5
    
    complexity = data.get("complexity", {})
    high_complexity = sum(1 for c in complexity.values() 
                         if isinstance(c, dict) and c.get("complexity", 0) > 20)
    score -= high_complexity * 2
    
    dead_code_count = len(data.get("dead_code", []))
    score -= dead_code_count * 1
    
    security_count = len(data.get("security_issues", []))
    score -= security_count * 3
    
    score = max(0, min(100, score))
    
    if score >= 80:
        summary = "Project health is good with low technical debt."
    elif score >= 60:
        summary = "Project has some technical debt that needs attention."
    elif score >= 40:
        summary = "Project has significant technical debt. Prioritize critical issues."
    else:
        summary = "Project has severe technical debt requiring major refactoring."
    
    return score, summary


def calculate_complexity_distribution(complexity_data: dict) -> list:
    """Calculate complexity distribution for chart"""
    distribution = [0, 0, 0, 0, 0]
    
    for item in complexity_data.values():
        if isinstance(item, dict):
            rank = item.get("rank", "C")
            if rank == "A":
                distribution[0] += 1
            elif rank == "B":
                distribution[1] += 1
            elif rank == "C":
                distribution[2] += 1
            elif rank == "D":
                distribution[3] += 1
            else:
                distribution[4] += 1
    
    return distribution


def calculate_issue_breakdown(data: dict) -> list:
    """Calculate issue breakdown for chart [security, dead_code, complexity, other]"""
    security = len(data.get("security_issues", []))
    dead_code = len(data.get("dead_code", []))
    complexity = len(data.get("complexity", {}))
    vulnerabilities = len(data.get("vulnerabilities", []))
    
    return [security, dead_code, complexity, vulnerabilities]


def build_heatmap_data(file_stats: dict, complexity: dict, dead_code: list, security: list) -> list:
    """Build heatmap data showing problem density per file"""
    file_scores = {}
    
    for key, data in complexity.items():
        if isinstance(data, dict):
            file_name = key.split(":")[0] if ":" in key else key
            score = data.get("complexity", 0)
            if file_name not in file_scores:
                file_scores[file_name] = {"score": 0, "issues": 0}
            file_scores[file_name]["score"] += score * 2
            file_scores[file_name]["issues"] += 1
    
    for item in dead_code:
        file_name = item.get("file", "unknown") if isinstance(item, dict) else "unknown"
        if file_name not in file_scores:
            file_scores[file_name] = {"score": 0, "issues": 0}
        file_scores[file_name]["score"] += 5
        file_scores[file_name]["issues"] += 1
    
    for item in security:
        file_name = item.get("file", "unknown") if isinstance(item, dict) else "unknown"
        if file_name not in file_scores:
            file_scores[file_name] = {"score": 0, "issues": 0}
        file_scores[file_name]["score"] += 15
        file_scores[file_name]["issues"] += 1
    
    max_score = max([s["score"] for s in file_scores.values()]) if file_scores else 1
    
    heatmap = []
    for path, data in file_scores.items():
        normalized = int((data["score"] / max_score) * 100) if max_score > 0 else 0
        severity = "high" if normalized > 70 else "medium" if normalized > 40 else "low"
        heatmap.append({
            "path": path,
            "score": normalized,
            "severity": severity,
            "issue_count": data["issues"]
        })
    
    heatmap.sort(key=lambda x: x["score"], reverse=True)
    return heatmap


@click.command()
@click.argument("project_path", type=click.Path(exists=True))
@click.option("-o", "--output", "output_path", type=click.Path(), 
              default=None, help="Output report path (default: ./<project>-analysis-<timestamp>.html)")
@click.option("--llm-backend", type=click.Choice(["openai", "ollama", "groq", "deepseek", "azure"]),
              default=None, help="LLM backend to use")
@click.option("--llm-api-key", "llm_api_key", type=str, default=None, help="API key for LLM")
@click.option("--llm-model", "llm_model", type=str, default=None, help="Model name")
@click.option("--no-llm", "no_llm", is_flag=True, default=False, help="Skip LLM analysis")
@click.option("--exclude", type=str, default=None, help="Comma-separated directories to exclude")
@click.option("--config", "config_path", type=click.Path(exists=True), default=None, help="Config file path")
@click.option("-v", "--verbose", is_flag=True, default=False, help="Verbose output")
def main(project_path: str, output_path: Optional[str], llm_backend: Optional[str], 
         llm_api_key: Optional[str], llm_model: Optional[str], no_llm: bool,
         exclude: Optional[str], config_path: Optional[str], verbose: bool):
    """
    Code Archaeologist - Analyze legacy codebases and generate health reports.
    
    PROJECT_PATH: Path to the project to analyze
    """
    project = Path(project_path).resolve()
    
    if verbose:
        click.echo(f"Scanning project: {project}")
    
    config = Config(Path(config_path) if config_path else None)
    
    exclude_patterns = exclude.split(",") if exclude else config.exclude_patterns
    
    analysis_data = {
        "project_name": project.name,
        "path": str(project)
    }
    
    if verbose:
        click.echo("Detecting languages...")
    detector = LanguageDetector(project, exclude_patterns)
    lang_result = detector.detect()
    analysis_data.update(lang_result)
    
    if verbose:
        click.echo(f"   Found {len(lang_result.get('languages', []))} languages")
    
    if verbose:
        click.echo("Scanning files...")
    scanner = FileScanner(project, exclude_patterns)
    file_stats = scanner.scan()
    analysis_data.update({
        "total_lines": file_stats.get("total_lines", 0),
        "file_count": file_stats.get("total_files", 0),
        "file_types": file_stats.get("file_types", {})
    })
    
    if verbose:
        click.echo("Detecting tech stack...")
    tech_detector = TechStackDetector(project)
    tech_result = tech_detector.detect()
    analysis_data.update({
        "frameworks": tech_result.get("frameworks", []),
        "libraries": tech_result.get("libraries", []),
        "tech_era": tech_result.get("era", "unknown"),
        "architecture": tech_result.get("architecture_patterns", []),
        "tech_generation": tech_result.get("tech_generation", "unknown")
    })
    
    if verbose:
        click.echo("Scanning dependencies...")
    dep_scanner = DependencyScanner(project)
    dep_result = dep_scanner.scan()
    analysis_data.update({
        "dependencies": dep_result,
        "vulnerabilities": dep_result.get("vulnerabilities", []),
        "dependency_count": len(dep_result.get("dependencies", []))
    })
    
    if verbose:
        click.echo("Analyzing code...")
    
    all_files = list(project.rglob("*"))
    all_files = [f for f in all_files if f.is_file() and not any(excl in str(f) for excl in exclude_patterns)]
    
    python_analyzer = PythonAnalyzer(project)
    js_analyzer = JSAnalyzer(project)
    
    py_files = [f for f in all_files if f.suffix == ".py"]
    if py_files:
        py_results = python_analyzer.analyze(py_files)
        analysis_data["complexity"] = py_results.get("complexity", {})
        analysis_data["dead_code"] = py_results.get("dead_code", [])
        analysis_data["security_issues"] = py_results.get("security_issues", [])
    
    js_files = [f for f in all_files if f.suffix in [".js", ".jsx", ".ts", ".tsx"]]
    if js_files:
        js_results = js_analyzer.analyze(js_files)
        existing_issues = analysis_data.get("security_issues", [])
        existing_issues.extend(js_results.get("issues", []))
        analysis_data["security_issues"] = existing_issues
    
    analysis_data["complexity_distribution"] = calculate_complexity_distribution(
        analysis_data.get("complexity", {})
    )
    analysis_data["issue_breakdown"] = calculate_issue_breakdown(analysis_data)
    analysis_data["high_complexity_count"] = sum(
        1 for c in analysis_data.get("complexity", {}).values()
        if isinstance(c, dict) and c.get("complexity", 0) > 20
    )
    
    analysis_data["heatmap"] = build_heatmap_data(
        file_stats,
        analysis_data.get("complexity", {}),
        analysis_data.get("dead_code", []),
        analysis_data.get("security_issues", [])
    )
    
    health_score, health_summary = calculate_health_score(analysis_data)
    analysis_data["health_score"] = health_score
    analysis_data["health_summary"] = health_summary
    analysis_data["vuln_count"] = len(analysis_data.get("vulnerabilities", []))
    analysis_data["outdated_count"] = len(dep_result.get("outdated", []))
    analysis_data["total_deps"] = len(dep_result.get("dependencies", []))
    analysis_data["issue_count"] = (
        len(analysis_data.get("dead_code", [])) +
        len(analysis_data.get("security_issues", [])) +
        analysis_data["high_complexity_count"]
    )
    
    if not no_llm:
        if verbose:
            click.echo("Generating AI analysis...")
        
        llm_config = config.llm_config.copy()
        if llm_backend:
            llm_config["backend"] = llm_backend
        if llm_api_key:
            llm_config["api_key"] = llm_api_key
        if llm_model:
            llm_config["model"] = llm_model
        
        try:
            llm_client = LLMClient(llm_config)
            validation = llm_client.validate_config()
            
            if validation["valid"]:
                prompt = PromptBuilder.build_analysis_prompt(analysis_data)
                system_prompt = PromptBuilder.SYSTEM_PROMPT
                llm_report = llm_client.generate_report(prompt, system_prompt)
                analysis_data["llm_report"] = llm_report
                
                if verbose:
                    click.echo("   LLM report generated successfully")
            else:
                if verbose:
                    click.echo(f"   LLM config invalid: {validation['errors']}")
        except Exception as e:
            if verbose:
                click.echo(f"   LLM error (continuing without): {str(e)}")
    
    if verbose:
        click.echo("Generating HTML report...")
    
    output = Path(output_path) if output_path else Path(f"./{project.name}-analysis-{datetime.now():%Y%m%d-%H%M%S}.html")
    reporter = HTMLReporter()
    reporter.generate(analysis_data, output)
    
    if verbose:
        click.echo(f"   Report saved to: {output}")
    
    click.echo("\nAnalysis complete!")
    click.echo(f"   Project: {project.name}")
    click.echo(f"   Health Score: {health_score}/100")
    click.echo(f"   Report: {output.absolute()}")


if __name__ == "__main__":
    main()