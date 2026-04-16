"""
Generic analyzer for unsupported or unknown languages
"""
from pathlib import Path
from typing import Dict, List, Any, Optional

from .base import BaseAnalyzer


class GenericAnalyzer(BaseAnalyzer):
    """Fallback analyzer for languages without specific support"""
    
    def get_language(self) -> str:
        return "generic"
    
    def get_file_extensions(self) -> List[str]:
        return []
    
    def analyze(self, files: List[Path]) -> Dict[str, Any]:
        """Basic analysis for any file type"""
        results = {
            "metrics": {
                "total_lines": 0,
                "files_analyzed": 0,
                "comment_lines": 0
            },
            "files": []
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    line_count = len(lines)
                    
                    comment_count = 0
                    for line in lines:
                        stripped = line.strip()
                        if stripped.startswith('#') or stripped.startswith('//'):
                            comment_count += 1
                    
                    results["metrics"]["total_lines"] += line_count
                    results["metrics"]["comment_lines"] += comment_count
                    results["metrics"]["files_analyzed"] += 1
                    
                    results["files"].append({
                        "name": file_path.name,
                        "path": str(file_path.relative_to(self.project_path)),
                        "lines": line_count,
                        "comments": comment_count
                    })
            except Exception:
                pass
        
        return results