from __future__ import annotations

import csv
import os
import socketserver
import sys
import tarfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sim_datasets import utils  # noqa: E402


def _write_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def test_get_datasets_list_supports_srbench2025() -> None:
    datasets = utils.get_datasets_list("srbench2025")
    assert len(datasets) == 24
    assert "srbench2025/blackbox/1028_SWD" in datasets
    assert "srbench2025/firstprinciples/first_principles_ideal_gas" in datasets


def test_download_dataset_tracks_failures_and_honors_cache_dir(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(utils, "get_datasets_list", lambda _: ["ok/ds", "bad/ds"])

    def fake_download(dataset_name: str, source: str | None = None, proxy: str = "", cache_dir=None):
        if dataset_name == "ok/ds":
            return {
                "dataset_name": dataset_name,
                "cache_path": str(Path(cache_dir) / dataset_name),
                "files": {"package.tar.gz": {"path": "dummy", "error": None}},
                "success": True,
            }
        return {
            "dataset_name": dataset_name,
            "cache_path": str(Path(cache_dir) / dataset_name),
            "files": {"package.tar.gz": {"path": None, "error": "HTTP 404"}},
            "success": False,
        }

    monkeypatch.setattr(utils, "download_single_dataset", fake_download)

    cache_dir = tmp_path / "cache"
    result = utils.download_dataset("srbench2025", source="modelscope", cache_dir=cache_dir)

    assert result["cache_dir"] == str(cache_dir)
    assert result["downloaded"] == ["ok/ds"]
    assert result["failed"] == ["bad/ds"]
    assert result["success_count"] == 1
    assert result["failed_count"] == 1


def test_download_single_dataset_supports_base_url_override(tmp_path: Path, monkeypatch) -> None:
    source_root = tmp_path / "source_root"
    dataset_rel = Path("srbench2025/blackbox/1028_SWD")
    dataset_dir = source_root / dataset_rel
    dataset_dir.mkdir(parents=True, exist_ok=True)

    _write_csv(dataset_dir / "train.csv", ["x0", "target"], [[1.0, 2.0], [2.0, 4.0]])
    _write_csv(dataset_dir / "valid.csv", ["x0", "target"], [[3.0, 6.0]])
    _write_csv(dataset_dir / "id_test.csv", ["x0", "target"], [[4.0, 8.0]])
    (dataset_dir / "metadata.yaml").write_text(
        "dataset:\n  name: srbench2025__blackbox__1028_SWD\n",
        encoding="utf-8",
    )

    package_path = dataset_dir / "package.tar.gz"
    with tarfile.open(package_path, "w:gz") as tar:
        for name in ["train.csv", "valid.csv", "id_test.csv", "metadata.yaml"]:
            tar.add(dataset_dir / name, arcname=name)

    handler = partial(SimpleHTTPRequestHandler, directory=str(source_root))
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        monkeypatch.setenv("SIM_DATASETS_MODELSCOPE_BASE_URL", f"http://127.0.0.1:{port}")

        cache_dir = tmp_path / "cache"
        result = utils.download_single_dataset(
            "srbench2025/blackbox/1028_SWD",
            source="modelscope",
            cache_dir=cache_dir,
        )

        httpd.shutdown()
        thread.join(timeout=5)

    assert result["success"] is True
    extracted_dir = cache_dir / dataset_rel
    assert (extracted_dir / "train.csv").exists()
    assert (extracted_dir / "valid.csv").exists()
    assert (extracted_dir / "id_test.csv").exists()
    assert (extracted_dir / "metadata.yaml").exists()
    assert not (extracted_dir / "package.tar.gz").exists()
