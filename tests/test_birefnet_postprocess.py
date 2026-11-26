from PIL import Image

from app.engine.birefnet import BiRefNetHREngine


def test_resolution_validation():
    try:
        BiRefNetHREngine(resolutions=(4096,))
    except ValueError:
        pass
    else:
        raise AssertionError("out-of-range model resolution should be rejected")
