# PortraitCut AI

Windows + NVIDIA 本地批量人物抠图桌面软件。

> 当前阶段：MVP Alpha。桌面界面、批量处理、透明 PNG 合成和 BiRefNet-HR 适配器已进入代码库；仍需在 Windows + RTX 4070 实机验证 CUDA、显存与模型质量。尚未达到 Photoshop 人工精修的等效水平。

## 功能目标

- PySide6 独立桌面界面
- BiRefNet-HR-matting 主模型，CUDA 可用时优先使用 FP16
- 单张顺序处理批量图片，降低显存峰值
- JPG/JPEG/PNG/WebP/BMP/TIFF 输入，RGBA PNG 输出
- 保留原图 RGB，只将预测 matte 用作 Alpha
- 单张失败不会中止整批任务
- 原始白底算法保存在 `legacy/white-bg-cutout`，作为专项算法参考

## Windows 安装

1. 安装 64 位 Python 3.11。
2. 在 PowerShell 运行：
   ```powershell
   .\scripts\install_windows.ps1
   ```
3. 按脚本提示安装与你的驱动匹配的 PyTorch CUDA 版本。请从 PyTorch 官方安装选择器获取命令：https://pytorch.org/get-started/locally/
4. 激活虚拟环境并启动：
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python -m app.main
   ```

## 当前模型

- BiRefNet-HR-matting：`ZhengPeng7/BiRefNet_HR-matting`
- 模型 revision 固定在 `app/engine/birefnet.py`，避免上游远程代码无意变化。
- 模型加载使用 `trust_remote_code=True`。这会执行模型仓库中的 Python 代码；首次加载前请审阅固定 revision 的代码。不要在含敏感数据的环境里盲目运行未审查的远程代码。
- 模型权重不提交到 Git。模型文件、代码和第三方依赖的许可需要分别核实。

## 运行测试

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -q
```

CI 当前运行 CPU-safe 单元测试；GitHub Actions 通过不代表 NVIDIA CUDA 实机测试通过。

## 已知限制

- 当前 UI 是第一版批量工具，不包含画笔式蒙版修复、图像对比滑块和完整模型管理器。
- MultiMatte 尚未接入独立推理 API。
- BiRefNet 推理采用固定方形输入预处理；高分辨率小目标/发丝的效果必须通过真实数据集评估。
- 自动显存降级只处理可识别的 CUDA OOM；其他异常会按文件报告。
- 目前尚未发布 Windows 安装包。

## 安全与隐私

所有图片处理目标为本地运行。首次模型下载需要网络；模型下载完成后推理可离线运行。不要提交个人照片、模型权重、访问令牌或密钥到仓库。

## 许可证

项目整体许可证尚未选定。原始白底算法目录保留其上游 LICENSE。添加项目根许可证前，请先确认新代码和所有依赖的兼容性。
