from pathlib import Path
from threading import Event
from PIL import Image

from app.core.batch import run_batch
from app.core.matte import MatteEngine, MatteResult


class DummyEngine(MatteEngine):
    name = "test-engine"

    def predict(self, image: Image.Image) -> MatteResult:
        return MatteResult(Image.new("L", image.size, 200), self.name, 512)


def test_batch_writes_png_and_continues_after_bad_file(tmp_path: Path):
    source = tmp_path / "input"
    output = tmp_path / "output"
    source.mkdir()
    Image.new("RGB", (8, 8), "red").save(source / "good.jpg")
    (source / "broken.png").write_bytes(b"broken")
    report = run_batch(source, output, DummyEngine())
    assert report.succeeded == 1
    assert report.failed == 1
    assert (output / "good.png").exists()


def test_batch_rejects_output_inside_input(tmp_path: Path):
    source = tmp_path / "input"
    source.mkdir()
    try:
        run_batch(source, source / "out", DummyEngine())
    except ValueError as exc:
        assert "Output directory" in str(exc)
    else:
        raise AssertionError("Expected output directory validation to fail")


def test_batch_can_cancel_before_next_item(tmp_path: Path):
    source = tmp_path / "input"
    output = tmp_path / "output"
    source.mkdir()
    Image.new("RGB", (8, 8), "red").save(source / "a.png")
    cancel = Event()
    cancel.set()
    report = run_batch(source, output, DummyEngine(), cancel_event=cancel)
    assert report.cancelled is True
    assert report.total == 0
