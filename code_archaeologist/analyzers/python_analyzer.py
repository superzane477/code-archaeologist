"""
Python code analyzer using radon, vulture, and bandit
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import json
import re

from .base import BaseAnalyzer, AnalysisResult


class PythonAnalyzer(BaseAnalyzer):
    """Analyzer for Python code using static analysis tools"""
    
    def get_language(self) -> str:
        return "python"
    
    def get_file_extensions(self) -> List[str]:
        return [".py"]
    
    def analyze(self, files: List[Path]) -> Dict[str, Any]:
        """Run Python-specific analysis tools"""
        results = {
            "complexity": {},
            "dead_code": [],
            "security_issues": [],
            "metrics": {
                "total_lines": 0,
                "files_analyzed": 0
            }
        }
        
        py_files = [f for f in files if f.suffix == ".py"]
        
        if not py_files:
            return results
        
        # Analyze complexity using radon
        complexity_results = self._analyze_complexity(py_files)
        results["complexity"] = complexity_results
        
        # Detect dead code using vulture
        dead_code_results = self._analyze_dead_code(py_files)
        results["dead_code"] = dead_code_results
        
        # Security scan using bandit
        security_results = self._analyze_security(py_files)
        results["security_issues"] = security_results
        
        # Calculate total lines
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    results["metrics"]["total_lines"] += lines
                    results["metrics"]["files_analyzed"] += 1
            except Exception:
                pass
        
        return results
    
    def _analyze_complexity(self, files: List[Path]) -> Dict[str, Any]:
        """Analyze cyclomatic complexity using radon"""
        complexity = {}
        
        try:
            for py_file in files:
                result = subprocess.run(
                    ["radon", "cc", "-j", str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    try:
                        cc_data = json.loads(result.stdout)
                        for func in cc_data:
                            name = f"{py_file.name}:{func.get('name', 'unknown')}"
                            complexity[name] = {
                                "complexity": func.get('complexity', 0),
                                "rank": self.calculate_complexity_rank(func.get('complexity', 0))
                            }
                    except json.JSONDecodeError:
                        pass
        except FileNotFoundError:
            pass
        except Exception:
            pass
        
        return complexity
    
    def _analyze_dead_code(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Detect unused code using vulture"""
        dead_code = []
        
        try:
            file_paths = [str(f) for f in files]
            result = subprocess.run(
                ["vulture", "--json"] + file_paths,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.project_path)
            )
            
            if result.returncode == 0:
                try:
                    vulture_data = json.loads(result.stdout)
                    for item in vulture_data:
                        dead_code.append({
                            "file": item.get('line', 0),
                            "line": item.get('line', 0),
                            "message": item.get('message', ''),
                            "type": item.get('type', 'unknown')
                        })
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            pass
        except Exception:
            pass
        
        return dead_code
    
    def _analyze_security(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Scan for security issues using bandit"""
        security_issues = []
        
        try:
            result = subprocess.run(
                ["bandit", "-r", "-j", str(self.project_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode in [0, 1]:
                try:
                    bandit_data = json.loads(result.stdout)
                    for issue in bandit_data.get("results", []):
                        security_issues.append({
                            "file": issue.get("filename", ""),
                            "line": issue.get("line", 0),
                            "severity": issue.get("issue_severity", "LOW"),
                            "confidence": issue.get("issue_confidence", "LOW"),
                            "message": issue.get("issue_text", ""),
                            "test_id": issue.get("test_id", "")
                        })
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            pass
        except Exception:
            pass
        
        return security_issues