try:
    import torch
except ImportError:
    raise SystemExit("PyTorch is not installed. Run scripts/install_windows.ps1.")

print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA runtime:", torch.version.cuda)
    print("GPU:", torch.cuda.get_device_name(0))
    props = torch.cuda.get_device_properties(0)
    print("VRAM GiB:", round(props.total_memory / 1024**3, 2))
    try:
        x = torch.randn((512, 512), device="cuda", dtype=torch.float16)
        y = x @ x
        torch.cuda.synchronize()
        print("CUDA smoke test: PASS", tuple(y.shape))
        del x, y
    except Exception as exc:
        raise SystemExit(f"CUDA smoke test failed: {type(exc).__name__}: {exc}") from exc
else:
    print("CUDA not available. Check the NVIDIA driver and the installed PyTorch CUDA wheel.")
