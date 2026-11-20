"""On Windows, run with Python 3: python reproduce.py > measurements.json"""
import json
import platform
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


def measure(shell, folder):
    executable = shutil.which(shell)
    if executable is None:
        raise SystemExit(f"Missing executable: {shell}")
    command = """Set-Content -LiteralPath sample.json -Encoding utf8 -NoNewline -Value '{"ok":true}'
$PSVersionTable.PSVersion.ToString()"""
    version = subprocess.check_output(
        [executable, "-NoProfile", "-NonInteractive", "-Command", command],
        cwd=folder, text=True,
    ).strip()
    path = folder / "sample.json"
    results = {}
    for mode, encoding in [("r", "utf-8"), ("r", "utf-8-sig"), ("rb", None)]:
        try:
            with path.open(mode, encoding=encoding) as stream:
                result = json.load(stream)
        except (ValueError, UnicodeError) as error:
            result = {"error": type(error).__name__, "message": str(error)}
        results[encoding or mode] = result
    return {"shell": shell, "version": version, "hex": path.read_bytes().hex(" "),
            "reads": results}


if __name__ == "__main__":
    with TemporaryDirectory() as workspace:
        runs = []
        for shell in ("powershell.exe", "pwsh.exe"):
            folder = Path(workspace) / shell
            folder.mkdir()
            runs.append(measure(shell, folder))
    print(json.dumps({"python": platform.python_version(), "os": platform.system(),
                      "runs": runs}, ensure_ascii=True, indent=2))
