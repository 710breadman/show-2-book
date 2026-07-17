from __future__ import annotations

import shutil
import sys
from pathlib import Path


def get_ffmpeg_exe() -> str:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    project_deps = Path(__file__).resolve().parents[1] / ".deps"
    if project_deps.exists() and str(project_deps) not in sys.path:
        sys.path.insert(0, str(project_deps))

    try:
        import imageio_ffmpeg
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "FFmpeg is unavailable. Install imageio-ffmpeg into the project's .deps folder."
        ) from exc
    return imageio_ffmpeg.get_ffmpeg_exe()
