"""Direct Python inference with the pinned, text-only EmbeddingGemma 2 model."""

import math
import os
from pathlib import Path

MODEL_ID = "google/embeddinggemma-2"
MODEL_REVISION = "914f7f89142e33e77833254d9c9b90c3cef7303b"
PROMPT_VERSION = "embeddinggemma-2-search-v1"
MODEL_FILES = ["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja"]


class SearchError(Exception):
    """An actionable error suitable for CLI output."""


def normalize(values):
    if not isinstance(values, list) or not values:
        raise SearchError("Embedding must be a nonempty numeric array")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise SearchError("Embedding contains invalid or nonfinite values")
    norm = math.hypot(*values)
    if not math.isfinite(norm) or norm == 0:
        raise SearchError("Embedding has an invalid norm")
    return [v / norm for v in values]


def model_cache():
    return Path(os.environ.get("GEMSEARCH_MODEL_CACHE", "~/.cache/gemsearch/models")).expanduser()


def download_model():
    """Network access is confined to this explicit setup operation."""
    from huggingface_hub import snapshot_download

    try:
        return snapshot_download(
            repo_id=MODEL_ID,
            revision=MODEL_REVISION,
            cache_dir=str(model_cache()),
            allow_patterns=MODEL_FILES,
        )
    except Exception as exc:
        raise SearchError("Model download failed; check connectivity and available disk space, then retry") from exc


class PythonEmbedder:
    def __init__(self, device="auto", batch_size=4):
        self.device = device
        self.batch_size = batch_size
        self._model = None

    def identity(self):
        return {"model": MODEL_ID, "revision": MODEL_REVISION, "prompt": PROMPT_VERSION, "dimensions": 768}

    def load(self):
        if self._model is not None:
            return self._model
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
        import torch
        from huggingface_hub import snapshot_download
        from sentence_transformers import SentenceTransformer

        try:
            local = snapshot_download(
                repo_id=MODEL_ID,
                revision=MODEL_REVISION,
                cache_dir=str(model_cache()),
                local_files_only=True,
                allow_patterns=MODEL_FILES,
            )
        except OSError as exc:
            raise SearchError("Model is not cached; run gemsearch download-model once while online") from exc
        device = self.device
        if device == "auto":
            device = "mps" if torch.backends.mps.is_available() else "cpu"
        if device == "mps" and not torch.backends.mps.is_available():
            raise SearchError("MPS is unavailable; use --device cpu or a native arm64 Python on macOS")
        try:
            self._model = SentenceTransformer(
                local,
                device=device,
                local_files_only=True,
                trust_remote_code=False,
                config_kwargs={"vision_config": None, "audio_config": None},
                model_kwargs={"torch_dtype": torch.float32},
            )
        except (OSError, ValueError, RuntimeError) as exc:
            raise SearchError(
                "Cannot load EmbeddingGemma 2; reinstall locked dependencies and try --device cpu"
            ) from exc
        self.device = device
        return self._model

    def embed(self, texts):
        model = self.load()
        for text in texts:
            if len(model.tokenizer.encode(text, add_special_tokens=True)) > model.max_seq_length:
                raise SearchError("Input exceeds the model token limit; shorten the query or chunk")
        try:
            vectors = model.encode(
                texts,
                prompt="",
                batch_size=self.batch_size,
                normalize_embeddings=True,
                show_progress_bar=False,
                convert_to_numpy=True,
            ).tolist()
        except RuntimeError as exc:
            raise SearchError("Embedding inference failed; try --device cpu or --batch-size 1") from exc
        if len(vectors) != len(texts):
            raise SearchError("Model returned the wrong number of embeddings")
        vectors = [normalize(v) for v in vectors]
        if any(len(v) != 768 for v in vectors):
            raise SearchError("Model returned an unexpected embedding dimension")
        return vectors

    def documents(self, title, chunks):
        return self.embed([f"title: {title[:200]} | text: {chunk}" for chunk in chunks])

    def query(self, text):
        return self.embed([f"task: search result | query: {text}"])[0]
