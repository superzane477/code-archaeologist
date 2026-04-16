"""
Language detector for identifying programming languages in a codebase
"""
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.token import Comment, String, Number, Keyword, Name


# Language signature patterns
LANGUAGE_SIGNATURES = {
    "python": {
        "extensions": [".py"],
        "keywords": ["def ", "class ", "import ", "from ", "if __name__", "self.", "print("],
        "comment_style": "#",
        "file_markers": ["setup.py", "requirements.txt", "pyproject.toml", "__init__.py"]
    },
    "javascript": {
        "extensions": [".js", ".jsx", ".mjs", ".cjs"],
        "keywords": ["const ", "let ", "function ", "=>", "require(", "module.exports", "async ", "await "],
        "comment_style": "//",
        "file_markers": ["package.json", "node_modules", "webpack.config", "vite.config"]
    },
    "typescript": {
        "extensions": [".ts", ".tsx", ".d.ts"],
        "keywords": [": string", ": number", ": boolean", "interface ", "type ", "as ", "<T>"],
        "comment_style": "//",
        "file_markers": ["tsconfig.json"]
    },
    "go": {
        "extensions": [".go"],
        "keywords": ["func ", "package ", "import (", "go func", "chan ", "defer ", ":= "],
        "comment_style": "//",
        "file_markers": ["go.mod", "go.sum"]
    },
    "java": {
        "extensions": [".java"],
        "keywords": ["public class", "private ", "protected ", "void ", "extends ", "implements ", "System.out"],
        "comment_style": "//",
        "file_markers": ["pom.xml", "build.gradle", "gradle.properties"]
    },
    "rust": {
        "extensions": [".rs"],
        "keywords": ["fn ", "let mut", "impl ", "pub fn", "use ", "mod ", "-> ", "&self", "&mut"],
        "comment_style": "//",
        "file_markers": ["Cargo.toml", "Cargo.lock"]
    },
    "c": {
        "extensions": [".c", ".h"],
        "keywords": ["#include", "int main(", "void ", "char *", "printf(", "struct "],
        "comment_style": "//",
        "file_markers": ["Makefile", ".c", ".h"]
    },
    "cpp": {
        "extensions": [".cpp", ".cc", ".cxx", ".hpp", ".hh"],
        "keywords": ["#include <", "std::", "cout <<", "cin >>", "namespace ", "template<", "virtual "],
        "comment_style": "//",
        "file_markers": ["CMakeLists.txt", ".cmake"]
    },
    "ruby": {
        "extensions": [".rb"],
        "keywords": ["def ", "end", "require ", "gem ", "class ", "module ", "attr_accessor", "puts "],
        "comment_style": "#",
        "file_markers": ["Gemfile", "Rakefile"]
    },
    "php": {
        "extensions": [".php"],
        "keywords": ["<?php", "$", "echo ", "function ", "class ", "public ", "private "],
        "comment_style": "//",
        "file_markers": ["composer.json"]
    }
}


class LanguageDetector:
    """Detects programming languages in a project"""
    
    def __init__(self, project_path: Path, exclude_patterns: List[str] = None):
        self.project_path = project_path
        self.exclude_patterns = exclude_patterns or [
            ".git", "node_modules", "__pycache__", ".venv", "venv",
            "dist", "build", ".idea", ".vscode"
        ]
    
    def detect(self) -> Dict[str, any]:
        """
        Detect languages used in the project.
        
        Returns:
            Dictionary with:
            - languages: list of (language, percentage, line_count) tuples
            - primary_language: the most used language
            - total_lines: total lines of code
            - file_counts: count of files per language
        """
        language_stats = defaultdict(lambda: {"files": 0, "lines": 0})
        
        for file_path in self._scan_files():
            lang = self._identify_file_language(file_path)
            if lang:
                language_stats[lang]["files"] += 1
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        language_stats[lang]["lines"] += lines
                except Exception:
                    pass
        
        total_lines = sum(stats["lines"] for stats in language_stats.values())
        languages = []
        
        for lang, stats in sorted(language_stats.items(), key=lambda x: x[1]["lines"], reverse=True):
            percentage = (stats["lines"] / total_lines * 100) if total_lines > 0 else 0
            languages.append({
                "name": lang,
                "files": stats["files"],
                "lines": stats["lines"],
                "percentage": round(percentage, 1)
            })
        
        primary = languages[0]["name"] if languages else "unknown"
        
        return {
            "languages": languages,
            "primary_language": primary,
            "total_lines": total_lines,
            "file_counts": {lang: stats["files"] for lang, stats in language_stats.items()}
        }
    
    def _scan_files(self) -> List[Path]:
        """Scan project for code files"""
        files = []
        
        for path in self.project_path.rglob("*"):
            if path.is_file():
                if any(excluded in str(path) for excluded in self.exclude_patterns):
                    continue
                files.append(path)
        
        return files
    
    def _identify_file_language(self, file_path: Path) -> str:
        """Identify the language of a single file"""
        ext = file_path.suffix.lower()
        
        for lang, sig in LANGUAGE_SIGNATURES.items():
            if ext in sig["extensions"]:
                if self._verify_language(file_path, lang):
                    return lang
        
        return self._detect_from_content(file_path)
    
    def _verify_language(self, file_path: Path, lang: str) -> bool:
        """Verify language by checking for characteristic patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(4096)
            
            sig = LANGUAGE_SIGNATURES.get(lang, {})
            keywords = sig.get("keywords", [])
            
            matches = sum(1 for kw in keywords if kw in content)
            return matches >= 2
            
        except Exception:
            return False
    
    def _detect_from_content(self, file_path: Path) -> str:
        """Detect language from file content using Pygments"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return "unknown"
            
            try:
                lexer = guess_lexer(content[:4096])
                lang = lexer.name.lower()
                
                lang_map = {
                    "python": "python",
                    "javascript": "javascript",
                    "typescript": "typescript",
                    "go": "go",
                    "java": "java",
                    "ruby": "ruby",
                    "php": "php",
                    "c": "c",
                    "c++": "cpp"
                }
                
                return lang_map.get(lang, "unknown")
            except Exception:
                return "unknown"
                
        except Exception:
            return "unknown"
    
    def get_language_config(self, lang: str) -> Dict:
        """Get configuration for a specific language"""
        return LANGUAGE_SIGNATURES.get(lang, {})