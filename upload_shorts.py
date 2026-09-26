
"""
Upload shorts video directly.
"""

import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.uploader import YouTubeUploader
from src.config import load_config

cfg = load_config()
uploader = YouTubeUploader(cfg)

video_file = "output/shorts/SjjBeV0Z4zU_I_Can_t_Control_My_Reactions_vert.mp4"
thumb_file = "output/shorts/SjjBeV0Z4zU_thumbnail.jpg"

print(f"Video: {video_file} ({Path(video_file).stat().st_size / 1024:.0f} KB)")
print(f"Thumb: {thumb_file}")

title = "THE MOMENT EVERYTHING WENT WRONG... 🤯 (I Can't Control My Reactions)"
description = """I Can't Control My Reactions - Watch till the end! 😱

#shorts #reactions #funny #viral #moments #cantcontrol #reactions"""

result = uploader.upload_video(
    video_file=Path(video_file),
    title=title,
    description=description,
    tags=["shorts", "reactions", "funny", "viral"],
    thumb_file=Path(thumb_file),
    privacy_status="unlisted",
)

print(f"Upload result: {result}")
print(f"YouTube ID: {result.get('id', 'unknown')}")
print(f"URL: https://www.youtube.com/watch?v={result.get('id', 'unknown')}")
