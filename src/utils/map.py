import shutil
import subprocess

from src.exc import MissingDependency


def gen_map(cols, lines):
    if not shutil.which("asciiworld"):
        raise MissingDependency("asciiworld")

    # Lazy af (◕▽◕✿)
    res = subprocess.run(
        ["asciiworld", "-w", str(cols), "-h", str(lines)], stdout=subprocess.PIPE
    )

    return res.stdout.decode("utf-8")
