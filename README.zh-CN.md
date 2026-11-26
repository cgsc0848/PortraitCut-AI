# PortraitCut AI

[English](README.md) · **简体中文**

**面向 Windows + NVIDIA 显卡的本地批量人物抠图桌面软件。**

> **当前状态：MVP Alpha。** 这是开发预览版，不是 Photoshop 的完整替代品。CUDA 推理、真实照片边缘质量和打包结果仍需在 Windows + RTX 4070 实机验证。

![PortraitCut AI 桌面界面概念图](docs/gui-concept.svg)

*这是 GUI 设计概念图，不是当前运行程序的真实截图。*

## 目标功能

- 导入人物照片文件夹，可选择递归子文件夹。
- 使用 BiRefNet-HR-matting 本地推理，每次处理一张图片。
- 优先 NVIDIA CUDA + FP16；发生 CUDA 显存不足时，逐级降低模型输入尺寸重试。
- 保留原图 RGB，只将模型预测蒙版用作 PNG Alpha 通道。
- 输出透明 PNG，不覆盖原始文件。
- 单张失败不会中断整批任务，并记录每张图片的处理结果。
- 图片处理留在本机；首次使用时将模型下载到本地 Hugging Face 缓存。

## 预期效果示意

### 透明 PNG 合成概念

![透明 PNG 结果示意](docs/transparency-concept.svg)

*这是合成插画。棋盘格代表透明区域，不是 AI 模型实测输出。*

### 质量验证关注点

![抠图质量验证类别](docs/quality-validation-cases.svg)

*这些合成图用于说明后续需要测试的边缘场景：碎发、白衣服对白背景、薄纱/半透明材质。不是模型实测结果。*

## 当前兼容版本基线

| 组件 | 项目基线 | 说明 |
|---|---|---|
| 操作系统 | Windows 10/11 x64 | 桌面目标平台 |
| Python | 3.11 x64 | 当前打包基线 |
| PyTorch | 2.5.1 | 使用 CUDA 12.1 wheel |
| torchvision | 0.20.1 | 与 PyTorch 2.5.1 配套 |
| CUDA runtime | 12.1 wheel | 仍需 NVIDIA 驱动；通常不需要另装 CUDA Toolkit |
| Transformers | 5.0.0（固定版本） | 与固定的 BiRefNet 模型代码兼容修正配套 |
| timm | >=1.0.23 | 上游模型代码依赖 |
| NumPy | 1.26.4 | 为上游兼容暂时固定在 NumPy 2 以下 |

BiRefNet-HR-matting 上游模型卡给出的 Transformers 加载方式使用 trust_remote_code=True。仓库将模型代码固定在 app/engine/birefnet.py 中的 revision：5d6b6f8adcb5b417c871b1d84ceaae9871355b7f。这会执行远程模型仓库中的 Python 代码，首次运行前应审阅对应版本。

参考资料：[BiRefNet-HR 模型页](https://huggingface.co/ZhengPeng7/BiRefNet_HR-matting) · [固定模型代码版本](https://huggingface.co/ZhengPeng7/BiRefNet_HR-matting/tree/5d6b6f8adcb5b417c871b1d84ceaae9871355b7f) · [PyTorch 官方安装选择器](https://pytorch.org/get-started/locally/) · [PyTorch 历史版本安装矩阵](https://pytorch.org/get-started/previous-versions/)

当前选择的是保守的兼容基线，不代表这些软件包是最新版本。更高版本可能可以运行，但不能未经验证就静默替换；升级后应重新执行模型 smoke test 和质量集。

## Windows 源码安装

1. 安装 64 位 Python 3.11 和较新的 NVIDIA 显卡驱动。
2. 在仓库根目录打开 PowerShell。
3. 执行：

~~~powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install_windows.ps1
~~~

4. 启动桌面程序：

~~~powershell
.\.venv\Scripts\python.exe -m app.main
~~~

5. 检查 CUDA runtime 和 GPU 张量运算：

~~~powershell
.\.venv\Scripts\python.exe scripts\verify_gpu.py
~~~

第一次加载模型需要联网下载文件。模型缓存完成后，推理在本机运行。不要在同一个虚拟环境里再安装第二套 Python / PyTorch。

## 构建独立 Windows 运行目录

执行 scripts/build_windows.ps1。构建结果位于 dist/PortraitCutAI/，发布或拷贝时要保留整个文件夹。该运行目录包含 Python 解释器和 Python 依赖；目标机器仍需安装 NVIDIA 显卡驱动。模型权重放在用户 Hugging Face 缓存目录，第一次运行时下载。因此，当前版本**应用代码和 Python 库可独立运行，但首次启动仍需联网下载模型，并非完全离线安装包**。

PyInstaller 构建与操作系统、Python 版本和位数相关，因此应在目标 Windows 环境构建。当前先采用 **onedir** 目录模式，便于排错和检查依赖，不急于压成单个 exe。

## 批量任务保护与行为

- 单张顺序推理，不会为一个批次创建多个模型副本。
- 单张图片最大 **5000 万像素**。超大图或损坏文件会单独失败并记录。
- 单批最多扫描 **10,000 张图片**。更大的任务请拆分文件夹。
- 可选递归扫描子文件夹。
- 输出保留相对目录结构，统一输出 PNG。不会覆盖已存在文件；重名时自动增加后缀。
- 默认显存降级顺序：2048 → 1792 → 1536 → 1280 → 1024，实际起点由用户质量设置决定。
- 取消任务会在当前图片推理完成后停止，不会强行中断正在运行的 CUDA kernel。
- 这些是软件保护上限，不代表已经测得的吞吐量极限。真正的极限压力测试仍需在目标 Windows 电脑上完成。

## 运行测试

~~~powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
~~~

GitHub Actions 在 Windows 上执行 CPU-safe 测试。CI 通过不等于 CUDA 推理、真实发丝边缘质量或打包程序已经在你的显卡上通过。

## 仓库结构

~~~text
app/
  core/        图片读写、Alpha 导出和批处理
  engine/      模型适配器（BiRefNet-HR）
  ui/          PySide6 桌面界面
scripts/       Windows 安装、GPU 检查和打包
tests/         CPU-safe 回归测试
docs/          GUI 概念图和合成验证示例
models/        模型下载与许可说明（不存储权重）
~~~

你另行上传的白底 JavaScript 抠图工具已经过代码审阅，但**当前尚未迁移到本仓库，也没有接入桌面运行流程**。后续需要单独迁移源码并审查接口，才能作为可选补充模式。

## 隐私与安全

- 不要提交个人照片、模型缓存、访问令牌、API key、密码或私钥。
- 公开仓库原则上只放源码与合成示例图片。
- 建议在 GitHub **Settings → Security & analysis** 中启用 Dependabot alerts、Secret scanning、Push protection 和 CodeQL（按账号方案可用性）。
- 仅搜索当前文件不等于扫描完整 Git 历史。如果曾经提交过真实密钥，即使后来删除，也必须先轮换凭据。
- 参见 [SECURITY.md](SECURITY.md)。

## 尚未完成

- MultiMatte 独立推理适配器尚未完成。
- 原有白底抠图算法尚未迁移到桌面应用中。
- 画笔式蒙版修复、前后对比滑块、预设和完整历史记录尚未完成。
- 需要真实人物照片质量集和 RTX 4070 压力测试。
- GUI 概念图不是最终运行程序的截图。
- 尚未发布签名安装包或正式 Release。

## 许可证

本项目根目录尚未选择统一许可证。第三方依赖、模型代码和模型权重分别适用各自的许可条款。未来迁移白底工具代码时，会保留其独立许可证。
