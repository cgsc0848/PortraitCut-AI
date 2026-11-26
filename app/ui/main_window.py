from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QProgressBar, QPushButton, QTextEdit,
    QVBoxLayout, QWidget,
)

from app.core.batch import run_batch
from app.engine.birefnet import BiRefNetHREngine


class BatchWorker(QThread):
    progress = Signal(int, int, str)
    completed = Signal(int, int, str)

    def __init__(self, input_dir: Path, output_dir: Path, resolution: int,
                 recursive: bool, refine_rgb: bool):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.resolution = resolution
        self.recursive = recursive
        self.refine_rgb = refine_rgb

    def run(self) -> None:
        try:
            fallbacks = {
                2048: (2048, 1792, 1536, 1280, 1024),
                1792: (1792, 1536, 1280, 1024),
                1536: (1536, 1280, 1024),
                1280: (1280, 1024),
                1024: (1024,),
            }
            engine = BiRefNetHREngine(resolutions=fallbacks[self.resolution])

            def on_progress(done: int, total: int, result) -> None:
                status = "OK" if result.success else "FAIL"
                self.progress.emit(
                    done, total, f"{status}  {result.source.name}: {result.message}"
                )

            report = run_batch(
                self.input_dir, self.output_dir, engine,
                recursive=self.recursive, refine_rgb=self.refine_rgb,
                progress=on_progress,
            )
            self.completed.emit(
                report.succeeded, report.failed, str(self.output_dir)
            )
        except Exception as exc:
            self.completed.emit(
                0, 0, f"Worker error: {type(exc).__name__}: {exc}"
            )


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PortraitCut AI")
        self.resize(860, 620)
        self.worker: BatchWorker | None = None

        root = QWidget()
        layout = QVBoxLayout(root)
        title = QLabel("PortraitCut AI  |  本地批量人物抠图")
        title.setStyleSheet("font-size: 22px; font-weight: 650; padding: 8px 0;")
        layout.addWidget(title)
        subtitle = QLabel(
            "BiRefNet-HR-matting · NVIDIA CUDA · Transparent PNG"
        )
        subtitle.setStyleSheet("color: #687386;")
        layout.addWidget(subtitle)

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("选择输入图片文件夹")
        input_row = QHBoxLayout()
        input_row.addWidget(self.input_edit)
        input_button = QPushButton("选择输入目录")
        input_button.clicked.connect(self.choose_input)
        input_row.addWidget(input_button)
        layout.addLayout(input_row)

        self.output_edit = QLineEdit(
            str(Path.home() / "Pictures" / "PortraitCut-Output")
        )
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_edit)
        output_button = QPushButton("选择输出目录")
        output_button.clicked.connect(self.choose_output)
        output_row.addWidget(output_button)
        layout.addLayout(output_row)

        options = QHBoxLayout()
        options.addWidget(QLabel("首选分辨率"))
        self.resolution = QComboBox()
        for value in (1536, 1792, 2048, 1280, 1024):
            self.resolution.addItem(str(value), value)
        self.resolution.setCurrentIndex(0)
        options.addWidget(self.resolution)

        self.recursive = QCheckBox("递归子文件夹")
        options.addWidget(self.recursive)
        self.refine = QCheckBox("边缘颜色去污染（会改变边缘 RGB）")
        self.refine.setChecked(False)
        options.addWidget(self.refine)
        layout.addLayout(options)

        notice = QLabel(
            "首次使用会下载 BiRefNet 模型。模型加载需要执行固定版本的远程模型代码；"
            "请先阅读 README 安全说明。每次只处理一张图片。"
        )
        notice.setWordWrap(True)
        notice.setStyleSheet(
            "background: #fff3cd; color: #664d03; padding: 10px; border-radius: 6px;"
        )
        layout.addWidget(notice)

        self.run_button = QPushButton("开始批量抠图")
        self.run_button.setMinimumHeight(42)
        self.run_button.clicked.connect(self.start_batch)
        layout.addWidget(self.run_button)
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        self.setCentralWidget(root)

    def choose_input(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择输入图片文件夹")
        if path:
            self.input_edit.setText(path)

    def choose_output(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if path:
            self.output_edit.setText(path)

    def start_batch(self) -> None:
        source = Path(self.input_edit.text()).expanduser()
        target = Path(self.output_edit.text()).expanduser()
        if not source.is_dir():
            QMessageBox.warning(self, "输入目录无效", "请选择存在的图片文件夹。")
            return
        if (
            source.resolve() == target.resolve()
            or source.resolve() in target.resolve().parents
        ):
            QMessageBox.warning(
                self, "输出目录无效",
                "输出目录不能与输入目录相同或位于输入目录内部。",
            )
            return

        self.run_button.setEnabled(False)
        self.progress.setValue(0)
        self.log.clear()
        self.log.append("准备加载模型；首次加载需要下载权重……")
        resolution = int(self.resolution.currentData())
        self.worker = BatchWorker(
            source, target, resolution,
            self.recursive.isChecked(), self.refine.isChecked(),
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.completed.connect(self.on_completed)
        self.worker.start()

    def on_progress(self, done: int, total: int, message: str) -> None:
        self.progress.setMaximum(max(total, 1))
        self.progress.setValue(done)
        self.log.append(message)

    def on_completed(self, succeeded: int, failed: int, detail: str) -> None:
        self.run_button.setEnabled(True)
        if failed == 0 and succeeded == 0:
            self.log.append(detail)
        else:
            self.log.append(
                f"完成：成功 {succeeded}，失败 {failed}。输出位置：{detail}"
            )
