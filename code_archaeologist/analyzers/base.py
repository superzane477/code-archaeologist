"""
Base analyzer class for code analysis
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AnalysisResult:
    """Container for analysis results"""
    file_path: str
    line_count: int = 0
    complexity: int = 0
    complexity_rank: str = "A"
    issues: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


class BaseAnalyzer(ABC):
    """Abstract base class for language-specific analyzers"""
    
    def __init__(self, project_path: Path, config: Optional[Dict] = None):
        self.project_path = project_path
        self.config = config or {}
        self.results: List[AnalysisResult] = []
    
    @abstractmethod
    def analyze(self, files: List[Path]) -> Dict[str, Any]:
        """Analyze the given files and return results"""
        pass
    
    @abstractmethod
    def get_language(self) -> str:
        """Return the language this analyzer handles"""
        pass
    
    def get_file_extensions(self) -> List[str]:
        """Return list of file extensions this analyzer handles"""
        return []
    
    def calculate_complexity_rank(self, complexity: int) -> str:
        """Calculate complexity rank (A-F) based on cyclomatic complexity"""
        if complexity <= 5:
            return "A"
        elif complexity <= 10:
            return "B"
        elif complexity <= 20:
            return "C"
        elif complexity <= 30:
            return "D"
        else:
            return "F"