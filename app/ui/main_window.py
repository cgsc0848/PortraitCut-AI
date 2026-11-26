from __future__ import annotations

from pathlib import Path
from threading import Event

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressBar,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.core.batch import BatchReport, FileResult, run_batch
from app.core.image_io import discover_images
from app.engine.birefnet import BiRefNetHREngine


STYLESHEET = """
QMainWindow, QWidget { background:#F3F6FA; color:#1D2B3D; font-family:"Segoe UI"; font-size:10pt; }
QGroupBox { background:#FFFFFF; border:1px solid #DFE6EF; border-radius:12px; margin-top:12px; padding:16px 12px 12px; font-weight:600; }
QGroupBox::title { subcontrol-origin:margin; left:14px; padding:0 5px; color:#5F7187; }
QLineEdit, QComboBox { background:#FFFFFF; border:1px solid #D5DEE9; border-radius:8px; padding:9px 11px; min-height:20px; }
QLineEdit:focus, QComboBox:focus { border:1px solid #367CC1; }
QPushButton { background:#E8EFF7; color:#24496E; border:0; border-radius:9px; padding:10px 16px; font-weight:600; }
QPushButton:hover { background:#DCE8F4; }
QPushButton:disabled { color:#9AA7B5; background:#E9EDF2; }
QPushButton#RunButton { background:#216BC1; color:white; min-height:24px; font-size:11pt; }
QPushButton#RunButton:hover { background:#185DAE; }
QPushButton#CancelButton { background:#FCE8E6; color:#A33C32; }
QProgressBar { background:#E8EDF3; border:0; border-radius:6px; height:12px; text-align:center; }
QProgressBar::chunk { background:#3282CC; border-radius:6px; }
QTableWidget { background:white; border:1px solid #DFE6EF; border-radius:10px; gridline-color:#EDF1F5; selection-background-color:#E7F0FB; selection-color:#1D2B3D; }
QHeaderView::section { background:#F7F9FC; color:#63748A; padding:9px; border:0; border-bottom:1px solid #DFE6EF; font-weight:600; }
QCheckBox { spacing:7px; color:#42546A; }
QLabel#Title { font-size:22pt; font-weight:700; color:#1B2B40; }
QLabel#Subtitle { color:#687A90; }
QLabel#StatusChip { background:#E1F4EC; color:#17664B; border-radius:10px; padding:8px 12px; font-weight:700; }
QLabel#Muted { color:#6F8095; }
"""


class BatchWorker(QThread):
    progress = Signal(int, int, object)
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, input_dir: Path, output_dir: Path, resolution: int,
                 recursive: bool, refine_rgb: bool):
        super().__init__()
        self.input_dir, self.output_dir = input_dir, output_dir
        self.resolution, self.recursive = resolution, recursive
        self.refine_rgb = refine_rgb
        self.cancel_event = Event()

    def cancel(self):
        self.cancel_event.set()

    def run(self):
        fallbacks = {
            2048: (2048, 1792, 1536, 1280, 1024),
            1792: (1792, 1536, 1280, 1024),
            1536: (1536, 1280, 1024),
            1280: (1280, 1024),
            1024: (1024,),
        }
        try:
            engine = BiRefNetHREngine(resolutions=fallbacks[self.resolution])
            engine.load()

            def on_progress(done: int, total: int, result: FileResult):
                self.progress.emit(done, total, result)

            report = run_batch(
                self.input_dir, self.output_dir, engine,
                recursive=self.recursive, refine_rgb=self.refine_rgb,
                progress=on_progress, cancel_event=self.cancel_event,
            )
            self.completed.emit(report)
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PortraitCut AI")
        self.resize(1040, 760)
        self.setMinimumSize(850, 640)
        self.worker: BatchWorker | None = None
        self._table_rows: dict[str, int] = {}
        self._build_ui()
        self.setStyleSheet(STYLESHEET)
        self._update_runtime_status()

    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(14)

        top = QHBoxLayout()
        title_block = QVBoxLayout()
        title = QLabel("PortraitCut AI")
        title.setObjectName("Title")
        subtitle = QLabel("本地 AI 人像抠图 · 批量处理 · 透明 PNG")
        subtitle.setObjectName("Subtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        top.addLayout(title_block)
        top.addStretch(1)
        self.runtime_status = QLabel("正在检测 AI 运行环境…")
        self.runtime_status.setObjectName("StatusChip")
        top.addWidget(self.runtime_status)
        root.addLayout(top)

        folders = QGroupBox("文件夹")
        folder_grid = QGridLayout(folders)
        folder_grid.setHorizontalSpacing(10)
        folder_grid.setVerticalSpacing(12)
        folder_grid.addWidget(QLabel("输入目录"), 0, 0)
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("选择包含 JPG / PNG / WebP / TIFF 图片的文件夹")
        folder_grid.addWidget(self.input_edit, 0, 1)
        browse_input = QPushButton("浏览…")
        browse_input.clicked.connect(self.choose_input)
        folder_grid.addWidget(browse_input, 0, 2)
        folder_grid.addWidget(QLabel("输出目录"), 1, 0)
        self.output_edit = QLineEdit(str(Path.home() / "Pictures" / "PortraitCut-Output"))
        folder_grid.addWidget(self.output_edit, 1, 1)
        browse_output = QPushButton("浏览…")
        browse_output.clicked.connect(self.choose_output)
        folder_grid.addWidget(browse_output, 1, 2)
        self.scan_button = QPushButton("扫描图片")
        self.scan_button.clicked.connect(self.scan_input)
        folder_grid.addWidget(self.scan_button, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.scan_summary = QLabel("尚未选择输入目录")
        self.scan_summary.setObjectName("Muted")
        folder_grid.addWidget(self.scan_summary, 2, 2)
        root.addWidget(folders)

        settings = QGroupBox("抠图设置")
        grid = QGridLayout(settings)
        grid.addWidget(QLabel("模型"), 0, 0)
        model_label = QLabel("BiRefNet-HR-matting")
        model_label.setStyleSheet("font-weight:700;color:#24496E;")
        grid.addWidget(model_label, 0, 1)
        grid.addWidget(QLabel("质量 / 模型输入尺寸"), 0, 2)
        self.resolution = QComboBox()
        for value in (1536, 1792, 2048, 1280, 1024):
            self.resolution.addItem(f"{value} × {value}", value)
        self.resolution.setCurrentIndex(self.resolution.findData(2048))
        grid.addWidget(self.resolution, 0, 3)
        self.recursive = QCheckBox("包含子文件夹")
        grid.addWidget(self.recursive, 1, 0, 1, 2)
        self.refine = QCheckBox("边缘颜色去污染（会改变边缘 RGB）")
        grid.addWidget(self.refine, 1, 2, 1, 2)
        hint = QLabel("单张顺序推理；显存不足时逐级降低输入尺寸。原图不会覆盖，输出为透明 PNG。")
        hint.setWordWrap(True)
        hint.setObjectName("Muted")
        grid.addWidget(hint, 2, 0, 1, 4)
        root.addWidget(settings)

        queue_group = QGroupBox("批量任务")
        queue_layout = QVBoxLayout(queue_group)
        self.queue_table = QTableWidget(0, 4)
        self.queue_table.setHorizontalHeaderLabels(["文件名", "状态", "实际尺寸", "结果信息"])
        modes = (
            QHeaderView.ResizeMode.Stretch,
            QHeaderView.ResizeMode.ResizeToContents,
            QHeaderView.ResizeMode.ResizeToContents,
            QHeaderView.ResizeMode.Stretch,
        )
        for col, mode in enumerate(modes):
            self.queue_table.horizontalHeader().setSectionResizeMode(col, mode)
        self.queue_table.verticalHeader().setVisible(False)
        self.queue_table.setAlternatingRowColors(True)
        self.queue_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.queue_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        queue_layout.addWidget(self.queue_table)
        root.addWidget(queue_group, 1)

        footer = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress_label = QLabel("等待开始")
        self.progress_label.setObjectName("Muted")
        footer.addWidget(self.progress, 1)
        footer.addWidget(self.progress_label)
        root.addLayout(footer)

        actions = QHBoxLayout()
        self.info_label = QLabel("所有图片均在本机处理；模型首次加载需要联网下载。")
        self.info_label.setObjectName("Muted")
        actions.addWidget(self.info_label, 1)
        self.cancel_button = QPushButton("取消任务")
        self.cancel_button.setObjectName("CancelButton")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_batch)
        actions.addWidget(self.cancel_button)
        self.run_button = QPushButton("开始批量抠图")
        self.run_button.setObjectName("RunButton")
        self.run_button.setMinimumWidth(190)
        self.run_button.clicked.connect(self.start_batch)
        actions.addWidget(self.run_button)
        root.addLayout(actions)
        self.setCentralWidget(central)

    def _update_runtime_status(self):
        try:
            import torch
            if torch.cuda.is_available():
                self.runtime_status.setText(f"CUDA 已就绪 · {torch.cuda.get_device_name(0)}")
            else:
                self.runtime_status.setText("未检测到 CUDA · 将使用 CPU")
                self.runtime_status.setStyleSheet(
                    "background:#FFF3CD;color:#805B13;border-radius:10px;padding:8px 12px;font-weight:700;"
                )
        except Exception:
            self.runtime_status.setText("AI 依赖未安装")
            self.runtime_status.setStyleSheet(
                "background:#FCE8E6;color:#9B3931;border-radius:10px;padding:8px 12px;font-weight:700;"
            )

    def choose_input(self):
        path = QFileDialog.getExistingDirectory(self, "选择输入图片文件夹")
        if path:
            self.input_edit.setText(path)
            self.scan_input()

    def choose_output(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if path:
            self.output_edit.setText(path)

    def scan_input(self):
        try:
            images = discover_images(Path(self.input_edit.text()).expanduser(),
                                     recursive=self.recursive.isChecked())
        except Exception as exc:
            QMessageBox.warning(self, "扫描失败", str(exc))
            return
        self.scan_summary.setText(f"检测到 {len(images):,} 张图片")
        self._populate_queue(images)

    def _populate_queue(self, images: list[Path]):
        self.queue_table.setRowCount(0)
        self._table_rows.clear()
        preview = images[:500]
        self.queue_table.setRowCount(len(preview))
        for row, path in enumerate(preview):
            self._table_rows[str(path)] = row
            values = (path.name, "等待中", "—", str(path.parent))
            for col, value in enumerate(values):
                self.queue_table.setItem(row, col, QTableWidgetItem(value))
        if len(images) > len(preview):
            self.info_label.setText(f"队列预览显示前 500 张；实际任务共 {len(images):,} 张。")

    def start_batch(self):
        source = Path(self.input_edit.text()).expanduser()
        target = Path(self.output_edit.text()).expanduser()
        if not source.is_dir():
            QMessageBox.warning(self, "输入目录无效", "请选择存在的图片文件夹。")
            return
        if target.resolve() == source.resolve() or source.resolve() in target.resolve().parents:
            QMessageBox.warning(self, "输出目录无效", "输出目录不能与输入目录相同或位于输入目录内部。")
            return
        try:
            images = discover_images(source, recursive=self.recursive.isChecked())
        except Exception as exc:
            QMessageBox.warning(self, "任务无法启动", str(exc))
            return
        if not images:
            QMessageBox.information(self, "没有图片", "输入目录中没有受支持的图片。")
            return

        self._populate_queue(images)
        for row in range(self.queue_table.rowCount()):
            self.queue_table.item(row, 1).setText("排队中")
        self.progress.setMaximum(len(images))
        self.progress.setValue(0)
        self.progress_label.setText(f"0 / {len(images):,}")
        self.run_button.setEnabled(False)
        self.scan_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.info_label.setText("首次运行可能需要下载模型；请保持网络连接。")
        self.worker = BatchWorker(
            source, target, int(self.resolution.currentData()),
            self.recursive.isChecked(), self.refine.isChecked(),
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.completed.connect(self.on_completed)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def on_progress(self, done: int, total: int, result: FileResult):
        self.progress.setMaximum(max(total, 1))
        self.progress.setValue(done)
        self.progress_label.setText(f"{done:,} / {total:,}")
        row = self._table_rows.get(str(result.source))
        if row is not None:
            self.queue_table.item(row, 1).setText("完成" if result.success else "失败")
            self.queue_table.item(row, 3).setText(result.message)

    def on_completed(self, report: BatchReport):
        self._finish_worker()
        state = "已取消" if report.cancelled else "处理完成"
        self.progress_label.setText(
            f"{state} · 成功 {report.succeeded:,} · 失败 {report.failed:,}"
        )
        if report.cancelled:
            for row in range(self.queue_table.rowCount()):
                if self.queue_table.item(row, 1).text() == "排队中":
                    self.queue_table.item(row, 1).setText("已取消")
        self.info_label.setText(f"输出目录：{self.output_edit.text()}")
        QMessageBox.information(
            self, state,
            f"已处理：{report.total:,}\\n成功：{report.succeeded:,}\\n失败：{report.failed:,}\\n输出：{self.output_edit.text()}",
        )

    def on_failed(self, message: str):
        self._finish_worker()
        QMessageBox.critical(self, "任务启动失败", message)
        self.progress_label.setText("任务失败")

    def _finish_worker(self):
        self.run_button.setEnabled(True)
        self.scan_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None

    def cancel_batch(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.cancel()
            self.cancel_button.setEnabled(False)
            self.progress_label.setText("正在停止；当前图片处理完成后退出…")

    def closeEvent(self, event: QCloseEvent):
        if self.worker is not None and self.worker.isRunning():
            self.worker.cancel()
            if not self.worker.wait(5000):
                QMessageBox.warning(self, "任务仍在运行",
                                    "当前图片仍在模型推理。请等待处理结束后再关闭软件。")
                event.ignore()
                return
        event.accept()
