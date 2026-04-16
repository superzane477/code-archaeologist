"""
Tech stack detector for identifying frameworks, libraries, and architecture patterns
"""
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict
import re


class TechStackDetector:
    """Detects technology stack, frameworks, and architecture patterns"""
    
    FRAMEWORK_PATTERNS = {
        # Python
        "django": {"files": ["manage.py", "settings.py"], "deps": ["django"], "era": "classic"},
        "flask": {"files": [], "deps": ["flask"], "era": "modern"},
        "fastapi": {"files": [], "deps": ["fastapi", "uvicorn"], "era": "modern"},
        "pyramid": {"files": ["setup.py"], "deps": ["pyramid"], "era": "classic"},
        "tornado": {"files": [], "deps": ["tornado"], "era": "classic"},
        "scrapy": {"files": [], "deps": ["scrapy"], "era": "modern"},
        "pandas": {"files": [], "deps": ["pandas"], "era": "modern"},
        "numpy": {"files": [], "deps": ["numpy"], "era": "modern"},
        "celery": {"files": [], "deps": ["celery"], "era": "modern"},
        
        # JavaScript/TypeScript
        "react": {"files": [], "deps": ["react", "react-dom"], "era": "modern"},
        "vue": {"files": [], "deps": ["vue"], "era": "modern"},
        "angular": {"files": [], "deps": ["@angular/core"], "era": "modern"},
        "nextjs": {"files": ["next.config.js", "next.config.ts"], "deps": ["next"], "era": "modern"},
        "nuxt": {"files": ["nuxt.config.js"], "deps": ["nuxt"], "era": "modern"},
        "svelte": {"files": ["svelte.config.js"], "deps": ["svelte"], "era": "modern"},
        "gatsby": {"files": ["gatsby-config.js"], "deps": ["gatsby"], "era": "modern"},
        "jquery": {"files": [], "deps": ["jquery"], "era": "classic"},
        "express": {"files": [], "deps": ["express"], "era": "modern"},
        "koa": {"files": [], "deps": ["koa"], "era": "modern"},
        "hapi": {"files": [], "deps": ["@hapi/hapi"], "era": "modern"},
        "sails": {"files": [], "deps": ["sails"], "era": "classic"},
        
        # Backend frameworks
        "spring": {"files": [], "deps": ["spring-boot", "spring-framework"], "era": "classic"},
        "spring-boot": {"files": ["pom.xml", "build.gradle"], "deps": ["spring-boot"], "era": "modern"},
        "play": {"files": ["build.sbt"], "deps": ["playframework"], "era": "classic"},
        "rails": {"files": ["Gemfile"], "deps": ["rails"], "era": "classic"},
        "laravel": {"files": ["artisan"], "deps": ["laravel"], "era": "modern"},
        "symfony": {"files": [], "deps": ["symfony"], "era": "classic"},
        
        # Mobile
        "react-native": {"files": [], "deps": ["react-native"], "era": "modern"},
        "flutter": {"files": ["pubspec.yaml"], "deps": ["flutter"], "era": "modern"},
        "ionic": {"files": [], "deps": ["@ionic/vue"], "era": "modern"},
        
        # Data/ML
        "tensorflow": {"files": [], "deps": ["tensorflow"], "era": "modern"},
        "pytorch": {"files": [], "deps": ["torch"], "era": "modern"},
        "keras": {"files": [], "deps": ["keras"], "era": "modern"},
        "scikit-learn": {"files": [], "deps": ["scikit-learn"], "era": "modern"},
    }
    
    ARCHITECTURE_PATTERNS = {
        "microservices": ["docker-compose", "Dockerfile", "kubernetes", "k8s", "service.yaml"],
        "monolith": ["app.py", "main.py", "server.js", "index.js"],
        "mvc": ["controllers/", "models/", "views/"],
        "api": ["api/", "rest/", "endpoints/", "routes/"],
        "serverless": ["serverless.yml", "vercel.json", "netlify.toml", "lambda"],
        "graphql": ["schema.graphql", "resolvers/", "typeDefs"],
        "crud": ["crud.py", "views.py", "resources/"],
    }
    
    ERA_INDICATORS = {
        "classic": [
            "angularjs", "backbone", "ember", "knockout",
            "jquery", "prototype", "mootools",
            "python2", "python3.5", "python3.6",
            "angularjs", "gulp", "grunt"
        ],
        "modern": [
            "react18", "react19", "vue3", "svelte",
            "next13", "next14", "vite",
            "python3.9", "python3.10", "python3.11", "python3.12",
            "es2020", "es2021", "es2022", "typescript4", "typescript5"
        ]
    }
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def detect(self) -> Dict[str, Any]:
        """
        Detect the technology stack used in the project.
        
        Returns:
            Dictionary with detected frameworks, libraries, era, and patterns
        """
        results = {
            "languages": [],
            "frameworks": [],
            "libraries": [],
            "tools": [],
            "era": "unknown",
            "architecture_patterns": [],
            "tech_generation": "unknown"
        }
        
        self._detect_from_package_files(results)
        self._detect_from_source_code(results)
        self._determine_era_and_generation(results)
        
        return results
    
    def _detect_from_package_files(self, results: Dict):
        """Detect tech stack from dependency/package files"""
        pkg_files = [
            ("requirements.txt", "python"),
            ("pyproject.toml", "python"),
            ("setup.py", "python"),
            ("package.json", "javascript"),
            ("go.mod", "go"),
            ("pom.xml", "java"),
            ("Cargo.toml", "rust"),
            ("Gemfile", "ruby"),
            ("composer.json", "php")
        ]
        
        for filename, lang in pkg_files:
            file_path = self.project_path / filename
            if file_path.exists():
                if lang not in results["languages"]:
                    results["languages"].append(lang)
                
                self._parse_dependencies(file_path, lang, results)
    
    def _parse_dependencies(self, file_path: Path, lang: str, results: Dict):
        """Parse dependency file and extract frameworks/libraries"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            if lang == "javascript":
                self._parse_package_json(content, results)
            elif lang == "python":
                self._parse_python_deps(content, results)
            elif lang == "go":
                self._parse_go_mod(content, results)
        except Exception:
            pass
    
    def _parse_package_json(self, content: str, results: Dict):
        """Parse package.json for dependencies"""
        import json
        try:
            pkg = json.loads(content)
            all_deps = {}
            all_deps.update(pkg.get("dependencies", {}))
            all_deps.update(pkg.get("devDependencies", {}))
            
            for name, version in all_deps.items():
                detected = False
                for fw_name, fw_info in self.FRAMEWORK_PATTERNS.items():
                    if name in fw_info["deps"] or name.startswith(fw_info["deps"][0].split("-")[0] if "-" in fw_info["deps"][0] else fw_info["deps"][0]):
                        if fw_name not in [f["name"] for f in results["frameworks"]]:
                            results["frameworks"].append({
                                "name": fw_name,
                                "version": version,
                                "category": "frontend" if fw_name in ["react", "vue", "angular", "svelte"] else "backend"
                            })
                        detected = True
                        break
                
                if not detected and name:
                    results["libraries"].append({"name": name, "version": version})
                    
        except Exception:
            pass
    
    def _parse_python_deps(self, content: str, results: Dict):
        """Parse Python requirements.txt or pyproject.toml"""
        deps = []
        
        if "dependencies" in content:
            in_deps = False
            for line in content.split('\n'):
                if '[dependencies]' in line or line.strip().startswith('dependencies'):
                    in_deps = True
                elif in_deps and line.strip().startswith('['):
                    in_deps = False
                elif in_deps:
                    match = re.match(r'^\s*"?([a-zA-Z0-9_-]+)', line)
                    if match:
                        deps.append(match.group(1))
        else:
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '==' in line:
                    deps.append(line.split('==')[0].strip())
        
        for dep in deps:
            for fw_name, fw_info in self.FRAMEWORK_PATTERNS.items():
                if dep in fw_info["deps"]:
                    if fw_name not in [f["name"] for f in results["frameworks"]]:
                        results["frameworks"].append({
                            "name": fw_name,
                            "version": dep,
                            "category": "python"
                        })
                    break
            else:
                results["libraries"].append({"name": dep})
    
    def _parse_go_mod(self, content: str, results: Dict):
        """Parse go.mod for dependencies"""
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith("require ") or line.startswith("github.com") or line.startswith("golang.org"):
                parts = line.split()
                if len(parts) >= 2:
                    results["libraries"].append({"name": parts[0]})
    
    def _detect_from_source_code(self, results: Dict):
        """Detect tech stack by scanning source code"""
        for fw_name, fw_info in self.FRAMEWORK_PATTERNS.items():
            for marker_file in fw_info["files"]:
                if (self.project_path / marker_file).exists():
                    if fw_name not in [f["name"] for f in results["frameworks"]]:
                        results["frameworks"].append({
                            "name": fw_name,
                            "category": fw_info.get("era", "unknown")
                        })
        
        for pattern_name, indicators in self.ARCHITECTURE_PATTERNS.items():
            for indicator in indicators:
                if any(str(f).find(indicator) >= 0 for f in self.project_path.rglob("*")):
                    if pattern_name not in results["architecture_patterns"]:
                        results["architecture_patterns"].append(pattern_name)
                    break
    
    def _determine_era_and_generation(self, results: Dict):
        """Determine the era (classic vs modern) and tech generation"""
        all_content = ""
        
        for ext in ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"]:
            for file_path in self.project_path.rglob(ext):
                try:
                    all_content += file_path.read_text(encoding='utf-8', errors='ignore')[:10000]
                except Exception:
                    pass
        
        classic_count = sum(1 for indicator in self.ERA_INDICATORS["classic"] if indicator.lower() in all_content.lower())
        modern_count = sum(1 for indicator in self.ERA_INDICATORS["modern"] if indicator.lower() in all_content.lower())
        
        if classic_count > modern_count:
            results["era"] = "classic"
            results["tech_generation"] = "legacy"
        elif modern_count > classic_count:
            results["era"] = "modern"
            results["tech_generation"] = "current"
        else:
            results["era"] = "mixed"
            results["tech_generation"] = "mixed"
        
        for fw in results["frameworks"]:
            fw_name = fw["name"].lower()
            if fw_name in self.FRAMEWORK_PATTERNS:
                fw_era = self.FRAMEWORK_PATTERNS[fw_name].get("era", "unknown")
                if fw_era != "unknown":
                    fw["era"] = fw_era