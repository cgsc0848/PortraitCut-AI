"""Offscreen GUI smoke tests; these tests never download or initialize the AI model."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_main_window_starts_without_loading_ai_model(qapp):
    window = MainWindow()
    try:
        assert window.windowTitle() == "PortraitCut AI"
        assert window.run_button.isEnabled()
        assert window.cancel_button.isEnabled() is False
        assert window.resolution.currentData() == 2048
        assert window.queue_table.columnCount() == 4
    finally:
        window.close()


def test_ui_has_safe_default_output_folder(qapp):
    window = MainWindow()
    try:
        assert window.output_edit.text().endswith("PortraitCut-Output")
        assert window.refine.isChecked() is False
        assert window.recursive.isChecked() is False
    finally:
        window.close()
