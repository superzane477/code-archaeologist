"""
JavaScript/TypeScript analyzer using ESLint
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import json
import tempfile
import os

from .base import BaseAnalyzer


class JSAnalyzer(BaseAnalyzer):
    """Analyzer for JavaScript and TypeScript using ESLint"""
    
    def get_language(self) -> str:
        return "javascript"
    
    def get_file_extensions(self) -> List[str]:
        return [".js", ".jsx", ".mjs", ".ts", ".tsx"]
    
    def analyze(self, files: List[Path]) -> Dict[str, Any]:
        """Run ESLint analysis on JavaScript/TypeScript files"""
        results = {
            "issues": [],
            "metrics": {
                "total_lines": 0,
                "files_analyzed": 0
            }
        }
        
        js_files = [f for f in files if f.suffix in self.get_file_extensions()]
        
        if not js_files:
            return results
        
        eslint_issues = self._run_eslint(js_files)
        results["issues"] = eslint_issues
        
        for js_file in js_files:
            try:
                with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    results["metrics"]["total_lines"] += lines
                    results["metrics"]["files_analyzed"] += 1
            except Exception:
                pass
        
        return results
    
    def _run_eslint(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Run ESLint on the given files"""
        issues = []
        
        config = {
            "rules": {
                "complexity": ["warn", {"max": 10}],
                "no-unused-vars": "warn",
                "no-undef": "error",
                "no-console": "off"
            },
            "env": {
                "browser": True,
                "es6": True,
                "node": True
            },
            "parserOptions": {
                "ecmaVersion": 2020,
                "sourceType": "module"
            }
        }
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(config, f)
                config_path = f.name
            
            file_paths = [str(f) for f in files]
            result = subprocess.run(
                ["npx", "eslint", "--no-eslintrc", "-c", config_path, "--format", "json"] + file_paths,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.project_path)
            )
            
            if result.stdout:
                try:
                    eslint_data = json.loads(result.stdout)
                    for file_result in eslint_data:
                        file_path = file_result.get("filePath", "")
                        for msg in file_result.get("messages", []):
                            issues.append({
                                "file": os.path.basename(file_path),
                                "line": msg.get("line", 0),
                                "column": msg.get("column", 0),
                                "severity": "warning" if msg.get("severity") == 1 else "error",
                                "rule_id": msg.get("ruleId", ""),
                                "message": msg.get("message", "")
                            })
                except json.JSONDecodeError:
                    pass
                    
        except FileNotFoundError:
            pass
        except Exception:
            pass
        finally:
            try:
                os.unlink(config_path)
            except Exception:
                pass
        
        return issues