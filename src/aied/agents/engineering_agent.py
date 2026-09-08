import json
import re

from openai import OpenAI

from aied.config import LLM_BASE_URL, LLM_MODEL, PROMPT_DIR
from aied.schemas import CadInstruction


def load_prompt() -> str:
    prompt_path = PROMPT_DIR / "engineering_agent.txt"
    return prompt_path.read_text(encoding="utf-8")


def get_client():
    return OpenAI(
        base_url=LLM_BASE_URL,
        api_key="local"
    )


def get_model_name():
    client = get_client()

    models = client.models.list()

    model_ids = [model.id for model in models.data]

    if not model_ids:
        raise RuntimeError(
            "Kein lokales Modell gefunden. "
            "Bitte Bionic öffnen und Local Model API starten."
        )

    if LLM_MODEL:
        return LLM_MODEL

    return model_ids[0]


def extract_json(text: str):
    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])

        raise ValueError(
            f"Das lokale LLM hat kein gültiges JSON geliefert:\n{text}"
        )


def run_engineering_agent(input_text: str):

    client = get_client()

    model_name = get_model_name()

    system_prompt = load_prompt()

    json_instruction = """
Antworte ausschließlich als gültiges JSON.

Für einen Quader:

{
  "operation": "create_box",
  "box": {
    "length_mm": 20,
    "width_mm": 40,
    "height_mm": 60
  },
  "cylinder": null,
  "sphere": null,
  "reason": "Kurze Begründung"
}

Für einen Zylinder:

{
  "operation": "create_cylinder",
  "box": null,
  "cylinder": {
    "radius_mm": 20,
    "height_mm": 100
  },
  "sphere": null,
  "reason": "Kurze Begründung"
}

Für eine Kugel:

{
  "operation": "create_sphere",
  "box": null,
  "cylinder": null,
  "sphere": {
    "radius_mm": 20
  },
  "reason": "Kurze Begründung"
}
"""

    response = client.chat.completions.create(
        model=model_name,

        messages=[
            {
                "role": "system",
                "content": system_prompt + "\n\n" + json_instruction
            },

            {
                "role": "user",
                "content": input_text
            }
        ],

        temperature=0.1
    )

    answer = response.choices[0].message.content

    data = extract_json(answer)

    instruction = CadInstruction.model_validate(data)

    return instruction