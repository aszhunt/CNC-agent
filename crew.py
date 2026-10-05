import base64
import json

from crewai import Agent, Crew, Process, Task, LLM

from core.config import BASE_URL, MODEL_NAME, get_api_key

SYSTEM_CONTEXT = """
You are part of a safety-first CNC engineering assistant.
You must never invent dimensions, tolerances, datum, material, machine limits,
tool data, feeds/speeds or controller behavior.
If information is missing or ambiguous, explicitly mark it UNKNOWN and recommend
a clarification. Do not output executable G-code in this drawing-analysis stage.
"""

def build_llm():
    key = get_api_key()
    if not key or key == "PASTE_YOUR_API_KEY_HERE":
        raise RuntimeError(
            "API key is not configured. Put GPT_API_KEY in Streamlit Secrets "
            "or replace the local placeholder in core/config.py."
        )
    return LLM(
        model=MODEL_NAME,
        api_key=key,
        base_url=BASE_URL,
        temperature=0,
    )

def run_drawing_analysis(file_bytes, filename, controller, machine, material, units, stock):
    # This first version sends metadata plus a conservative instruction.
    # Vision/image transport differs between GPT-120B providers, so the actual
    # provider adapter should be finalized once the exact API is known.
    encoded = base64.b64encode(file_bytes).decode("utf-8")

    llm = build_llm()

    analyst = Agent(
        role="Senior CNC Drawing Analyst",
        goal="Extract only defensible engineering information from a drawing.",
        backstory=SYSTEM_CONTEXT,
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    task = Task(
        description=f"""
Analyze the uploaded engineering drawing named {filename}.

Known job context:
- Controller: {controller}
- Machine: {machine}
- Material supplied by user: {material}
- Units selected by user: {units}
- Stock supplied by user: {stock}

Return a structured engineering assessment with:
1. drawing units
2. overall dimensions
3. detected features (holes, pockets, slots, profiles, radii/chamfers)
4. dimensions and tolerances that are actually visible
5. datum/WCS information
6. material information
7. missing/ambiguous information
8. recommended manufacturing-operation sequence
9. safety blockers

Do not fabricate values.
Do not generate executable G-code.

The uploaded file is available to the application as base64 data:
{encoded[:2000]}...
""",
        expected_output="A concise engineering assessment with explicit UNKNOWN fields.",
        agent=analyst,
    )

    crew = Crew(
        agents=[analyst],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()
    return str(result)
