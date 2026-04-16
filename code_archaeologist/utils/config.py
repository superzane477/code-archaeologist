"""
Configuration management
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import os


class Config:
    """Manages configuration for code archaeologist"""
    
    DEFAULT_CONFIG = {
        "exclude_patterns": [
            ".git", "node_modules", "__pycache__", ".venv", "venv",
            "dist", "build", ".idea", ".vscode", "*.pyc"
        ],
        "llm": {
            "backend": "openai",
            "model": "gpt-4",
            "temperature": 0.3,
            "max_tokens": 2000
        },
        "analysis": {
            "max_file_size_kb": 1000,
            "timeout_seconds": 300,
            "parallel_workers": 4
        },
        "report": {
            "output_format": "html",
            "include_charts": True,
            "theme": "github"
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self._config = self.DEFAULT_CONFIG.copy()
        
        if config_path and config_path.exists():
            self._load_from_file(config_path)
        
        self._apply_env_overrides()
    
    def _load_from_file(self, path: Path) -> None:
        """Load configuration from JSON/YAML file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                self._deep_merge(self._config, user_config)
        except Exception:
            pass
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides"""
        if os.getenv("LLM_BACKEND"):
            self._config["llm"]["backend"] = os.getenv("LLM_BACKEND")
        if os.getenv("LLM_API_KEY"):
            self._config["llm"]["api_key"] = os.getenv("LLM_API_KEY")
        if os.getenv("LLM_MODEL"):
            self._config["llm"]["model"] = os.getenv("LLM_MODEL")
        if os.getenv("LLM_BASE_URL"):
            self._config["llm"]["base_url"] = os.getenv("LLM_BASE_URL")
        
        if os.getenv("OUTPUT_PATH"):
            self._config["report"]["output_path"] = os.getenv("OUTPUT_PATH")
    
    def _deep_merge(self, base: Dict, updates: Dict) -> None:
        """Deep merge updates into base dictionary"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """Get a configuration value by key path"""
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value
    
    def set(self, value: Any, *keys: str) -> None:
        """Set a configuration value by key path"""
        target = self._config
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
    
    @property
    def exclude_patterns(self) -> List[str]:
        return self._config.get("exclude_patterns", [])
    
    @property
    def llm_config(self) -> Dict[str, Any]:
        return self._config.get("llm", {})
    
    @property
    def analysis_config(self) -> Dict[str, Any]:
        return self._config.get("analysis", {})
    
    @property
    def report_config(self) -> Dict[str, Any]:
        return self._config.get("report", {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return self._config.copy()
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save configuration to file"""
        target = path or self.config_path
        if target:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)