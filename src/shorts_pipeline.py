"""
Shorts pipeline for YouTube Shorts automation.
"""

import logging
import time
from pathlib import Path

from src.config import load_config
from src.trending_finder import TrendingFinder
from src.clipper import VideoClipper
from src.clickbait_generator import ClickbaitGenerator
from src.uploader import YouTubeUploader

logger = logging.getLogger(__name__)


class ShortsPipeline:
    """End-to-end pipeline for YouTube Shorts."""

    def __init__(self, config: dict = None):
        self.config = config or load_config()
        self.finder = TrendingFinder(self.config)
        self.clipper = VideoClipper(self.config)
        self.thumb_gen = ClickbaitGenerator(self.config)
        self.uploader = YouTubeUploader(self.config)
        self.shorts_config = self.config.get("shorts", {})
        self.history_file = self.config.get("history_file", "data/shorts_history.json")
        
        # Create data directory
        Path("data").mkdir(exist_ok=True)

    def run(self, dry_run: bool = False, niche: str = None, privacy: str = "unlisted"):
        """Run one full Shorts cycle."""
        logger.info("=" * 60)
        logger.info("YOUTUBE SHORTS PIPELINE")
        logger.info("=" * 60)
        
        # Search for trending Shorts content
        videos = self.finder.find_trending(limit=5, niche=niche)
        
        if not videos:
            logger.info("No trending Shorts found.")
            return
        
        # Process first qualifying video
        for video in videos:
            if self._is_processed(video["id"]):
                continue
            
            self._process_video(video, dry_run=dry_run, privacy=privacy)
            break

    def process_url(self, url: str, dry_run: bool = False, privacy: str = "unlisted"):
        """Process a specific URL for Shorts."""
        video = {
            "id": url.split("v=")[-1] if "v=" in url else "unknown",
            "title": "Direct URL",
            "webpage_url": url,
            "uploader": "Unknown",
            "duration": 60,
            "view_count": 100000,
            "description": "",
            "tags": [],
        }
        self._process_video(video, dry_run=dry_run, privacy=privacy)

    def _process_video(self, video: dict, dry_run: bool = False, privacy: str = "unlisted"):
        """Process a single video into a Short."""
        try:
            # Download and clip to Shorts duration (under 60s)
            clip_path = self.clipper.download_and_clip(
                video["webpage_url"],
                target_duration=45,
            )
            
            if not clip_path:
                logger.warning(f"Failed to clip: {video['title']}")
                return
            
            # Convert to vertical (9:16)
            vertical_path = clip_path.parent / f"{clip_path.stem}_vert.mp4"
            self.clipper.create_vertical(clip_path, vertical_path)
            
            # Generate thumbnail
            thumb_path = self.thumb_gen.create_thumbnail(vertical_path)
            
            # Upload
            if not dry_run:
                self.uploader.upload_video(
                    video_file=vertical_path,
                    title=f"SHORT: {video['title'][:80]}",
                    description=self._make_description(video),
                    tags=["shorts", "viral"],
                    thumb_file=thumb_path,
                    privacy_status=privacy,
                )
            
            self._mark_processed(video["id"])
            
        except Exception as e:
            logger.error(f"Error processing {video['title']}: {e}")

    def _make_description(self, video: dict) -> str:
        """Create description for Shorts upload."""
        desc = f"SHORT: {video['title']}\n\n"
        if video.get("description"):
            desc += video["description"][:200]
        desc += "\n\n#shorts #viral #trending"
        return desc

    def _is_processed(self, video_id: str) -> bool:
        """Check if a video has already been processed."""
        import json
        if Path(self.history_file).exists():
            with open(self.history_file, "r") as f:
                history = json.load(f)
            return video_id in history
        return False

    def _mark_processed(self, video_id: str):
        """Mark a video as processed."""
        import json
        if Path(self.history_file).exists():
            with open(self.history_file, "r") as f:
                history = json.load(f)
        else:
            history = {}
        history[video_id] = time.time()
        with open(self.history_file, "w") as f:
            json.dump(history, f)
