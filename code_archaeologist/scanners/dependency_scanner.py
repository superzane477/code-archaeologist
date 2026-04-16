"""
Dependency scanner for analyzing project dependencies
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import json
import re


class DependencyScanner:
    """Scans and analyzes project dependencies"""
    
    DEPENDENCY_FILES = {
        "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "setup.cfg"],
        "javascript": ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
        "go": ["go.mod", "go.sum"],
        "java": ["pom.xml", "build.gradle", "gradle.properties"],
        "rust": ["Cargo.toml", "Cargo.lock"],
        "ruby": ["Gemfile", "Gemfile.lock"],
        "php": ["composer.json", "composer.lock"]
    }
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def scan(self) -> Dict[str, Any]:
        """
        Scan for dependencies and check for issues.
        
        Returns:
            Dictionary with dependency information and vulnerabilities
        """
        results = {
            "dependencies": [],
            "outdated": [],
            "vulnerabilities": [],
            "unsupported": []
        }
        
        project_type = self._detect_project_type()
        
        if project_type == "python":
            self._scan_python(results)
        elif project_type == "javascript":
            self._scan_javascript(results)
        elif project_type == "go":
            self._scan_go(results)
        else:
            results["unsupported"].append({
                "type": project_type,
                "message": "Dependency scanning not yet supported for this language"
            })
        
        return results
    
    def _detect_project_type(self) -> str:
        """Detect the primary language/framework of the project"""
        for lang, files in self.DEPENDENCY_FILES.items():
            for filename in files:
                if (self.project_path / filename).exists():
                    return lang
        return "unknown"
    
    def _scan_python(self, results: Dict):
        """Scan Python dependencies"""
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        results["dependencies"].append({
                            "name": line.split('==')[0] if '==' in line else line,
                            "version": line.split('==')[1] if '==' in line else "latest",
                            "source": "requirements.txt"
                        })
        
        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            try:
                with open(pyproject, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    in_deps = False
                    for line in content.split('\n'):
                        if line.strip().startswith('dependencies'):
                            in_deps = True
                        elif in_deps and line.strip().startswith(']'):
                            in_deps = False
                        elif in_deps and '=' in line:
                            name = line.split('=')[0].strip()
                            version = line.split('=')[1].strip().strip('"')
                            results["dependencies"].append({
                                "name": name,
                                "version": version,
                                "source": "pyproject.toml"
                            })
            except Exception:
                pass
        
        self._check_python_vulnerabilities(results)
    
    def _check_python_vulnerabilities(self, results: Dict):
        """Check for known vulnerabilities in Python packages"""
        try:
            result = subprocess.run(
                ["safety", "check", "--json", "--output=raw"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.project_path)
            )
            
            if result.stdout:
                try:
                    vuln_data = json.loads(result.stdout)
                    for item in vuln_data:
                        results["vulnerabilities"].append({
                            "package": item.get("package", ""),
                            "installed_version": item.get("installed_version", ""),
                            "vulnerability_id": item.get("vulnerability_id", ""),
                            "severity": item.get("severity", "UNKNOWN"),
                            "description": item.get("description", "")
                        })
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            self._check_python_vulnerabilities_pip_audit(results)
        except Exception:
            pass
    
    def _check_python_vulnerabilities_pip_audit(self, results: Dict):
        """Fallback to pip-audit for vulnerability checking"""
        try:
            result = subprocess.run(
                ["pip-audit", "--json"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.project_path)
            )
            
            if result.returncode == 0 and result.stdout:
                try:
                    vuln_data = json.loads(result.stdout)
                    for item in vuln_data:
                        results["vulnerabilities"].append({
                            "package": item.get("name", ""),
                            "installed_version": item.get("version", ""),
                            "vulnerability_id": item.get("id", ""),
                            "severity": "HIGH",
                            "description": item.get("description", "")
                        })
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            pass
        except Exception:
            pass
    
    def _scan_javascript(self, results: Dict):
        """Scan JavaScript/Node.js dependencies"""
        pkg_file = self.project_path / "package.json"
        
        if pkg_file.exists():
            try:
                with open(pkg_file, 'r', encoding='utf-8') as f:
                    pkg_data = json.load(f)
                
                deps = pkg_data.get("dependencies", {})
                dev_deps = pkg_data.get("devDependencies", {})
                
                for name, version in deps.items():
                    results["dependencies"].append({
                        "name": name,
                        "version": version,
                        "type": "production"
                    })
                
                for name, version in dev_deps.items():
                    results["dependencies"].append({
                        "name": name,
                        "version": version,
                        "type": "development"
                    })
            except Exception:
                pass
        
        self._check_npm_vulnerabilities(results)
    
    def _check_npm_vulnerabilities(self, results: Dict):
        """Check for npm package vulnerabilities"""
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.project_path)
            )
            
            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get("vulnerabilities", {})
                    
                    for name, info in vulnerabilities.items():
                        results["vulnerabilities"].append({
                            "package": name,
                            "installed_version": info.get("version", ""),
                            "severity": info.get("severity", "UNKNOWN"),
                            "vulnerability_id": info.get("via", [{}])[0].get("id", "") if info.get("via") else "",
                            "description": info.get("title", "")
                        })
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            pass
        except Exception:
            pass
    
    def _scan_go(self, results: Dict):
        """Scan Go module dependencies"""
        go_mod = self.project_path / "go.mod"
        
        if go_mod.exists():
            try:
                with open(go_mod, 'r', encoding='utf-8', errors='ignore') as f:
                    in_require = False
                    for line in f:
                        line = line.strip()
                        
                        if line.startswith("require ("):
                            in_require = True
                        elif line.startswith(")"):
                            in_require = False
                        elif in_require and "=>" not in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                results["dependencies"].append({
                                    "name": parts[0],
                                    "version": parts[1],
                                    "source": "go.mod"
                                })
                        elif line.startswith("require ") and "=>" not in line:
                            parts = line.split()[1:]
                            if len(parts) >= 2:
                                results["dependencies"].append({
                                    "name": parts[0],
                                    "version": parts[1],
                                    "source": "go.mod"
                                })
            except Exception:
                pass
        
        self._check_go_vulnerabilities(results)
    
    def _check_go_vulnerabilities(self, results: Dict):
        """Check for known vulnerabilities in Go packages"""
        try:
            result = subprocess.run(
                ["govulncheck", "-json", "./..."],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.project_path)
            )
            
            if result.stdout:
                try:
                    vuln_data = json.loads(result.stdout)
                    for item in vuln_data.get("vulnerabilities", []):
                        results["vulnerabilities"].append({
                            "package": item.get("package", ""),
                            "severity": item.get("severity", "UNKNOWN"),
                            "description": item.get("description", "")
                        })
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            pass
        except Exception:
            pass