"""
Highlight detector for YouTube videos.
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class HighlightDetector:
    """Detects highlights in videos based on various signals."""

    def __init__(self, config: dict):
        self.config = config
        self.highlight_config = config.get("highlight", {})

    def detect_highlights(
        self,
        video_path: str,
        video_info: Dict = None,
    ) -> List[Dict]:
        """Detect highlight segments in a video."""
        
        highlights = []
        
        # Check for heatmap data from YouTube
        if video_info and video_info.get("heatmap"):
            heatmap = video_info["heatmap"]
            # Find most popular segments from heatmap
            highlights.extend(self._heatmap_to_segments(heatmap))
        
        # Check for chapters
        if video_info and video_info.get("chapters"):
            chapters = video_info["chapters"]
            highlights.extend(self._chapters_to_segments(chapters))
        
        # Sort by popularity/score
        highlights.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return highlights[:10]  # Return top 10

    def _heatmap_to_segments(self, heatmap: List[Dict]) -> List[Dict]:
        """Convert YouTube heatmap data to highlight segments."""
        segments = []
        for segment in heatmap:
            if segment.get("value", 0) > 0.5:  # High interest segments
                segments.append({
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "score": segment.get("value", 0),
                    "source": "heatmap",
                })
        return segments

    def _chapters_to_segments(self, chapters: List[Dict]) -> List[Dict]:
        """Convert YouTube chapters to highlight segments."""
        segments = []
        for chapter in chapters:
            segments.append({
                "start": chapter.get("start_time", 0),
                "end": chapter.get("end_time", 0),
                "title": chapter.get("title", ""),
                "score": 0.5,
                "source": "chapters",
            })
        return segments
