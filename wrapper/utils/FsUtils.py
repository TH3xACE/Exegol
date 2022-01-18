import re
import subprocess
from pathlib import Path, PurePosixPath

from wrapper.utils.ConstantConfig import ConstantConfig
from wrapper.utils.ExeLog import logger


def parseDockerVolumePath(source: str) -> Path:
    # Check if path is from Windows Docker Desktop
    matches = re.match(r"^/run/desktop/mnt/host/([a-z])(/.*)$", source, re.IGNORECASE)
    if matches:
        # Convert Windows Docker-VM style volume path to local OS path
        src_path = Path(f"{matches.group(1).upper()}:{matches.group(2)}")
        logger.debug(f"Windows style detected : {src_path}")
    else:
        # Remove docker mount path if exist
        src_path = PurePosixPath(source.replace('/run/desktop/mnt/host', ''))
    return src_path


def resolvPath(path: Path) -> str:
    """Resolv a filesystem path depending on the environment.
    On WSL, Windows PATH can be resolved using 'wslpath'."""
    if path is None:
        return None
    if ConstantConfig.wsl_environment:
        try:
            # Resolv Windows path on WSL environment
            p = subprocess.Popen(["wslpath", "-a", str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = p.communicate()
            logger.debug(f"Resolv path input: {path}")
            logger.debug(f"Resolv path output: {output}")
            if err != b'':
                # result is returned to STDERR when the translation didn't properly find a match
                logger.debug(f"Error on FS path resolution: {err}. Input path is probably a linux path.")
            else:
                return output.decode('utf-8').strip()
        except FileNotFoundError:
            logger.warning("Missing WSL tools: 'wslpath'. Skipping resolution.")
    return str(path)


def resolvStrPath(path: str) -> str:
    if path is None:
        return None
    return resolvPath(Path(path))