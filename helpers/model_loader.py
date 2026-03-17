import torch
import logging
import traceback
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor
from .config import DEVICE, MODEL_CONFIG

logger = logging.getLogger(__name__)


async def load_models(state) -> None:
    logger.info("=" * 60)
    logger.info("Starting model loading...")
    logger.info(f"Target device: {DEVICE}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU memory free: {torch.cuda.mem_get_info()[0] / 1e9:.1f} GB")
    logger.info("=" * 60)

    try:
        logger.info("[1/4] Loading IndicProcessor...")
        state.ip = IndicProcessor(inference=True)
        logger.info("✓ IndicProcessor loaded")

        for idx, (key, model_name) in enumerate(MODEL_CONFIG.items(), start=2):
            logger.info(f"[{idx}/4] Loading {key} model ({model_name})...")

            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            logger.info("  ✓ Tokenizer loaded")

            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            )
            model = model.to(DEVICE)
            model.eval()

            # Verify device placement — fail loudly if not on expected device
            actual_device = next(model.parameters()).device
            if str(actual_device) != DEVICE and not str(actual_device).startswith(DEVICE):
                raise RuntimeError(
                    f"Model {key} loaded to {actual_device}, expected {DEVICE}. "
                    f"Check GPU availability and memory."
                )
            logger.info(f"  ✓ Model on {actual_device}")

            if DEVICE == "cuda":
                used = torch.cuda.memory_allocated() / 1e9
                logger.info(f"  ✓ GPU memory allocated so far: {used:.1f} GB")

            state.models[key] = {"tokenizer": tokenizer, "model": model}

        state.models_loaded = True
        logger.info("=" * 60)
        logger.info("✓ ALL MODELS LOADED SUCCESSFULLY!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"✗ Model loading failed: {e}")
        traceback.print_exc()
        state.models_loaded = False
        raise  # Re-raise so startup failure is visible
