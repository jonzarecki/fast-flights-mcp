import subprocess
import time
from pathlib import Path


def test_npm_install_and_node_start(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    subprocess.run(['npm','install', str(repo_root)], cwd=tmp_path, check=True)

    node_entry = tmp_path / 'node_modules' / 'fast-flights-mcp' / 'index.js'
    assert node_entry.exists()

    proc = subprocess.Popen(['node', str(node_entry)], cwd=tmp_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1)
        running = proc.poll() is None
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    assert running
