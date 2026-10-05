import os
import base64
import streamlit as st

APP_NAME = "AI CNC Programming Copilot"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="⚙️",
    layout="wide"
)


def get_secret(name, default=""):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass

    return os.getenv(name, default)


def pdf_to_png(pdf_bytes):
    import fitz

    doc = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    if len(doc) == 0:
        raise ValueError("PDF contains no pages.")

    page = doc.load_page(0)

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2, 2),
        alpha=False
    )

    return pix.tobytes("png")


def analyze_drawing(
    image_bytes,
    filename,
    controller,
    machine,
    material,
    units,
    stock
):
    api_key = get_secret("GPT_API_KEY")

    base_url = get_secret("GPT_BASE_URL")

    model = get_secret(
        "GPT_MODEL",
        "gpt-120b"
    )

    if not api_key:
        raise RuntimeError(
            "GPT_API_KEY is missing. "
            "Add it in Streamlit Cloud → Settings → Secrets."
        )

    from openai import OpenAI

    client_args = {
        "api_key": api_key
    }

    if base_url:
        client_args["base_url"] = base_url

    client = OpenAI(**client_args)

    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    prompt = f"""
You are a senior CNC manufacturing engineer.

Analyze the uploaded engineering drawing conservatively.

JOB INFORMATION

Controller:
{controller}

Machine:
{machine}

Material:
{material}

Units:
{units}

Stock:
{stock}

File:
{filename}


RETURN THESE SECTIONS:

1. DRAWING INTERPRETATION

2. CONFIRMED DIMENSIONS

3. DETECTED FEATURES
- holes
- pockets
- slots
- profiles
- radii
- chamfers

4. TOLERANCES

5. SURFACE FINISH REQUIREMENTS

6. DATUM / WCS

7. RECOMMENDED MACHINING OPERATIONS

8. TOOLING REQUIREMENTS

9. MISSING OR AMBIGUOUS INFORMATION

10. SAFETY BLOCKERS

11. CONFIDENCE ASSESSMENT


STRICT SAFETY RULES:

- NEVER invent dimensions.
- NEVER invent tolerances.
- NEVER invent datum locations.
- NEVER invent material information.
- NEVER invent machine limits.
- NEVER invent tooling data.
- NEVER invent feeds or speeds.
- Clearly mark uncertain information as UNKNOWN.
- Clearly identify information requiring confirmation.
- DO NOT generate executable G-code at this stage.
- If the drawing is unclear, STOP and explain what information is required.
"""

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a safety-first CNC engineering assistant. "
                    "Accuracy is more important than completing the task. "
                    "Never guess engineering information."
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                "data:image/png;base64,"
                                + image_base64
                            )
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content


# ------------------------------------------------
# USER INTERFACE
# ------------------------------------------------

st.title("⚙️ AI CNC Programming Copilot")

st.caption(
    "Safety-first CNC drawing analysis "
    "and manufacturing planning"
)


# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------

with st.sidebar:

    st.header("Machine Setup")

    controller = st.selectbox(
        "Controller",
        [
            "Fanuc",
            "Haas",
            "Siemens",
            "Mitsubishi"
        ]
    )

    machine = st.text_input(
        "Machine",
        "3-Axis CNC Milling Machine"
    )

    material = st.text_input(
        "Material",
        "Aluminum 6061"
    )

    units = st.selectbox(
        "Units",
        [
            "mm",
            "inch"
        ]
    )

    stock = st.text_input(
        "Stock Size",
        "100 x 80 x 30 mm"
    )


# ------------------------------------------------
# SAFETY WARNING
# ------------------------------------------------

st.warning(
    """
    ⚠️ SAFETY WARNING

    This application is decision-support software.

    NEVER run AI-generated CNC code directly on a machine.

    A qualified CNC programmer/machinist must verify:

    • tooling
    • workholding
    • work offsets
    • machine limits
    • feeds and speeds
    • tool clearance
    • simulation
    • final G-code
    """
)


# ------------------------------------------------
# FILE UPLOAD
# ------------------------------------------------

uploaded = st.file_uploader(
    "Upload Engineering Drawing",
    type=[
        "png",
        "jpg",
        "jpeg",
        "pdf"
    ],
    help="Upload a clear dimensioned engineering drawing."
)


if uploaded:

    raw_file = uploaded.getvalue()

    # IMAGE
    if uploaded.type.startswith("image/"):

        preview = raw_file

    # PDF
    else:

        try:

            preview = pdf_to_png(
                raw_file
            )

        except Exception as error:

            preview = None

            st.error(
                f"PDF processing failed: {error}"
            )


    # SHOW DRAWING

    if preview:

        st.image(
            preview,
            caption=uploaded.name,
            use_container_width=True
        )


    # ANALYZE BUTTON

    if st.button(
        "🔎 Analyze Drawing",
        type="primary",
        use_container_width=True
    ):

        if preview is None:

            st.error(
                "Drawing could not be read."
            )

        else:

            with st.spinner(
                "AI is analyzing the engineering drawing..."
            ):

                try:

                    result = analyze_drawing(
                        image_bytes=preview,
                        filename=uploaded.name,
                        controller=controller,
                        machine=machine,
                        material=material,
                        units=units,
                        stock=stock
                    )

                    st.session_state[
                        "analysis_result"
                    ] = result

                except Exception as error:

                    st.error(
                        f"Analysis failed: {error}"
                    )


# ------------------------------------------------
# RESULT
# ------------------------------------------------

if "analysis_result" in st.session_state:

    st.divider()

    st.subheader(
        "📋 Engineering Analysis"
    )

    st.markdown(
        st.session_state[
            "analysis_result"
        ]
    )

    st.error(
        """
        🚫 G-CODE EXPORT BLOCKED

        This version intentionally does not generate
        executable CNC G-code.

        Before G-code generation we will add:

        • structured geometry extraction
        • manufacturing planning
        • tooling database
        • deterministic feeds & speeds calculations
        • controller-specific post processor
        • G-code validator
        • collision checking
        • simulation
        • human approval
        """
    )


# ------------------------------------------------
# FOOTER
# ------------------------------------------------

st.divider()

st.caption(
    "CNC AI Programming Copilot • "
    "Streamlit • GPT-120B-compatible API"
)
