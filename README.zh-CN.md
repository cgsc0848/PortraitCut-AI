# PortraitCut AI

Windows + NVIDIA 本地批量人物抠图桌面软件。

> 当前阶段：MVP Alpha。桌面界面、批量处理、透明 PNG 合成和 BiRefNet-HR 适配器已进入代码库；仍需在 Windows + RTX 4070 实机验证 CUDA、显存与模型质量。尚未达到 Photoshop 人工精修的等效水平。

## 功能

- PySide6 独立桌面界面
- BiRefNet-HR-matting 主模型，CUDA 可用时优先使用 FP16
- 单张顺序处理批量图片，降低显存峰值
- JPG/JPEG/PNG/WebP/BMP/TIFF 输入，RGBA PNG 输出
- 保留原图 RGB，只将预测 matte 用作 Alpha
- 单张失败不会中止整批任务
- 可选边缘颜色去污染（会修改边缘 RGB）

## Windows 安装

1. 安装 64 位 Python 3.11。
2. 在 PowerShell 运行：
   ```powershell
   .\\scripts\\install_windows.ps1
   ```
3. 从 PyTorch 官方选择器安装与你的 NVIDIA 驱动匹配的 CUDA 版 PyTorch：https://pytorch.org/get-started/locally/
4. 安装 AI 依赖并启动：
   ```powershell
   .\\.venv\\Scripts\\python.exe -m pip install -r requirements-ai.txt
   .\\.venv\\Scripts\\python.exe -m app.main
   ```
5. 可选：检查 CUDA 是否可用：
   ```powershell
   .\\.venv\\Scripts\\python.exe scripts\\verify_gpu.py
   ```

## 当前模型

- BiRefNet-HR-matting：`ZhengPeng7/BiRefNet_HR-matting`
- 模型 revision 固定在 `app/engine/birefnet.py`，避免上游远程代码无意变化。
- 模型加载使用 `trust_remote_code=True`。这会执行模型仓库中的 Python 代码；首次加载前请审阅固定 revision 的代码。不要在含敏感数据的环境里盲目运行未审查的远程代码。
- 模型权重不提交到 Git。模型代码、权重和第三方依赖的许可需要分别核实。

## 运行测试

```powershell
.\\.venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt
.\\.venv\\Scripts\\python.exe -m pytest -q
```

GitHub Actions 运行 CPU-safe 单元测试；CI 通过不代表 NVIDIA CUDA 实机测试通过。

## 已知限制

- 当前 UI 是第一版批量工具，不包含画笔式蒙版修复、图像对比滑块和完整模型管理器。
- MultiMatte 尚未接入独立推理 API。
- BiRefNet 推理采用固定方形输入预处理；高分辨率小目标/发丝效果需要通过真实数据集评估。
- 原始白底抠图代码尚未迁移到本仓库，需单独核查其许可证和接口后再迁移。
- 尚未发布 Windows 安装包。
- 不保证达到 Photoshop 人工精修水平；复杂发丝、半透明布料、低对比度衣物仍需专项评估。

## 许可证

本项目根目录暂未选择统一许可证。第三方依赖和模型权重有各自的许可条款。
