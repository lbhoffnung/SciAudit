import os
import re
from typing import List, Dict, Optional
from .models import Severity

class Config:
    def __init__(self):
        self.rules: Dict[str, str] = {} # rule_id -> severity name or 'off'
        self.ignore_paths: List[str] = []

    def get_rule_severity(self, rule_id: str) -> Optional[str]:
        return self.rules.get(rule_id)

    def is_rule_off(self, rule_id: str) -> bool:
        return self.rules.get(rule_id) == "off"

    def should_ignore(self, path: str) -> bool:
        norm_path = os.path.normpath(path).replace("\\", "/")
        for ignore in self.ignore_paths:
            if ignore in norm_path:
                return True
        return False

def load_config(root_dir: str = ".") -> Config:
    config = Config()
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
        print(f"\x1b[33mWarning: Failed to parse .sciaudit.yml ({e}). Using defaults.\x1b[0m")
        
    return config
