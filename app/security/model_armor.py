# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Model Armor security and sanitization filter for CineFlow."""

import os
import re
from pathlib import Path
from typing import Any

import yaml


class ModelArmorFilter:
    """Enterprise sanitization, prompt injection detection, and RAI guardrail filter."""

    def __init__(self, config_path: str | None = None):
        self.config = self._load_config(config_path)
        self.pii_patterns = [
            (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_MASKED]"),
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", "[EMAIL_MASKED]"),
            (
                r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
                "[PHONE_MASKED]",
            ),
            (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", "[CREDIT_CARD_MASKED]"),
        ]
        self.injection_patterns = [
            r"ignore\s+previous\s+instructions",
            r"system\s*override",
            r"disregard\s+(all\s+)?prior\s+(rules|instructions)",
            r"you\s+are\s+now\s+in\s+unrestricted\s+mode",
            r"bypass\s+(safety|content)\s+filters",
            r"jailbreak",
        ]
        self.blocked_rai_terms = [
            r"how\s+to\s+build\s+a\s+bomb",
            r"synthesize\s+illegal\s+chemical",
            r"generate\s+malware",
            r"ddos\s+attack\s+script",
        ]

    def _load_config(self, config_path: str | None) -> dict[str, Any]:
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
                "config",
                "model-armor-config.yaml",
            )
        path = Path(config_path)
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                pass
        return {
            "filter_config": {
                "rai_settings": {
                    "hate_speech": "BLOCK_LOW_AND_ABOVE",
                    "harassment": "BLOCK_LOW_AND_ABOVE",
                    "sexually_explicit": "BLOCK_LOW_AND_ABOVE",
                    "dangerous_content": "BLOCK_LOW_AND_ABOVE",
                },
                "prompt_injection_protection": {
                    "enabled": True,
                    "enforcement": "REJECT",
                },
                "pii_sanitization": {"enabled": True, "mask_character": "*"},
            }
        }

    def inspect_and_sanitize(self, text: str) -> tuple[bool, str, str | None]:
        """Inspects text for prompt injection and RAI violations, sanitizes PII.

        Returns:
            Tuple of (is_safe, sanitized_text, violation_reason)
        """
        if not text:
            return True, text, None

        # 1. Prompt injection check
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return (
                    False,
                    text,
                    f"Prompt injection attempt detected matching: {pattern}",
                )

        # 2. RAI Safety check
        for pattern in self.blocked_rai_terms:
            if re.search(pattern, text, re.IGNORECASE):
                return False, text, f"Content violated RAI policy: {pattern}"

        # 3. PII Sanitization
        sanitized = text
        for pattern, replacement in self.pii_patterns:
            sanitized = re.sub(pattern, replacement, sanitized)

        return True, sanitized, None


# Global singleton instance
model_armor = ModelArmorFilter()


def sanitize_director_input(user_input: str) -> str:
    """Sanitize input from Human Director or trigger Model Armor rejection error."""
    is_safe, sanitized, reason = model_armor.inspect_and_sanitize(user_input)
    if not is_safe:
        raise ValueError(f"Google Model Armor Security Intercept: {reason}")
    return sanitized
