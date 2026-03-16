import os
import re
from typing import List, Dict, Optional
from .models import Severity

class Config:
    PROFILES = {
        "strict": {
            # Everything is error
            "SCI-001": "error", "SCI-002": "error", "SCI-003": "error", "SCI-004": "error",
            "SCI-005": "error", "SCI-006": "error", "SCI-007": "error", "SCI-008": "error",
            "SCI-009": "error", "SCI-013": "error", "SCI-014": "error", "SCI-017": "error",
        },
        "balanced": {
            # O perfil balanced utiliza as severidades padrão definidas em cada regra.
            # Não remove nem eleva o rigor além do planejado originalmente.
        },
        "relaxed": {
            "SCI-002": "info",
            "SCI-003": "off",
            "SCI-004": "info",
            "SCI-005": "warning",
            "SCI-009": "info",
            "SCI-013": "off",
            "SCI-014": "info",
            "SCI-017": "warning",
        }
    }

    def __init__(self, profile_name: str = "balanced"):
        self.rules: Dict[str, str] = {} # rule_id -> severity name or 'off'
        self.ignore_paths: List[str] = []
        self.baseline: List[Dict] = [] # List of violation fingerprints
        
        # Load profile defaults
        if profile_name in self.PROFILES:
            self.rules.update(self.PROFILES[profile_name])

    def get_rule_severity(self, rule_id: str) -> Optional[str]:
        return self.rules.get(rule_id)

    def is_rule_off(self, rule_id: str) -> bool:
        return self.rules.get(rule_id) == "off"

    def should_ignore(self, path: str) -> bool:
        norm_path = os.path.normpath(path).replace("\\", "/")
        path_parts = norm_path.split("/")
        
        for ignore in self.ignore_paths:
            # Verifica se o padrão de ignore (ex: 'venv') é uma sub-pasta exata
            # ou o arquivo exato dentro do caminho completo.
            if ignore in path_parts:
                return True
        return False

    def is_in_baseline(self, violation_data: Dict) -> bool:
        """
        Check if a violation fingerprint matches one in the baseline.
        """
        for b in self.baseline:
            # Optamos por não incluir 'message' na comparação obrigatória do baseline
            # para evitar que mudanças cosméticas em hints ou mensagens (ex: correções ortográficas)
            # invalidem todo o registro do baseline injustamente. 
            # O fingerprint é focado em (regra, arquivo, linha).
            if b.get("rule_id") == violation_data.get("rule_id") and \
               b.get("file") == violation_data.get("file") and \
               b.get("line") == violation_data.get("line"):
                return True
        return False

def load_config(root_dir: str = ".", profile: Optional[str] = None) -> Config:
    config = Config(profile_name=profile or "balanced")
    config_path = os.path.join(root_dir, ".sciaudit.yml")
    
    if not os.path.exists(config_path):
        return config
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Simple line-based YAML parser (Zero Dependencies)
            # This handles:
            # rules:
            #   SCI-002: warning
            # paths:
            #   ignore:
            #     - "venv/"
            
            current_section = None
            for line in content.splitlines():
                # Remove comments
                line = line.split("#")[0].strip()
                if not line:
                    continue
                
                # Detect top-level sections
                if line.endswith(":"):
                    header = line[:-1].strip().lower()
                    if header == "rules":
                        current_section = "rules"
                        continue
                    elif header == "paths":
                        current_section = "paths"
                        continue
                    elif header == "ignore":
                        if current_section == "paths":
                            current_section = "ignore"
                            continue
                
                # Parse entries
                if current_section == "rules":
                    # sci-002: warning
                    if ":" in line:
                        rid, val = [p.strip() for p in line.split(":", 1)]
                        config.rules[rid.upper()] = val.lower()
                elif current_section == "ignore":
                    # - "venv/"
                    if line.startswith("-"):
                        path_val = line[1:].strip().strip("\"").strip("'").strip("/")
                        if path_val:
                            config.ignore_paths.append(path_val)
                            
    except Exception as e:
        import sys
        print(f"\x1b[33mWarning: Failed to parse .sciaudit.yml ({e}). Using defaults.\x1b[0m", file=sys.stderr)
        
    return config
