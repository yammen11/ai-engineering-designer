from datetime import datetime
from pathlib import Path
from uuid import uuid4

from aied.config import LLM_PROVIDER, OUTPUT_DIR
from aied.agents.engineering_agent import run_engineering_agent
from aied.schemas import BoxParameters, CadInstruction, RunRecord, StepMetadata
from aied.services.pdf_service import extract_pdf_text
from aied.services.cad_service import inspect_step, generate_step


def _demo_instruction() -> CadInstruction:
    return CadInstruction(
        operation="create_box",
        box=BoxParameters(
            length_mm=100.0,
            width_mm=60.0,
            height_mm=20.0,
        ),
        reason=(
            "Demo mode because no OpenAI API key is configured. "
            "A 100 x 60 x 20 mm box verifies the local end-to-end pipeline."
        ),
    )


def execute_pipeline(
    pdf_path: Path | None,
    step_path: Path | None,
    user_request: str,
) -> RunRecord:
    if not pdf_path and not step_path and not user_request.strip():
        raise ValueError(
            "Please provide at least a PDF, a STEP file, or a text request."
        )

    pdf_text = ""
    step_metadata: StepMetadata | None = None

    if pdf_path:
        pdf_text = extract_pdf_text(pdf_path)

    if step_path:
        step_metadata = inspect_step(step_path)

    step_context = (
        step_metadata.model_dump_json(indent=2)
        if step_metadata
        else "(no STEP supplied)"
    )

    llm_input = f"""
USER REQUEST:
{user_request.strip() or "(none)"}

PDF TEXT:
{pdf_text or "(no PDF supplied)"}

INPUT STEP METADATA:
{step_context}

Return one supported CAD instruction for prototype v0.1.
""".strip()

    if LLM_PROVIDER == "local":

        mode = "local"

        instruction = run_engineering_agent(llm_input)

    else:

        mode = "demo"

        instruction = _demo_instruction(user_request)

    run_id = (
        datetime.now().strftime("%Y%m%d_%H%M%S")
        + "_"
        + uuid4().hex[:8]
    )

    run_dir = OUTPUT_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    output_step = run_dir / "output.step"
    generate_step(
        instruction=instruction,
        output_path=output_step,
        input_step_path=step_path,
    )

    record = RunRecord(
        run_id=run_id,
        mode=mode,
        user_request=user_request,
        pdf_file=str(pdf_path) if pdf_path else None,
        step_file=str(step_path) if step_path else None,
        step_metadata=step_metadata,
        instruction=instruction,
        output_step=str(output_step),
    )

    (run_dir / "run.json").write_text(
        record.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return record
