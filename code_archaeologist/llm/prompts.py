"""
Prompt templates for LLM analysis
"""
from typing import Dict, Any, List


class PromptBuilder:
    """Builds prompts for code archaeology analysis"""
    
    SYSTEM_PROMPT = """You are a senior code archaeologist specializing in analyzing legacy codebases for technical debt and health. You have 20 years of programming experience and are proficient in multiple programming languages and architecture patterns. Your analysis is fact-based, concise, and sometimes humorous but direct.

Please analyze the provided data and generate a structured report."""
    
    @classmethod
    def build_analysis_prompt(cls, project_data: Dict[str, Any]) -> str:
        """
        Build the main analysis prompt from project data.
        
        Args:
            project_data: Dictionary containing project analysis results
            
        Returns:
            Formatted prompt string
        """
        project_name = project_data.get("name", "Unknown Project")
        primary_lang = project_data.get("primary_language", "unknown")
        total_lines = project_data.get("total_lines", 0)
        file_count = project_data.get("file_count", 0)
        languages = project_data.get("languages", [])
        
        tech_stack = project_data.get("tech_stack", {})
        frameworks = tech_stack.get("frameworks", [])
        libraries = tech_stack.get("libraries", [])
        era = tech_stack.get("era", "unknown")
        architecture = tech_stack.get("architecture_patterns", [])
        
        code_health = project_data.get("code_health", {})
        complexity = code_health.get("complexity", {})
        dead_code = code_health.get("dead_code", [])
        security = code_health.get("security_issues", [])
        
        dependencies = project_data.get("dependencies", {})
        dep_list = dependencies.get("dependencies", [])
        vulns = dependencies.get("vulnerabilities", [])
        
        avg_complexity = 0
        if complexity:
            complexities = [c.get("complexity", 0) for c in complexity.values() if isinstance(c, dict)]
            if complexities:
                avg_complexity = sum(complexities) / len(complexities)
        
        dead_code_count = len(dead_code) if isinstance(dead_code, list) else 0
        security_count = len(security) if isinstance(security, list) else 0
        vuln_count = len(vulns) if isinstance(vulns, list) else 0
        
        prompt = f"""## Project Basic Information

- **Project Name**: {project_name}
- **Primary Language**: {primary_lang}
- **Total Lines of Code**: {total_lines:,}
- **File Count**: {file_count:,}
- **Language Distribution**: {", ".join([f"{l['name']} ({l['percentage']}%)" for l in languages[:5]])}

## Tech Stack

- **Frameworks**: {", ".join([f.get("name", "") for f in frameworks]) or "None detected"}
- **Core Libraries**: {", ".join([l.get("name", "") for l in libraries[:10]]) or "None detected"}
- **Era**: {era}
- **Architecture Patterns**: {", ".join(architecture) or "None detected"}

## Code Health Metrics

- **Average Cyclomatic Complexity**: {avg_complexity:.1f}
- **Dead Code Count**: {dead_code_count} locations
- **Security Issues**: {security_count} issues
- **Dependency Vulnerabilities**: {vuln_count} items

## Dependencies ({len(dep_list)} total)

{", ".join([f"{d.get('name', 'unknown')}@{d.get('version', 'latest')}" for d in dep_list[:15]])}

{len(dep_list) > 15 and f"... and {len(dep_list) - 15} more dependencies" or ""}

## Please Generate the Following Analysis Report

1. **Technical Debt Summary** (3-5 sentences, humorous but direct about project status)

2. **Refactoring Priority List** (top 5 modules/files needing refactoring with descriptions)

3. **Migration Path Suggestions** (if tech stack is outdated, provide steps to modernize)

4. **Risk Assessment** (High/Medium/Low with specific descriptions)
   - Security risks
   - Architecture risks
   - Dependency obsolescence risks

5. **Quick Fix清单** (3-5 improvements that can be done immediately without major refactoring)

Please respond in English, format clearly for readability."""
        
        return prompt
    
    @classmethod
    def build_summary_prompt(cls, project_data: Dict[str, Any]) -> str:
        """Build a shorter summary prompt for quick overviews"""
        project_name = project_data.get("name", "Unknown Project")
        health_score = project_data.get("health_score", 50)
        tech_debt = project_data.get("tech_debt_level", "medium")
        
        return f"""Project "{project_name}" has a technical health score of {health_score}/100 with {tech_debt} technical debt level.

Please summarize the most critical finding in one sentence and give the most important recommendation."""
    
    @classmethod
    def build_heatmap_prompt(cls, file_scores: List[Dict[str, Any]]) -> str:
        """Build prompt for heatmap analysis"""
        top_files = file_scores[:10]
        
        file_list = "\n".join([
            f"- {f.get('path', 'unknown')}: Score {f.get('score', 0)}, Issues {f.get('issue_count', 0)}"
            for f in top_files
        ])
        
        return f"""Based on the following file problem density analysis:

{file_list}

Please explain why these files have the most problems and provide specific recommendations."""