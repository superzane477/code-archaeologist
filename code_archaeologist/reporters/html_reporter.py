"""
HTML report generator
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


class HTMLReporter:
    """Generates HTML reports from analysis results"""
    
    LANGUAGE_COLORS = {
        "python": "#3572A5",
        "javascript": "#f1e05a",
        "typescript": "#2b7489",
        "go": "#00ADD8",
        "java": "#b07219",
        "ruby": "#701516",
        "rust": "#dea584",
        "php": "#4F5D95",
        "c": "#555555",
        "cpp": "#f34b7d",
        "generic": "#8b949e"
    }
    
    COMPLEXITY_COLORS = {
        "A": "#3fb950",
        "B": "#58a6ff",
        "C": "#d29922",
        "D": "#f85149",
        "F": "#f85149"
    }
    
    def __init__(self, template_path: Optional[Path] = None):
        if template_path is None:
            template_path = Path(__file__).parent.parent.parent / "templates"
        
        self.template_path = template_path
        self.env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.env.filters['format_number'] = format_number
    
    def generate(self, data: Dict[str, Any], output_path: Path) -> None:
        """
        Generate HTML report from analysis data.
        
        Args:
            data: Analysis results dictionary
            output_path: Path where the HTML file will be saved
        """
        context = self._prepare_context(data)
        
        template = self.env.get_template("base.html")
        html_content = template.render(**context)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _prepare_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare template context from analysis data"""
        context = {
            "title": f"{data.get('project_name', 'Project')} - Code Archaeology Report",
            "project_name": data.get("project_name", "Unknown Project"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "health_score": data.get("health_score", 50),
            "health_summary": data.get("health_summary", "Analyzing..."),
            "total_lines": data.get("total_lines", 0),
            "file_count": data.get("file_count", 0),
            "dependency_count": data.get("dependency_count", 0),
            "issue_count": data.get("issue_count", 0),
            "languages": self._prepare_languages(data.get("languages", [])),
            "frameworks": data.get("frameworks", []),
            "libraries": data.get("libraries", [])[:20],
            "tech_era": data.get("tech_era", "unknown"),
            "architecture": ", ".join(data.get("architecture", [])) or "unknown",
            "tech_generation": data.get("tech_generation", "unknown"),
            "complexity_issues": self._prepare_complexity(data.get("complexity", {})),
            "dead_code_issues": self._prepare_dead_code(data.get("dead_code", [])),
            "security_issues": self._prepare_security(data.get("security_issues", [])),
            "vulnerabilities": data.get("vulnerabilities", []),
            "heatmap_data": data.get("heatmap", []),
            "llm_report": data.get("llm_report", ""),
            "total_deps": data.get("total_deps", 0),
            "vuln_count": data.get("vuln_count", 0),
            "outdated_count": data.get("outdated_count", 0),
            "complexity_labels": ["A (1-5)", "B (6-10)", "C (11-20)", "D (21-30)", "F (31+)"],
            "complexity_data": data.get("complexity_distribution", [0, 0, 0, 0, 0]),
            "issue_data": data.get("issue_breakdown", [0, 0, 0, 0])
        }
        
        if context["health_score"] >= 70:
            context["score_class"] = "score-high"
        elif context["health_score"] >= 40:
            context["score_class"] = "score-medium"
        else:
            context["score_class"] = "score-low"
        
        context["health_tags"] = self._prepare_health_tags(data)
        
        return context
    
    def _prepare_languages(self, languages: List[Dict]) -> List[Dict]:
        """Prepare language data with colors"""
        for lang in languages:
            lang_name = lang.get("name", "unknown")
            lang["color"] = self.LANGUAGE_COLORS.get(lang_name.lower(), "#8b949e")
        return languages
    
    def _prepare_complexity(self, complexity: Dict[str, Any]) -> List[Dict]:
        """Prepare complexity issues for display"""
        issues = []
        for key, data in complexity.items():
            if isinstance(data, dict):
                parts = key.rsplit(":", 1) if ":" in key else [key, ""]
                rank = data.get("rank", "C")
                issues.append({
                    "file": parts[0],
                    "function": parts[1] if len(parts) > 1 else "unknown",
                    "complexity": data.get("complexity", 0),
                    "rank": rank,
                    "rank_color": self.COMPLEXITY_COLORS.get(rank, "yellow").replace("#", "")
                })
        
        issues.sort(key=lambda x: x["complexity"], reverse=True)
        return issues[:20]
    
    def _prepare_dead_code(self, dead_code: List[Dict]) -> List[Dict]:
        """Prepare dead code issues for display"""
        issues = []
        for item in dead_code:
            issues.append({
                "file": item.get("file", "unknown"),
                "line": item.get("line", 0),
                "type": item.get("type", "unknown"),
                "message": item.get("message", "")
            })
        return issues[:20]
    
    def _prepare_security(self, security: List[Dict]) -> List[Dict]:
        """Prepare security issues for display"""
        issues = []
        for item in security:
            severity = item.get("severity", "LOW")
            color_map = {
                "HIGH": "red",
                "MEDIUM": "yellow",
                "LOW": "green"
            }
            issues.append({
                "file": item.get("file", "unknown"),
                "line": item.get("line", 0),
                "severity": severity,
                "severity_color": color_map.get(severity.upper(), "yellow"),
                "message": item.get("message", item.get("description", ""))
            })
        return issues[:20]
    
    def _prepare_health_tags(self, data: Dict[str, Any]) -> List[Dict]:
        """Prepare health status tags"""
        tags = []
        
        era = data.get("tech_era", "unknown")
        if era == "classic":
            tags.append({"label": "Legacy", "color": "red"})
        elif era == "modern":
            tags.append({"label": "Modern", "color": "green"})
        else:
            tags.append({"label": "Mixed", "color": "yellow"})
        
        vuln_count = data.get("vuln_count", 0)
        if vuln_count > 5:
            tags.append({"label": f"{vuln_count} Vulnerabilities", "color": "red"})
        elif vuln_count > 0:
            tags.append({"label": f"{vuln_count} Vulnerabilities", "color": "yellow"})
        
        high_complexity = data.get("high_complexity_count", 0)
        if high_complexity > 10:
            tags.append({"label": f"{high_complexity} Complex Functions", "color": "yellow"})
        
        return tags


def format_number(num: int) -> str:
    """Format number with K/M suffix"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)