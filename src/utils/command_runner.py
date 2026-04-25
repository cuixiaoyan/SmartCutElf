"""
Subprocess helpers for FFmpeg-style jobs.

Keeps heavy media commands globally throttled and cancellable so batch-level
and segment-level parallelism do not multiply into too many FFmpeg processes.
"""

import subprocess
import threading
from typing import List, Optional

from utils.config import get_config
from utils.logger import setup_logger


logger = setup_logger()

if hasattr(subprocess, "CREATE_NO_WINDOW"):
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
else:
    CREATE_NO_WINDOW = 0


_state_lock = threading.Lock()
_active_processes = set()
_semaphore = None
_semaphore_size = None


def _get_limit() -> int:
    config = get_config()
    configured = config.get("processing.max_ffmpeg_workers", None)
    if configured is None:
        configured = config.get("processing.max_segment_workers", 2)
    try:
        return max(1, int(configured))
    except (TypeError, ValueError):
        return 2


def _get_semaphore() -> threading.BoundedSemaphore:
    global _semaphore, _semaphore_size
    limit = _get_limit()
    with _state_lock:
        if _semaphore is None or _semaphore_size != limit:
            _semaphore = threading.BoundedSemaphore(limit)
            _semaphore_size = limit
        return _semaphore


def run_media_command(
    cmd: List[str],
    *,
    timeout: Optional[float] = None,
    encoding: str = "utf-8",
    errors: str = "ignore",
    check: bool = False,
    throttle: bool = True,
):
    """Run a subprocess, optionally under the global media-job throttle."""
    semaphore = _get_semaphore() if throttle else None
    if semaphore:
        semaphore.acquire()

    proc = None
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding=encoding,
            errors=errors,
            creationflags=CREATE_NO_WINDOW,
        )
        with _state_lock:
            _active_processes.add(proc)

        stdout, stderr = proc.communicate(timeout=timeout)
        result = subprocess.CompletedProcess(cmd, proc.returncode, stdout, stderr)
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, output=stdout, stderr=stderr
            )
        return result
    except subprocess.TimeoutExpired:
        if proc:
            proc.kill()
            stdout, stderr = proc.communicate()
            return subprocess.CompletedProcess(cmd, -9, stdout, stderr)
        raise
    finally:
        if proc:
            with _state_lock:
                _active_processes.discard(proc)
        if semaphore:
            semaphore.release()


def cancel_active_media_commands():
    """Terminate all currently running registered media commands."""
    with _state_lock:
        processes = list(_active_processes)

    for proc in processes:
        try:
            if proc.poll() is None:
                proc.terminate()
        except Exception as e:
            logger.warning(f"终止媒体进程失败: {e}")

    for proc in processes:
        try:
            if proc.poll() is None:
                proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
