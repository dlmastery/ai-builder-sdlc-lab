"""Image-quality features and the difficulty predictor (plan B.9, spec §3 step 1)."""

from __future__ import annotations

import io
from typing import Any

import numpy as np
from PIL import Image, ImageFilter, ImageOps

FEATURES = ["blur", "contrast", "noise", "skew", "ink_density", "dark_fraction", "aspect"]


def quality_features(image: Image.Image) -> dict[str, float]:
    g = ImageOps.grayscale(image.convert("RGB"))
    long_side = max(g.size)
    if long_side > 1200:
        s = 1200 / long_side
        g = g.resize(
            (max(1, int(g.width * s)), max(1, int(g.height * s))), Image.Resampling.BILINEAR
        )
    a = np.asarray(g, dtype=np.float32) / 255.0
    # blur: variance of the Laplacian (low = blurry)
    lap = np.asarray(
        g.filter(ImageFilter.Kernel((3, 3), [0, 1, 0, 1, -4, 1, 0, 1, 0], scale=1)),
        dtype=np.float32,
    )
    blur = float(lap.var())
    contrast = float(a.std())
    # noise: residual after a small median filter
    med = np.asarray(g.filter(ImageFilter.MedianFilter(3)), dtype=np.float32) / 255.0
    noise = float(np.abs(a - med).mean())
    # skew: angle of the dominant text rows via row-projection variance over small rotations
    best, best_var = 0.0, -1.0
    for ang in (-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0):
        r = g.rotate(ang, resample=Image.Resampling.BILINEAR, fillcolor=255)
        prof = (255 - np.asarray(r, dtype=np.float32)).sum(axis=1)
        v = float(prof.var())
        if v > best_var:
            best, best_var = ang, v
    ink = float((a < 0.5).mean())
    dark = float((a < 0.2).mean())
    return {
        "blur": blur,
        "contrast": contrast,
        "noise": noise,
        "skew": abs(best),
        "ink_density": ink,
        "dark_fraction": dark,
        "aspect": image.width / max(1, image.height),
    }


def feature_vector(feats: dict[str, float]) -> list[float]:
    return [float(feats[k]) for k in FEATURES]


class DifficultyModel:
    """Gradient boosting on quality features → P(at least one required field wrong)."""

    def __init__(self) -> None:
        from sklearn.ensemble import GradientBoostingClassifier

        self.clf = GradientBoostingClassifier(
            n_estimators=120, max_depth=3, learning_rate=0.08, random_state=0
        )
        self.fitted = False

    def fit(self, x: list[list[float]], y: list[int]) -> dict[str, Any]:
        arr = np.asarray(x, dtype=np.float64)
        lab = np.asarray(y, dtype=int)
        if len(set(lab.tolist())) < 2:
            self.fitted = False
            return {"fitted": False, "reason": "single class"}
        self.clf.fit(arr, lab)
        self.fitted = True
        return {"fitted": True, "n": len(lab), "positive_rate": float(lab.mean())}

    def predict(self, feats: dict[str, float]) -> float:
        if not self.fitted:
            # heuristic before any outcomes exist: blur and noise dominate
            return float(
                min(
                    1.0, 0.15 + 0.6 * feats["noise"] * 10 + (0.25 if feats["blur"] < 0.002 else 0.0)
                )
            )
        return float(self.clf.predict_proba(np.asarray([feature_vector(feats)]))[0][1])

    def dumps(self) -> bytes:
        import joblib

        buf = io.BytesIO()
        joblib.dump({"clf": self.clf, "fitted": self.fitted}, buf)
        return buf.getvalue()

    @classmethod
    def loads(cls, data: bytes) -> DifficultyModel:
        import joblib

        obj = joblib.load(io.BytesIO(data))
        m = cls()
        m.clf = obj["clf"]
        m.fitted = bool(obj["fitted"])
        return m
