from pathlib import Path
import os

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "inputs"
OUTPUT_DIR = DATA_DIR / "outputs"
PROMPT_DIR = PROJECT_ROOT / "prompts"


INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# LLM configuration
LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "local"
).strip()

LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL",
    "http://localhost:1234/v1"
).strip()

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    ""
).strip()


CANONICAL_LENGTH_UNIT = "mm"
PDF_MAX_CHARACTERS = 40000