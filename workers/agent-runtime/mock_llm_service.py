"""
Mock LLM service for testing agent pipeline.

Returns valid JSON responses with intentional inconsistencies for testing warning generation.
Implements Requirements: 2.2, 3.2, 4.2, 5.2, 6.2
"""

from typing import Any, Dict
import logging

# Configure logging
logger = logging.getLogger(__name__)


class MockLLMService:
    """Mock LLM service that returns schema-compliant responses."""
    
    def __init__(self):
        """Initialize the mock LLM service."""
        self.call_count = 0
    
    def generate(self, prompt: str, schema: Dict[str, Any], temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate mock content based on the schema.
        
        Implements Requirement 12.4: Log LLM calls
        
        Args:
            prompt: The prompt (not used in mock)
            schema: JSON schema defining expected output
            temperature: Temperature parameter (not used in mock)
            
        Returns:
            Mock content matching the schema
        """
        self.call_count += 1
        
        # Requirement 12.4: Log LLM call details
        logger.info(
            f"LLM call #{self.call_count} - "
            f"model: mock_llm, "
            f"temperature: {temperature}, "
            f"prompt_length: {len(prompt)} chars"
        )
        logger.debug(f"LLM prompt: {prompt[:200]}...")  # Log first 200 chars of prompt
        
        # Determine document type from schema or prompt
        # Check required fields first as they are more reliable than prompt keywords
        required_fields = schema.get("required", [])
        
        # Check required fields to determine document type
        if "scenes" in required_fields:
            response = self._generate_script_draft()
        elif "shots" in required_fields:
            response = self._generate_visual_spec()
        elif "genre" in required_fields:
            response = self._generate_brief()
        elif "world_rules" in required_fields:
            response = self._generate_story_bible()
        elif "characters" in required_fields:
            response = self._generate_character_profile()
        # Fallback to prompt-based detection if required fields don't match
        elif "storyboard" in prompt.lower() and "shot" in prompt.lower():
            response = self._generate_visual_spec()
        elif "brief" in prompt.lower() and "adaptation" in prompt.lower():
            response = self._generate_brief()
        elif "story_bible" in prompt.lower():
            response = self._generate_story_bible()
        elif "character" in prompt.lower() and "profile" in prompt.lower():
            response = self._generate_character_profile()
        elif "script" in prompt.lower() and "scene" in prompt.lower():
            response = self._generate_script_draft()
        else:
            response = {}
        
        # Log response summary
        logger.info(f"LLM response received - response_keys: {list(response.keys())}")
        
        return response
    
    def _generate_brief(self) -> Dict[str, Any]:
        """Generate mock brief document."""
        return {
            "genre": "urban_drama",
            "target_audience": "18-35 female viewers interested in family dynamics",
            "core_selling_points": [
                "Identity reversal with high emotional stakes",
                "Visual anchor system (red earring)",
                "Family power dynamics"
            ],
            "main_conflict": "Protagonist must prove her true identity to reclaim her place in the family",
            "adaptation_risks": [
                "Pacing may feel rushed in 60-second format",
                "Complex family relationships need clear visual cues"
            ],
            "target_style": "cinematic with cold color palette",
            "tone": "tense and dramatic"
        }
    
    def _generate_story_bible(self) -> Dict[str, Any]:
        """Generate mock story bible document with intentional inconsistency."""
        return {
            "world_rules": [
                "Family status is determined by possession of ancestral tokens",
                "Red earring signifies true heir status",
                "Public challenges must be witnessed by elders"
            ],
            "timeline": [
                {
                    "event": "Protagonist abandoned as child",
                    "time": "20 years ago"
                },
                {
                    "event": "Protagonist returns with proof",
                    "time": "present day"
                }
            ],
            "relationship_baseline": {
                "protagonist_antagonist": ["rivalry", "family_tension"],
                "protagonist_elder": ["unknown", "potential_ally"]
            },
            "forbidden_conflicts": [
                "No physical violence in family hall",
                "No direct contradiction of elder decisions"
            ],
            "key_settings": {
                "ancestral_hall": "Traditional Chinese architecture with red accents",
                "family_estate": "Modern luxury mixed with traditional elements"
            }
        }
    
    def _generate_character_profile(self) -> Dict[str, Any]:
        """Generate mock character profile with intentional missing visual anchor."""
        return {
            "characters": [
                {
                    "name": "Lin Xiao",
                    "role": "protagonist",
                    "goal": "Reclaim her rightful place in the family",
                    "motivation": "Prove her identity and honor her mother's memory",
                    "speaking_style": "Calm, measured, with underlying steel",
                    "visual_anchor": "Red jade earring, white dress",
                    "personality_traits": ["resilient", "strategic", "emotionally controlled"],
                    "relationships": {
                        "Lin Wei": "antagonist_sister",
                        "Elder Lin": "potential_ally"
                    }
                },
                {
                    "name": "Lin Wei",
                    "role": "antagonist",
                    "goal": "Maintain her position as family heir",
                    "motivation": "Fear of losing status and power",
                    "speaking_style": "Aggressive, domineering, publicly confident",
                    "visual_anchor": "",  # Intentionally empty for testing warning generation
                    "personality_traits": ["ambitious", "insecure", "publicly_aggressive"],
                    "relationships": {
                        "Lin Xiao": "rival_sister",
                        "Elder Lin": "seeks_approval"
                    }
                },
                {
                    "name": "Elder Lin",
                    "role": "supporting",
                    "goal": "Maintain family honor and tradition",
                    "motivation": "Uphold family rules and discover truth",
                    "speaking_style": "Formal, authoritative, measured",
                    "visual_anchor": "Traditional robes, family pendant",
                    "personality_traits": ["wise", "traditional", "fair"],
                    "relationships": {
                        "Lin Xiao": "unknown_relation",
                        "Lin Wei": "current_heir"
                    }
                }
            ]
        }
    
    def _generate_script_draft(self) -> Dict[str, Any]:
        """Generate mock script draft with intentional character behavior deviation."""
        return {
            "scenes": [
                {
                    "scene_no": 1,
                    "location": "Ancestral Hall - Main Chamber",
                    "characters": ["Lin Xiao", "Lin Wei", "Elder Lin"],
                    "goal": "Establish conflict and reveal protagonist's claim",
                    "dialogue": [
                        {
                            "character": "Lin Wei",
                            "line": "You dare show your face here? You have no claim to this family!",
                            "emotion": "aggressive"
                        },
                        {
                            "character": "Lin Xiao",
                            "line": "I have every right. This earring proves my bloodline.",
                            "emotion": "calm_confident"
                        },
                        {
                            "character": "Lin Wei",
                            "line": "That could be stolen! You're nothing but an imposter!",
                            "emotion": "desperate"
                        },
                        {
                            "character": "Lin Xiao",
                            "line": "Then explain why Elder Lin recognizes it.",
                            "emotion": "strategic"
                        },
                        {
                            "character": "Elder Lin",
                            "line": "The red jade... I have not seen it in twenty years.",
                            "emotion": "shocked_recognition"
                        }
                    ],
                    "emotion_beats": [
                        "tension_builds",
                        "public_challenge",
                        "evidence_revealed",
                        "power_shift"
                    ],
                    "duration_estimate_sec": 55
                }
            ]
        }
    
    def _generate_visual_spec(self) -> Dict[str, Any]:
        """Generate mock visual spec for storyboard."""
        return {
            "shots": [
                {
                    "shot_id": "temp_001",
                    "render_prompt": "Close-up of red jade earring catching light, cold white lighting, shallow depth of field",
                    "character_refs": ["Lin Xiao"],
                    "style_keywords": ["cinematic", "cold_palette", "dramatic_lighting"],
                    "composition": "extreme_close_up"
                },
                {
                    "shot_id": "temp_002",
                    "render_prompt": "Medium shot of Lin Wei stepping forward aggressively, low angle to show dominance, ancestral hall background",
                    "character_refs": ["Lin Wei"],
                    "style_keywords": ["cinematic", "cold_palette", "power_dynamic"],
                    "composition": "medium_low_angle"
                },
                {
                    "shot_id": "temp_003",
                    "render_prompt": "Two-shot of Lin Xiao and Elder Lin, focus on Elder's shocked expression, family pendant visible",
                    "character_refs": ["Lin Xiao", "Elder Lin"],
                    "style_keywords": ["cinematic", "cold_palette", "emotional_reveal"],
                    "composition": "medium_two_shot"
                }
            ],
            "overall_duration_ms": 58000,
            "shot_count": 3,
            "visual_style": "cinematic cold palette with red accents",
            "camera_strategy": "favor close-ups and low angles for power dynamics"
        }
    
    def get_token_usage(self) -> int:
        """Get mock token usage."""
        return self.call_count * 500  # Mock: 500 tokens per call
