try:
    import torch
except ImportError:
    raise SystemExit("PyTorch is not installed. Install a CUDA wheel from https://pytorch.org/get-started/locally/")

print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA runtime:", torch.version.cuda)
    print("GPU:", torch.cuda.get_device_name(0))
    print("VRAM GiB:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2))
else:
    print("No CUDA device detected. Check the NVIDIA driver and PyTorch wheel.")
