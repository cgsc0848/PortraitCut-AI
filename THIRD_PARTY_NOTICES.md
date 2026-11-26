# Third-party software and model notices

PortraitCut AI's own source code is licensed under the Apache License 2.0.
That project license does not replace or relicense third-party packages, model
code, model weights, or other separately licensed materials.

The list below records the principal runtime components currently referenced by
the project. It is not a complete generated Software Bill of Materials (SBOM).
Before publishing a packaged build, regenerate and review the full dependency
license inventory for the exact lockfile/build environment.

## BiRefNet-HR-matting model

- Project: [ZhengPeng7/BiRefNet_HR-matting](https://huggingface.co/ZhengPeng7/BiRefNet_HR-matting)
- Model repository metadata currently declares the MIT License.
- Pinned model-code revision used by this app:
  `5d6b6f8adcb5b417c871b1d84ceaae9871355b7f`
- Model weights are downloaded separately at runtime and are not committed here.
- The upstream model repository's license and notices apply to its code and weights.
- Upstream authors: Zheng Peng and BiRefNet contributors. Please cite the BiRefNet
  paper as requested by the upstream project.

## BiRefNet source code and foreground refinement

- Source: [ZhengPeng7/BiRefNet image_proc.py](https://github.com/ZhengPeng7/BiRefNet/blob/main/image_proc.py)
- The BiRefNet source repository declares the MIT License. The application’s
  `refine_foreground_rgb` helper is adapted from the CPU foreground-colour
  refinement implementation in that file.
- Copyright notice from the upstream source: Copyright (c) 2024 ZhengPeng.
- The BiRefNet implementation credits PhotoRoom's
  [fast-foreground-estimation project](https://github.com/PhotoRoom/fast-foreground-estimation)
  and Marco Forte's paper, *Approximate Fast Foreground Colour Estimation*,
  ICIP 2021, DOI: [10.1109/ICIP42928.2021.9506164](https://doi.org/10.1109/ICIP42928.2021.9506164).
- The PhotoRoom GitHub repository currently has no declared repository license
  or LICENSE file in its default-branch tree. This project attributes the
  research/source reference through the BiRefNet implementation; it does not
  claim a separate license grant from PhotoRoom. Do not copy additional code
  directly from the PhotoRoom repository unless permission or an applicable
  license is confirmed.

## PySide6 / Qt for Python

- Project: [Qt for Python](https://doc.qt.io/qtforpython-6/)
- PySide6 is offered under LGPLv3, GPLv3 (and other applicable GPL terms for
  certain distributions/modules), or a commercial Qt license.
- This project uses the community PyPI distribution. The project's Apache-2.0
  license does not change Qt's license.
- If you redistribute a packaged application, review and satisfy the applicable
  LGPL/GPL obligations for the exact Qt modules and binaries you ship. In
  particular, LGPL distribution can require license notices, access to the
  corresponding Qt source and a practical way for recipients to replace/relink
  the Qt libraries. The current PyInstaller build script is a development
  packaging baseline, not a completed Qt redistribution-compliance package.
- Commercial distribution may require a commercial Qt license depending on
  how Qt is used and the applicable terms. Consult Qt's official licensing
  documentation before shipping a commercial binary.

## Other principal runtime dependencies

The application installs these projects as independent packages; each retains
its own license and notices:

- [PyTorch](https://github.com/pytorch/pytorch) — BSD-3-Clause for the main
  project; binary distributions may include separately licensed third-party
  components and their notices.
- [Transformers](https://github.com/huggingface/transformers) — Apache-2.0.
- [Pillow](https://github.com/python-pillow/Pillow) — HPND / Pillow license.
- [NumPy](https://github.com/numpy/numpy) — BSD-3-Clause.
- [OpenCV](https://github.com/opencv/opencv) — Apache-2.0.
- [SciPy](https://github.com/scipy/scipy) — BSD-3-Clause.
- [scikit-image](https://github.com/scikit-image/scikit-image) — BSD-3-Clause.
- Other packages in requirements files retain their respective upstream
  licenses. This list is intentionally not exhaustive.

## Important scope note

The separately supplied white-background JavaScript utility has not been
migrated into this repository. No license for that separate source is granted
by this repository's LICENSE file. If it is migrated later, its original
copyright and license must be preserved and reviewed independently.
