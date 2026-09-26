"""
Facebook Reels pipeline for downloading and processing Facebook reels.
Integrates with the YT_Clipping_2026 pipeline.
"""

import os
import sys
import json
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.config import load_config
from src.clipper import VideoClipper
from src.clickbait_generator import ClickbaitGenerator
from src.cartoon_meme_transformer import CartoonMemeTransformer
from src.uploader import YouTubeUploader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("facebook_reels")

# Facebook reels finder
try:
    from src.facebook_reels_finder import FacebookReelsFinder
except ImportError:
    FacebookReelsFinder = None
    logger.warning("FacebookReelsFinder not available - facebook_reels_finder.py not found")


def run_facebook_reels_pipeline(
    config: dict,
    upload: bool = True,
    privacy_status: str = "unlisted",
    dry_run: bool = False,
    trending_only: bool = True,
    url: str = None,
):
    """Run the Facebook Reels pipeline."""
    
    fb_config = config.get("facebook_reels", {})
    if not fb_config.get("enabled", False):
        logger.info("Facebook reels pipeline is disabled in config.")
        return
    
    if FacebookReelsFinder is None:
        logger.error("FacebookReelsFinder module not available.")
        return
    
    finder = FacebookReelsFinder(config)
    clipper = VideoClipper(config)
    clickbait = ClickbaitGenerator(config)
    transformer = CartoonMemeTransformer(config)
    uploader = YouTubeUploader(config) if upload else None
    
    if url:
        # Process specific reel
        logger.info(f"Processing specific reel: {url}")
        clips = finder.download_reel(url)
    elif trending_only:
        # Find trending reels
        logger.info("Finding trending Facebook reels...")
        clips = finder.find_trending(limit=5)
    else:
        clips = []
    
    for clip_path in clips:
        if not clip_path or not Path(clip_path).exists():
            continue
        
        try:
            # Generate thumbnail
            thumb_path = clickbait.create_thumbnail(Path(clip_path))
            
            # Apply cartoon transform
            cartoon_path = transformer.transform(Path(clip_path))
            
            if uploader and not dry_run:
                uploader.upload_video(
                    video_file=Path(cartoon_path or clip_path),
                    title="Facebook Reel",
                    description="Trending Facebook Reel",
                    tags=["viral", "reels", "facebook"],
                    thumb_file=thumb_path,
                    privacy_status=privacy_status,
                )
        except Exception as e:
            logger.error(f"Error processing reel: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Facebook Reels Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Run without uploading")
    parser.add_argument("--url", type=str, help="Process specific Facebook reel URL")
    parser.add_argument("--trending", action="store_true", help="Process trending reels")
    parser.add_argument("--privacy", type=str, default="unlisted", help="Privacy status")
    
    args = parser.parse_args()
    
    config = load_config()
    
    run_facebook_reels_pipeline(
        config,
        upload=True,
        privacy_status=args.privacy,
        dry_run=args.dry_run,
        trending_only=args.trending,
        url=args.url,
    )


if __name__ == "__main__":
    main()
