"""
Agents module - Contains all AI Agent implementations.
"""

# Note: Using absolute imports to avoid relative import issues
# Import order matters - base_agent must be imported first
import sys
from pathlib import Path

# Ensure parent directory is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent, DocumentRef, LockedRef, StageTaskInput, Warning, AssetRef
from agents.brief_agent import BriefAgent
from agents.story_bible_agent import StoryBibleAgent
from agents.character_agent import CharacterAgent
from agents.script_agent import ScriptAgent
from agents.storyboard_agent import StoryboardAgent

__all__ = [
    'BaseAgent',
    'DocumentRef',
    'LockedRef',
    'StageTaskInput',
    'Warning',
    'AssetRef',
    'BriefAgent',
    'StoryBibleAgent',
    'CharacterAgent',
    'ScriptAgent',
    'StoryboardAgent',
]
