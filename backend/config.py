"""
Configuration Management
"""

import json
import os
from typing import Dict, Any


class Config:
    """Manages configuration for task routing and system settings"""

    def __init__(self, config_path: str = "task_rules.json"):
        self.config_path = config_path
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        """Load task routing rules from JSON file"""
        if not os.path.exists(self.config_path):
            # Create default rules if file doesn't exist
            default_rules = {
                "routing_rules": {
                    "coding": "grok_refine_then_claude",
                    "summarization": "chatgpt",
                    "data_analysis": "chatgpt",
                    "creative_writing": "grok",
                    "general": "grok"
                },
                "settings": {
                    "max_retries": 3,
                    "timeout_seconds": 60,
                    "enable_logging": True
                }
            }
            self._save_rules(default_rules)
            return default_rules

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _save_rules(self, rules: Dict[str, Any]):
        """Save rules to JSON file"""
        with open(self.config_path, 'w') as f:
            json.dump(rules, f, indent=2)

    def get_routing_rule(self, task_type: str) -> str:
        """Get routing rule for a specific task type"""
        return self.rules['routing_rules'].get(task_type, 'grok')

    def update_routing_rule(self, task_type: str, rule: str):
        """Update routing rule for a task type"""
        self.rules['routing_rules'][task_type] = rule
        self._save_rules(self.rules)

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.rules['settings'].get(key, default)
