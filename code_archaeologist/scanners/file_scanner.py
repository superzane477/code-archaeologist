"""
File scanner for analyzing project structure and code statistics
"""
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict
import os


class FileScanner:
    """Scans project files and collects statistics"""
    
    DEFAULT_EXCLUDES = [
        ".git", ".svn", ".hg",
        "node_modules", "bower_components",
        "__pycache__", ".pytest_cache", ".mypy_cache",
        ".venv", "venv", "env", ".env",
        "dist", "build", "out", "target",
        ".idea", ".vscode", ".vs",
        "*.pyc", "*.pyo", "*.so", "*.dylib",
        ".DS_Store", "Thumbs.db",
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "vendor", "packages"
    ]
    
    def __init__(self, project_path: Path, exclude_patterns: List[str] = None):
        self.project_path = project_path
        self.exclude_patterns = exclude_patterns or self.DEFAULT_EXCLUDES
        self.files: List[Path] = []
        self.file_tree: Dict[str, Any] = {}
    
    def scan(self) -> Dict[str, Any]:
        """
        Scan the project and return statistics.
        
        Returns:
            Dictionary with file statistics, structure, and metrics
        """
        self.files = self._scan_files()
        
        return {
            "total_files": len(self.files),
            "total_lines": self._count_total_lines(),
            "file_types": self._count_by_extension(),
            "largest_files": self._get_largest_files(10),
            "structure": self._build_file_tree(),
            "directory_sizes": self._get_directory_sizes()
        }
    
    def _scan_files(self) -> List[Path]:
        """Recursively scan for files, excluding patterns"""
        files = []
        
        for root, dirs, filenames in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._is_excluded(d)]
            
            root_path = Path(root)
            for filename in filenames:
                file_path = root_path / filename
                if not self._is_excluded(str(file_path)):
                    files.append(file_path)
        
        return files
    
    def _is_excluded(self, path_str: str) -> bool:
        """Check if a path should be excluded"""
        path_str = path_str.replace("\\", "/")
        
        for pattern in self.exclude_patterns:
            if pattern.startswith("*"):
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True
            
            parts = path_str.split("/")
            if pattern in parts:
                return True
        
        return False
    
    def _count_total_lines(self) -> int:
        """Count total lines of code"""
        total = 0
        for file_path in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    total += len(f.readlines())
            except Exception:
                pass
        return total
    
    def _count_by_extension(self) -> Dict[str, int]:
        """Count files and lines by extension"""
        stats = defaultdict(lambda: {"files": 0, "lines": 0})
        
        for file_path in self.files:
            ext = file_path.suffix.lower() or "no_extension"
            stats[ext]["files"] += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    stats[ext]["lines"] += len(f.readlines())
            except Exception:
                pass
        
        return dict(stats)
    
    def _get_largest_files(self, count: int) -> List[Dict[str, Any]]:
        """Get the largest files by line count"""
        file_sizes = []
        
        for file_path in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    file_sizes.append({
                        "path": str(file_path.relative_to(self.project_path)),
                        "lines": lines
                    })
            except Exception:
                pass
        
        file_sizes.sort(key=lambda x: x["lines"], reverse=True)
        return file_sizes[:count]
    
    def _build_file_tree(self) -> Dict[str, Any]:
        """Build a tree representation of the project structure"""
        tree = {"name": self.project_path.name, "type": "directory", "children": []}
        
        by_dir = defaultdict(list)
        for file_path in self.files:
            rel_path = file_path.relative_to(self.project_path)
            parts = rel_path.parts[:-1]
            
            if parts:
                dir_key = "/".join(parts)
            else:
                dir_key = "."
            
            by_dir[dir_key].append({
                "name": file_path.name,
                "type": "file",
                "size": file_path.stat().st_size if file_path.exists() else 0
            })
        
        def build_subtree(parent_dict, dir_key):
            children = by_dir.get(dir_key, [])
            
            for child in children:
                if child["type"] == "file":
                    parent_dict["children"].append(child)
                else:
                    subdir = {
                        "name": child["name"],
                        "type": "directory",
                        "children": []
                    }
                    parent_dict["children"].append(subdir)
        
        build_subtree(tree, ".")
        
        subdirs = sorted(set(k for k in by_dir.keys() if k != "."))
        for subdir in subdirs:
            parts = subdir.split("/")
            current = tree
            for i, part in enumerate(parts):
                found = None
                for child in current["children"]:
                    if child["name"] == part and child["type"] == "directory":
                        found = child
                        break
                
                if found is None:
                    new_dir = {"name": part, "type": "directory", "children": []}
                    current["children"].append(new_dir)
                    current = new_dir
                else:
                    current = found
                
                full_key = subdir
                if full_key in by_dir:
                    for item in by_dir[full_key]:
                        if item["name"] not in [c["name"] for c in current["children"]]:
                            current["children"].append(item)
        
        return tree
    
    def _get_directory_sizes(self) -> List[Dict[str, Any]]:
        """Calculate total lines per directory"""
        dir_lines = defaultdict(int)
        
        for file_path in self.files:
            rel_path = file_path.relative_to(self.project_path)
            parts = rel_path.parts
            
            for i in range(1, len(parts)):
                dir_path = "/".join(parts[:i])
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        dir_lines[dir_path] += len(f.readlines())
                except Exception:
                    pass
        
        return [
            {"directory": k, "lines": v}
            for k, v in sorted(dir_lines.items(), key=lambda x: x[1], reverse=True)[:20]
        ]