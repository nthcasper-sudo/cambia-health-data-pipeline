import os
from textwrap import dedent

import pandas as pd
import plotly.express as px
import snowflake.connector
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(
    page_title="Synthea Healthcare Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# -------------------------------------------------
# HTML helper
# -------------------------------------------------
def render_html(markup: str) -> None:
    """Render custom HTML without Markdown treating indented HTML as code."""
    st.markdown(dedent(markup).strip(), unsafe_allow_html=True)


# -------------------------------------------------
# Design system
# -------------------------------------------------
render_html(
    """
    <style>
        :root {
            --paper: #FAF7F0;
            --paper-2: #F4EFE5;
            --surface: #FFFDF8;
            --surface-2: #FBF5EA;
            --ink: #171411;
            --ink-soft: #2C2925;
            --muted: #706A61;
            --muted-2: #9A9287;
            --line: #DED4C5;
            --line-strong: #C9BDAA;
            --accent: #E95A2A;
            --accent-soft: #FFE2D6;
            --green: #1E6F5C;
            --warning-bg: #FFF3C7;
            --warning-text: #6D4C00;
            --radius-lg: 24px;
            --radius-md: 16px;
            --radius-sm: 12px;
            --shadow: 0 18px 50px rgba(32, 24, 16, 0.08);
            --shadow-soft: 0 10px 30px rgba(32, 24, 16, 0.055);
            --ease: cubic-bezier(.2, .8, .2, 1);
        }

        html {
            scroll-behavior: smooth;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 0%, rgba(233, 90, 42, 0.10), transparent 28rem),
                radial-gradient(circle at 94% 8%, rgba(30, 111, 92, 0.08), transparent 24rem),
                var(--paper);
            color: var(--ink);
        }

        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        #MainMenu,
        footer {
            display: none !important;
        }

        div[data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 8% 0%, rgba(233, 90, 42, 0.10), transparent 28rem),
                radial-gradient(circle at 94% 8%, rgba(30, 111, 92, 0.08), transparent 24rem),
                var(--paper) !important;
        }

        .block-container {
            width: min(1280px, calc(100vw - 3.5rem));
            max-width: none;
            padding-top: 1.35rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3, h4, p, li, label, span, div {
            font-family: ui-sans-serif, Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        h1, h2, h3 {
            color: var(--ink) !important;
            letter-spacing: -0.04em;
        }

        h1 {
            font-size: clamp(2.1rem, 4.5vw, 4.2rem) !important;
            line-height: 0.99 !important;
            font-weight: 780 !important;
            margin-bottom: 0.65rem !important;
        }

        h2 {
            font-size: 1.35rem !important;
            font-weight: 760 !important;
        }

        h3 {
            font-size: 1.05rem !important;
            font-weight: 720 !important;
        }

        section[data-testid="stSidebar"] {
            background: rgba(255, 253, 248, 0.84);
            backdrop-filter: blur(18px);
            border-right: 1px solid var(--line);
        }

        section[data-testid="stSidebar"] hr {
            border-color: var(--line);
            opacity: 1;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {
            color: var(--ink) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: var(--muted) !important;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .wordmark {
            color: var(--ink);
            font-size: 0.76rem;
            font-weight: 780;
            letter-spacing: 0.32em;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .status-text {
            color: var(--muted);
            font-size: 0.86rem;
            font-weight: 620;
            text-align: right;
        }

        .hero-card,
        .section-card,
        .metric-card,
        .control-card,
        .model-card,
        .note-card {
            background: rgba(255, 253, 248, 0.84);
            border: 1px solid var(--line);
            box-shadow: var(--shadow-soft);
            transition:
                transform 190ms var(--ease),
                border-color 190ms var(--ease),
                background 190ms var(--ease),
                box-shadow 190ms var(--ease);
        }

        .hero-card:hover,
        .section-card:hover,
        .metric-card:hover,
        .control-card:hover,
        .model-card:hover,
        .note-card:hover {
            transform: translateY(-2px);
            border-color: var(--line-strong);
            background: var(--surface);
            box-shadow: var(--shadow);
        }

        .hero-card {
            position: relative;
            overflow: hidden;
            border-radius: 30px;
            padding: clamp(1.2rem, 2.2vw, 1.8rem);
            margin-bottom: 0.9rem;
        }

        .hero-card::after {
            content: "";
            position: absolute;
            width: 15rem;
            height: 15rem;
            right: -7rem;
            top: -8rem;
            background: radial-gradient(circle, rgba(233, 90, 42, 0.15), transparent 68%);
            pointer-events: none;
        }

        .hero-eyebrow {
            color: var(--muted);
            font-size: 0.74rem;
            font-weight: 780;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
        }

        .hero-title {
            position: relative;
            color: var(--ink);
            font-size: clamp(2.15rem, 4.6vw, 4.2rem);
            font-weight: 780;
            line-height: 0.99;
            letter-spacing: -0.06em;
            max-width: 980px;
            margin-bottom: 0.85rem;
            z-index: 1;
        }

        .hero-subtitle {
            position: relative;
            color: var(--ink-soft);
            font-size: clamp(0.98rem, 1.35vw, 1.1rem);
            line-height: 1.55;
            max-width: 820px;
            z-index: 1;
        }

        .data-note {
            background: var(--warning-bg);
            border: 1px solid rgba(176, 124, 0, 0.24);
            color: var(--warning-text);
            border-radius: var(--radius-md);
            padding: 0.78rem 0.95rem;
            font-size: 0.9rem;
            line-height: 1.48;
            margin-bottom: 0.95rem;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 0.8rem;
            margin-bottom: 1rem;
        }

        .metric-card {
            border-radius: var(--radius-lg);
            padding: 0.95rem;
            min-height: 116px;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.72rem;
            font-weight: 780;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 0.58rem;
        }

        .metric-value {
            color: var(--ink);
            font-size: clamp(1.55rem, 2.5vw, 2.05rem);
            font-weight: 780;
            letter-spacing: -0.055em;
            line-height: 1;
            margin-bottom: 0.6rem;
            overflow-wrap: anywhere;
        }

        .metric-copy {
            color: var(--muted);
            font-size: 0.82rem;
            line-height: 1.35;
        }

        .section-card {
            border-radius: var(--radius-lg);
            padding: 0.95rem 1.05rem;
            margin-bottom: 0.75rem;
        }

        .section-label {
            color: var(--muted);
            font-size: 0.72rem;
            font-weight: 780;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            margin-bottom: 0.3rem;
        }

        .section-title {
            color: var(--ink);
            font-size: 1.12rem;
            font-weight: 760;
            letter-spacing: -0.035em;
            margin-bottom: 0.22rem;
        }

        .section-copy {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .control-card {
            border-radius: var(--radius-md);
            padding: 0.82rem 0.95rem;
            margin-bottom: 0.75rem;
        }

        .control-title {
            color: var(--ink);
            font-size: 0.95rem;
            font-weight: 740;
            margin-bottom: 0.2rem;
        }

        .control-copy {
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.42;
        }

        .small-muted {
            color: var(--muted);
            font-size: 0.85rem;
            line-height: 1.45;
        }

        .model-card {
            border-radius: var(--radius-lg);
            padding: 1rem 1.1rem;
            min-height: 180px;
            margin-bottom: 0.75rem;
        }

        .model-card h4 {
            color: var(--ink);
            letter-spacing: -0.025em;
            margin: 0 0 0.65rem 0;
        }

        .model-card code {
            color: var(--ink);
            background: var(--surface-2);
            border: 1px solid var(--line);
            border-radius: 999px;
            padding: 0.15rem 0.45rem;
        }

        div[data-testid="stTabs"] [role="tablist"] {
            gap: 0.35rem;
            border-bottom: 1px solid var(--line);
            padding-bottom: 0.35rem;
            margin-bottom: 0.95rem;
        }

        div[data-testid="stTabs"] button[role="tab"] {
            border-radius: 999px;
            padding: 0.45rem 0.95rem;
            color: var(--muted) !important;
            transition: background 180ms var(--ease), color 180ms var(--ease), transform 180ms var(--ease);
        }

        div[data-testid="stTabs"] button[role="tab"]:hover {
            background: var(--surface-2);
            color: var(--ink) !important;
            transform: translateY(-1px);
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: var(--ink) !important;
            color: var(--surface) !important;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] p {
            color: var(--surface) !important;
        }

        div[data-testid="stExpander"] {
            background: rgba(255, 253, 248, 0.78);
            border: 1px solid var(--line);
            border-radius: var(--radius-md);
            box-shadow: none;
            overflow: hidden;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: var(--radius-md);
            overflow: hidden;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background: var(--surface) !important;
            border-color: var(--line) !important;
            border-radius: 999px !important;
            color: var(--ink) !important;
            transition: border-color 180ms var(--ease), box-shadow 180ms var(--ease);
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div:focus-within,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 4px rgba(233, 90, 42, 0.12) !important;
        }

        div[role="radiogroup"] label {
            color: var(--ink-soft) !important;
        }

        .stPlotlyChart {
            background: rgba(255, 253, 248, 0.72);
            border: 1px solid var(--line);
            border-radius: var(--radius-lg);
            padding: 0.35rem;
            box-shadow: var(--shadow-soft);
        }

        @media (max-width: 900px) {
            .topbar {
                align-items: flex-start;
                flex-direction: column;
            }

            .status-text {
                text-align: left;
            }
        }

        @media (max-width: 640px) {
            .block-container {
                width: min(100%, calc(100vw - 1.2rem));
                padding-left: 0.6rem;
                padding-right: 0.6rem;
            }

            .hero-title {
                letter-spacing: -0.052em;
            }

            .wordmark {
                letter-spacing: 0.22em;
                white-space: normal;
            }
        }
    </style>
    """
)


# -------------------------------------------------
# Chart theme
# -------------------------------------------------
CHART_COLORS = {
    "ink": "#171411",
    "muted": "#706A61",
    "accent": "#E95A2A",
    "green": "#1E6F5C",
    "ochre": "#B88219",
    "clay": "#B85C38",
    "blue": "#2F5D8C",
    "plum": "#6A4C7C",
}

COLOR_SEQUENCE = [
    CHART_COLORS["ink"],
    CHART_COLORS["accent"],
    CHART_COLORS["green"],
    CHART_COLORS["ochre"],
    CHART_COLORS["blue"],
    CHART_COLORS["plum"],
    CHART_COLORS["clay"],
]


def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, Segoe UI, Arial, sans-serif",
            color="#171411",
        ),
        title=dict(
            font=dict(size=17, color="#171411"),
            x=0,
            xanchor="left",
        ),
        margin=dict(l=10, r=10, t=54, b=24),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#706A61"),
        ),
        hoverlabel=dict(
            bgcolor="#171411",
            bordercolor="#171411",
            font=dict(color="#FFFDF8", family="Inter, Segoe UI, Arial, sans-serif"),
        ),
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E8DFD1",
        zeroline=False,
        linecolor="#DED4C5",
        tickfont=dict(color="#706A61"),
        title_font=dict(color="#706A61"),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E8DFD1",
        zeroline=False,
        linecolor="#DED4C5",
        tickfont=dict(color="#706A61"),
        title_font=dict(color="#706A61"),
    )

    return fig


def section_intro(label: str, title: str, copy: str) -> None:
    render_html(
        f"""
        <div class="section-card">
            <div class="section-label">{label}</div>
            <div class="section-title">{title}</div>
            <div class="section-copy">{copy}</div>
        </div>
        """
    )


def control_intro(title: str, copy: str) -> None:
    render_html(
        f"""
        <div class="control-card">
            <div class="control-title">{title}</div>
            <div class="control-copy">{copy}</div>
        </div>
        """
    )


def kpi_grid(cards: list[dict[str, str]]) -> None:
    card_html = ""

    for card in cards:
        card_html += dedent(
            f"""
            <div class="metric-card">
                <div class="metric-label">{card["label"]}</div>
                <div class="metric-value">{card["value"]}</div>
                <div class="metric-copy">{card["copy"]}</div>
            </div>
            """
        ).strip()

    render_html(
        f"""
        <div class="kpi-grid">
            {card_html}
        </div>
        """
    )



def clear_mfa_state() -> None:
    """Clear the saved MFA code and all code input boxes."""
    st.session_state.pop("mfa_passcode", None)
    for index in range(6):
        st.session_state.pop(f"mfa_digit_{index}", None)


def render_mfa_autofocus_script() -> None:
    """Client-side behavior for the six MFA inputs."""
    components.html(
        r"""
        <script>
            const parentDoc = window.parent.document;
            let autoSubmitLock = false;

            function getMfaInputs() {
                const labelledInputs = Array.from(
                    parentDoc.querySelectorAll('input[aria-label^="Digit "]')
                );

                if (labelledInputs.length === 6) {
                    return labelledInputs;
                }

                const forms = Array.from(parentDoc.querySelectorAll('div[data-testid="stForm"]'));
                const visibleForm = forms.find((form) => form.offsetParent !== null) || forms[0];

                if (!visibleForm) {
                    return [];
                }

                return Array.from(visibleForm.querySelectorAll('input[type="text"]')).slice(0, 6);
            }

            function getSubmitButton() {
                const forms = Array.from(parentDoc.querySelectorAll('div[data-testid="stForm"]'));
                const visibleForm = forms.find((form) => form.offsetParent !== null) || forms[0];

                if (!visibleForm) {
                    return null;
                }

                const buttons = Array.from(visibleForm.querySelectorAll('button'));
                return buttons.find((button) => button.innerText.trim().toLowerCase() === 'continue') || buttons[buttons.length - 1];
            }

            function emitInput(input) {
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }

            function focusInput(inputs, index) {
                const target = inputs[index];
                if (!target) {
                    return;
                }

                window.setTimeout(() => {
                    target.focus();
                    target.select();
                }, 0);
            }

            function codeIsComplete(inputs) {
                return inputs.length === 6 && inputs.every((input) => /^\d$/.test(input.value));
            }

            function submitCode(inputs, delay = 0) {
                if (!codeIsComplete(inputs) || autoSubmitLock) {
                    return;
                }

                const submitButton = getSubmitButton();
                if (!submitButton) {
                    return;
                }

                autoSubmitLock = true;
                window.setTimeout(() => {
                    submitButton.click();
                }, delay);
            }

            function attachMfaBehavior() {
                const inputs = getMfaInputs();

                if (inputs.length !== 6) {
                    return;
                }

                inputs.forEach((input, index) => {
                    input.setAttribute('inputmode', 'numeric');
                    input.setAttribute('pattern', '[0-9]*');
                    input.setAttribute('autocomplete', index === 0 ? 'one-time-code' : 'off');
                    input.setAttribute('maxlength', '1');
                    input.setAttribute('placeholder', '');

                    if (input.dataset.mfaAutoAdvance === 'true') {
                        return;
                    }

                    input.dataset.mfaAutoAdvance = 'true';

                    input.addEventListener('focus', () => {
                        input.select();
                    });

                    input.addEventListener('beforeinput', (event) => {
                        if (event.inputType === 'insertText' && event.data && !/^\d$/.test(event.data)) {
                            event.preventDefault();
                        }
                    });

                    input.addEventListener('input', () => {
                        const cleanValue = input.value.replace(/\D/g, '').slice(-1);

                        if (input.value !== cleanValue) {
                            input.value = cleanValue;
                            emitInput(input);
                        }

                        if (cleanValue && index < inputs.length - 1) {
                            focusInput(inputs, index + 1);
                        }

                        submitCode(inputs, 180);
                    });

                    input.addEventListener('keydown', (event) => {
                        if (event.key === 'Enter') {
                            event.preventDefault();

                            if (codeIsComplete(inputs)) {
                                submitCode(inputs, 0);
                                return;
                            }

                            const firstEmptyIndex = inputs.findIndex((field) => field.value === '');
                            if (firstEmptyIndex >= 0) {
                                focusInput(inputs, firstEmptyIndex);
                            }
                        }

                        if (event.key === 'Backspace' && input.value === '' && index > 0) {
                            event.preventDefault();
                            const previous = inputs[index - 1];
                            previous.value = '';
                            emitInput(previous);
                            focusInput(inputs, index - 1);
                        }

                        if (event.key === 'ArrowLeft' && index > 0) {
                            event.preventDefault();
                            focusInput(inputs, index - 1);
                        }

                        if (event.key === 'ArrowRight' && index < inputs.length - 1) {
                            event.preventDefault();
                            focusInput(inputs, index + 1);
                        }
                    });

                    input.addEventListener('paste', (event) => {
                        event.preventDefault();
                        const pastedDigits = (event.clipboardData || window.clipboardData)
                            .getData('text')
                            .replace(/\D/g, '')
                            .slice(0, 6);

                        if (!pastedDigits) {
                            return;
                        }

                        pastedDigits.split('').forEach((digit, digitOffset) => {
                            const target = inputs[index + digitOffset];
                            if (!target) {
                                return;
                            }
                            target.value = digit;
                            emitInput(target);
                        });

                        focusInput(inputs, Math.min(index + pastedDigits.length, inputs.length - 1));
                        submitCode(inputs, 180);
                    });
                });

                const firstEmptyInput = inputs.find((input) => input.value === '');
                if (firstEmptyInput && parentDoc.activeElement === parentDoc.body) {
                    window.setTimeout(() => firstEmptyInput.focus(), 50);
                }
            }

            attachMfaBehavior();

            const observer = new MutationObserver(() => attachMfaBehavior());
            observer.observe(parentDoc.body, { childList: true, subtree: true });
        </script>
        """,
        height=0,
        width=0,
    )


def render_login_page() -> None:
    """Render a full-page MFA entry screen before loading Snowflake data."""
    render_html(
        """
        <style>
            section[data-testid="stSidebar"],
            div[data-testid="collapsedControl"] {
                display: none !important;
            }

            html,
            body,
            .stApp,
            div[data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at 8% 0%, rgba(233, 90, 42, 0.10), transparent 28rem),
                    radial-gradient(circle at 94% 8%, rgba(30, 111, 92, 0.08), transparent 24rem),
                    var(--paper) !important;
            }

            .block-container {
                width: min(760px, calc(100vw - 2rem)) !important;
                max-width: 760px !important;
                padding-top: clamp(1.25rem, 5vh, 3.25rem) !important;
                padding-bottom: 2rem !important;
            }

            div[data-testid="stForm"] {
                background:
                    radial-gradient(circle at top right, rgba(233, 90, 42, 0.12), transparent 17rem),
                    rgba(255, 253, 248, 0.92);
                border: 1px solid var(--line);
                border-radius: 34px;
                box-shadow: var(--shadow);
                padding: clamp(1.35rem, 4vw, 2.4rem);
                overflow: visible !important;
            }

            .login-wordmark {
                color: var(--ink);
                font-size: 0.76rem;
                font-weight: 780;
                letter-spacing: 0.32em;
                text-transform: uppercase;
                margin-bottom: clamp(1.5rem, 5vw, 3rem);
            }

            .login-eyebrow {
                color: var(--muted);
                font-size: 0.76rem;
                font-weight: 780;
                letter-spacing: 0.18em;
                text-transform: uppercase;
                margin-bottom: 0.65rem;
            }

            .login-title {
                color: var(--ink);
                font-size: clamp(2.4rem, 7vw, 4.6rem);
                font-weight: 780;
                letter-spacing: -0.065em;
                line-height: 0.98;
                margin-bottom: 0.9rem;
            }

            .login-copy {
                color: var(--ink-soft);
                font-size: clamp(1rem, 2vw, 1.15rem);
                line-height: 1.5;
                max-width: 600px;
                margin-bottom: 1.35rem;
            }

            .login-helper-row {
                display: none !important;
            }

            div[data-testid="stForm"] div[data-testid="stTextInput"] {
                min-width: 0 !important;
                height: clamp(3.75rem, 9vw, 4.75rem) !important;
                margin-bottom: 0 !important;
                overflow: visible !important;
            }

            div[data-testid="stForm"] div[data-testid="stTextInput"] > div,
            div[data-testid="stForm"] div[data-testid="stTextInput"] div[data-baseweb="input"] {
                height: 100% !important;
                min-height: 100% !important;
                border-radius: 20px !important;
                border: 1px solid var(--line-strong) !important;
                background: rgba(255, 255, 255, 0.58) !important;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7) !important;
                overflow: visible !important;
            }

            div[data-testid="stForm"] div[data-testid="stTextInput"] input {
                height: 100% !important;
                min-height: 100% !important;
                border: 0 !important;
                background: transparent !important;
                color: var(--ink) !important;
                text-align: center !important;
                font-size: clamp(1.55rem, 5vw, 2.15rem) !important;
                font-weight: 760 !important;
                line-height: 1 !important;
                padding: 0 !important;
            }

            div[data-testid="stForm"] div[data-testid="stTextInput"]:focus-within > div,
            div[data-testid="stForm"] div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
                border-color: var(--accent) !important;
                box-shadow: 0 0 0 4px rgba(233, 90, 42, 0.13) !important;
            }

            div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] {
                gap: clamp(0.35rem, 1.4vw, 0.75rem);
            }

            div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] {
                position: absolute !important;
                width: 1px !important;
                height: 1px !important;
                overflow: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }

            div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button {
                width: 1px !important;
                height: 1px !important;
                min-height: 1px !important;
                padding: 0 !important;
                border: 0 !important;
            }

            @media (max-width: 520px) {
                .login-title {
                    font-size: clamp(2.25rem, 12vw, 3.6rem);
                }
            }
        </style>
        """
    )

    render_html('<div class="login-wordmark">A N T H O N Y  C A S P E R</div>')

    with st.form("mfa_code_form", clear_on_submit=False):
        render_html(
            """
            <div class="login-eyebrow">Snowflake Login</div>
            <div class="login-title">Enter the code</div>
            <div class="login-copy">
                Use the 6-digit MFA code from your Snowflake sign-in prompt to load the dashboard.
            </div>
            """
        )

        digit_columns = st.columns(6)
        digits = []

        for index, column in enumerate(digit_columns):
            with column:
                digit = st.text_input(
                    f"Digit {index + 1}",
                    key=f"mfa_digit_{index}",
                    max_chars=1,
                    label_visibility="collapsed",
                )
                digits.append(digit.strip())

        submit_clicked = st.form_submit_button("Continue", type="primary")

    render_mfa_autofocus_script()

    if submit_clicked:
        mfa_code = "".join(digits)

        if len(mfa_code) != 6 or not mfa_code.isdigit():
            st.error("Enter all 6 digits before submitting.")
        else:
            st.session_state["mfa_passcode"] = mfa_code
            st.rerun()


def render_loading_page() -> None:
    """Render a clean loading page while Snowflake validates MFA and returns data."""
    render_html(
        """
        <style>
            section[data-testid="stSidebar"],
            div[data-testid="collapsedControl"] {
                display: none !important;
            }

            .block-container {
                width: min(760px, calc(100vw - 2rem)) !important;
                max-width: 760px !important;
                padding-top: clamp(1.25rem, 8vh, 4rem) !important;
            }

            .stApp,
            div[data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at 8% 0%, rgba(233, 90, 42, 0.10), transparent 28rem),
                    radial-gradient(circle at 94% 8%, rgba(30, 111, 92, 0.08), transparent 24rem),
                    var(--paper) !important;
            }

            iframe[title="streamlit.components.v1.html"] {
                border: 0 !important;
                background: transparent !important;
            }
        </style>
        """
    )

    components.html(
        """
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style>
                :root {
                    --paper: #FAF7F0;
                    --surface: #FFFDF8;
                    --ink: #171411;
                    --ink-soft: #2C2925;
                    --muted: #706A61;
                    --line: #DED4C5;
                    --accent: #E95A2A;
                }

                * {
                    box-sizing: border-box;
                }

                html,
                body {
                    width: 100%;
                    min-height: 100%;
                    margin: 0;
                    overflow: hidden;
                    background: transparent;
                    font-family: ui-sans-serif, Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    color: var(--ink);
                }

                .loading-wrap {
                    width: min(640px, 100%);
                    margin: 0 auto;
                    padding: 0.2rem 0 1rem;
                }

                .wordmark {
                    color: var(--ink);
                    font-size: 0.76rem;
                    font-weight: 780;
                    letter-spacing: 0.32em;
                    text-transform: uppercase;
                    margin-bottom: clamp(1.25rem, 5vw, 2.5rem);
                }

                .card {
                    position: relative;
                    overflow: hidden;
                    background:
                        radial-gradient(circle at top right, rgba(233, 90, 42, 0.12), transparent 17rem),
                        rgba(255, 253, 248, 0.94);
                    border: 1px solid var(--line);
                    border-radius: 34px;
                    box-shadow: 0 28px 80px rgba(32, 24, 16, 0.12);
                    padding: clamp(1.5rem, 5vw, 2.6rem);
                }

                .topline {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    margin-bottom: 1.1rem;
                }

                .orb {
                    width: 2.15rem;
                    height: 2.15rem;
                    border-radius: 999px;
                    border: 2px solid rgba(233, 90, 42, 0.18);
                    border-top-color: var(--accent);
                    animation: spin 900ms linear infinite;
                    flex: 0 0 auto;
                }

                .eyebrow {
                    color: var(--muted);
                    font-size: 0.76rem;
                    font-weight: 780;
                    letter-spacing: 0.18em;
                    text-transform: uppercase;
                }

                .title {
                    color: var(--ink);
                    font-size: clamp(2.35rem, 8vw, 4.4rem);
                    font-weight: 780;
                    letter-spacing: -0.065em;
                    line-height: 0.98;
                    margin-bottom: 0.85rem;
                }

                .copy {
                    color: var(--ink-soft);
                    font-size: clamp(1rem, 2vw, 1.15rem);
                    line-height: 1.5;
                    max-width: 560px;
                    margin-bottom: 1.35rem;
                }

                .bar {
                    width: 100%;
                    height: 0.5rem;
                    overflow: hidden;
                    border-radius: 999px;
                    background: rgba(201, 189, 170, 0.45);
                }

                .bar::before {
                    content: "";
                    display: block;
                    width: 42%;
                    height: 100%;
                    border-radius: inherit;
                    background: var(--accent);
                    animation: loadbar 1.4s ease-in-out infinite;
                }

                @keyframes spin {
                    to { transform: rotate(360deg); }
                }

                @keyframes loadbar {
                    0% { transform: translateX(-110%); }
                    50% { transform: translateX(95%); }
                    100% { transform: translateX(245%); }
                }

                @media (max-width: 520px) {
                    .wordmark {
                        letter-spacing: 0.22em;
                        white-space: normal;
                    }
                }
            </style>
        </head>
        <body>
            <main class="loading-wrap" role="status" aria-live="polite">
                <div class="wordmark">A N T H O N Y  C A S P E R</div>
                <section class="card">
                    <div class="topline">
                        <div class="orb" aria-hidden="true"></div>
                        <div class="eyebrow">Connecting to Snowflake</div>
                    </div>
                    <div class="title">Checking your code.</div>
                    <div class="copy">Loading the dashboard views. This usually takes a few seconds.</div>
                    <div class="bar" aria-hidden="true"></div>
                </section>
            </main>
        </body>
        </html>
        """,
        height=620,
        scrolling=False,
    )


# -------------------------------------------------
# Snowflake connection
# -------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_connection(mfa_passcode: str):
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        authenticator="username_password_mfa",
        passcode=mfa_passcode,
        role=os.environ.get("SNOWFLAKE_ROLE"),
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema="MART",
    )


@st.cache_data(ttl=600, show_spinner=False)
def run_query(query: str, mfa_passcode: str) -> pd.DataFrame:
    conn = get_connection(mfa_passcode)
    return pd.read_sql(query, conn)


# -------------------------------------------------
# Authentication gate
# -------------------------------------------------
if "mfa_passcode" not in st.session_state:
    render_login_page()
    st.stop()

mfa_passcode = st.session_state["mfa_passcode"]


# -------------------------------------------------
# Load data
# -------------------------------------------------
loading_area = st.empty()
with loading_area.container():
    render_loading_page()

try:
    kpi_df = run_query(
        """
        SELECT *
        FROM MART.VW_KPI_OVERVIEW
        """,
        mfa_passcode,
    )

    age_gender_df = run_query(
        """
        SELECT *
        FROM MART.VW_ENCOUNTERS_BY_AGE_GENDER
        ORDER BY AGE_GROUP, GENDER
        """,
        mfa_passcode,
    )

    top_conditions_df = run_query(
        """
        SELECT *
        FROM MART.VW_TOP_CONDITIONS
        ORDER BY CONDITION_COUNT DESC
        LIMIT 25
        """,
        mfa_passcode,
    )

    top_medications_df = run_query(
        """
        SELECT *
        FROM MART.VW_TOP_MEDICATIONS
        ORDER BY MEDICATION_COUNT DESC
        LIMIT 25
        """,
        mfa_passcode,
    )

    trend_df = run_query(
        """
        SELECT
            YEAR,
            MONTH,
            MONTH_NAME,
            ENCOUNTER_COUNT,
            TOTAL_CLAIM_COST,
            AVG_CLAIM_COST
        FROM MART.VW_ENCOUNTER_TRENDS
        ORDER BY YEAR, MONTH
        """,
        mfa_passcode,
    )

    cost_age_df = run_query(
        """
        SELECT *
        FROM MART.VW_COST_BY_AGE_GROUP
        ORDER BY AGE_GROUP
        """,
        mfa_passcode,
    )

except Exception as exc:
    loading_area.empty()
    st.error("Could not load data from Snowflake. Check your MFA code and connection settings.")

    if st.button("Enter a different MFA code"):
        clear_mfa_state()
        st.rerun()

    st.exception(exc)
    st.stop()


loading_area.empty()


# -------------------------------------------------
# Sidebar after data loads
# -------------------------------------------------
st.sidebar.markdown("## Synthea Analytics")
st.sidebar.caption("Snowflake MART dashboard")

st.sidebar.markdown("---")
st.sidebar.markdown("### Connection")
st.sidebar.success("Connected")
st.sidebar.button("Enter a new code", on_click=clear_mfa_state)

st.sidebar.markdown("---")
st.sidebar.markdown("### Source")
render_html(
    """
    <div class="small-muted">
        Reads from curated Snowflake MART views. Chart controls are placed where they affect the data.
    </div>
    """
)


# -------------------------------------------------
# Header
# -------------------------------------------------
render_html(
    """
    <div class="topbar">
        <div class="wordmark">A N T H O N Y  C A S P E R</div>
        <div class="status-text">Connected to Snowflake MART</div>
    </div>

    <div class="hero-card">
        <div class="hero-eyebrow">Healthcare Data Pipeline</div>
        <div class="hero-title">Healthcare analytics from warehouse to insight.</div>
        <div class="hero-subtitle">
            A Streamlit dashboard for checking utilization, clinical patterns, medication usage,
            and cost signals from curated Synthea MART views.
        </div>
    </div>
    """
)

render_html(
    """
    <div class="data-note">
        <strong>Data scope:</strong> The pipeline currently ingests patients, encounters, conditions, medications, procedures, and observations. 
        The current MART dashboard focuses on patients, encounters, conditions, medications, procedures, 
        and cost/utilization. Observation-specific analytics are a future modeling candidate.
    </div>
    """
)


# -------------------------------------------------
# KPI cards
# -------------------------------------------------
total_patients = int(kpi_df.loc[0, "TOTAL_PATIENTS"])
total_encounters = int(kpi_df.loc[0, "TOTAL_ENCOUNTERS"])
total_conditions = int(kpi_df.loc[0, "TOTAL_CONDITIONS"])
total_medications = int(kpi_df.loc[0, "TOTAL_MEDICATIONS"])
avg_claim_cost = float(kpi_df.loc[0, "AVG_CLAIM_COST"])
total_claim_cost = float(kpi_df.loc[0, "TOTAL_CLAIM_COST"])

kpi_grid(
    [
        {
            "label": "Patients",
            "value": f"{total_patients:,}",
            "copy": "Unique patients in the modeled population.",
        },
        {
            "label": "Encounters",
            "value": f"{total_encounters:,}",
            "copy": "Visit and care events in the encounter fact.",
        },
        {
            "label": "Conditions",
            "value": f"{total_conditions:,}",
            "copy": "Diagnosis records linked to patients.",
        },
        {
            "label": "Medications",
            "value": f"{total_medications:,}",
            "copy": "Medication records for treatment analysis.",
        },
        {
            "label": "Avg Claim Cost",
            "value": f"${avg_claim_cost:,.2f}",
            "copy": "Average cost across modeled encounters.",
        },
        {
            "label": "Total Claim Cost",
            "value": f"${total_claim_cost:,.2f}",
            "copy": "Total modeled claim cost across encounters.",
        },
    ]
)


# -------------------------------------------------
# Tabs
# -------------------------------------------------
overview_tab, clinical_tab, cost_tab, data_tab = st.tabs(
    ["Overview", "Clinical Patterns", "Cost & Utilization", "Data Model"]
)


# -------------------------------------------------
# Overview tab
# -------------------------------------------------
with overview_tab:
    control_intro(
        "Choose the utilization view",
        "This control only changes the utilization chart below. The cost chart stays separate so both charts remain readable.",
    )

    view_mode = st.radio(
        "Utilization view",
        ["Age and gender", "Age totals", "Gender totals"],
        horizontal=True,
        label_visibility="collapsed",
    )

    section_intro(
        "Utilization",
        "Encounter distribution",
        "Shows how encounters are distributed across demographic groups.",
    )

    if view_mode == "Age and gender":
        fig_age_gender = px.bar(
            age_gender_df,
            x="AGE_GROUP",
            y="ENCOUNTER_COUNT",
            color="GENDER",
            barmode="group",
            color_discrete_sequence=COLOR_SEQUENCE,
            title="Encounters by Age Group and Gender",
            labels={
                "AGE_GROUP": "Age Group",
                "ENCOUNTER_COUNT": "Encounter Count",
                "GENDER": "Gender",
            },
        )

    elif view_mode == "Age totals":
        age_total_df = (
            age_gender_df.groupby("AGE_GROUP", as_index=False)["ENCOUNTER_COUNT"]
            .sum()
        )

        fig_age_gender = px.bar(
            age_total_df,
            x="AGE_GROUP",
            y="ENCOUNTER_COUNT",
            color_discrete_sequence=[CHART_COLORS["accent"]],
            title="Encounters by Age Group",
            labels={
                "AGE_GROUP": "Age Group",
                "ENCOUNTER_COUNT": "Encounter Count",
            },
        )

    else:
        gender_total_df = (
            age_gender_df.groupby("GENDER", as_index=False)["ENCOUNTER_COUNT"]
            .sum()
        )

        fig_age_gender = px.bar(
            gender_total_df,
            x="GENDER",
            y="ENCOUNTER_COUNT",
            color="GENDER",
            color_discrete_sequence=COLOR_SEQUENCE,
            title="Encounters by Gender",
            labels={
                "GENDER": "Gender",
                "ENCOUNTER_COUNT": "Encounter Count",
            },
        )

        fig_age_gender.update_layout(showlegend=False)

    fig_age_gender = style_chart(fig_age_gender)
    fig_age_gender.update_layout(height=520)

    st.plotly_chart(
        fig_age_gender,
        use_container_width=True,
        config={"displayModeBar": False},
    )

    section_intro(
        "Cost",
        "Average claim cost by age group",
        "Shows cost by age group as its own full-width chart instead of squeezing it into a side rail.",
    )

    fig_cost_age = px.bar(
        cost_age_df,
        x="AGE_GROUP",
        y="AVG_CLAIM_COST",
        color="AGE_GROUP",
        color_discrete_sequence=COLOR_SEQUENCE,
        title="Average Claim Cost by Age Group",
        labels={
            "AGE_GROUP": "Age Group",
            "AVG_CLAIM_COST": "Average Claim Cost",
        },
    )

    fig_cost_age.update_layout(showlegend=False)
    fig_cost_age.update_yaxes(tickprefix="$", separatethousands=True)
    fig_cost_age = style_chart(fig_cost_age)
    fig_cost_age.update_layout(height=480)

    st.plotly_chart(
        fig_cost_age,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# -------------------------------------------------
# Clinical tab
# -------------------------------------------------
with clinical_tab:
    control_intro(
        "Set the clinical ranking depth",
        "This slider controls how many conditions and medications appear. Smaller values are better for quick review.",
    )

    top_n = st.slider(
        "Number of records to show",
        min_value=5,
        max_value=20,
        value=10,
        step=1,
    )

    visible_conditions_df = top_conditions_df.head(top_n)
    visible_medications_df = top_medications_df.head(top_n)

    left, right = st.columns(2)

    with left:
        section_intro(
            "Conditions",
            f"Top {top_n} conditions",
            "Ranks the most common conditions in the synthetic population.",
        )

        fig_conditions = px.bar(
            visible_conditions_df,
            x="CONDITION_COUNT",
            y="CONDITION_DESCRIPTION",
            orientation="h",
            color="CONDITION_COUNT",
            color_continuous_scale=[[0, "#F6D8CA"], [0.55, "#E95A2A"], [1, "#171411"]],
            title=f"Top {top_n} Conditions",
            labels={
                "CONDITION_COUNT": "Condition Count",
                "CONDITION_DESCRIPTION": "Condition",
            },
        )

        fig_conditions.update_layout(coloraxis_showscale=False)
        fig_conditions.update_layout(yaxis={"categoryorder": "total ascending"})

        st.plotly_chart(
            style_chart(fig_conditions),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with right:
        section_intro(
            "Medications",
            f"Top {top_n} medications",
            "Ranks medication usage so treatment patterns can be compared with condition patterns.",
        )

        fig_medications = px.bar(
            visible_medications_df,
            x="MEDICATION_COUNT",
            y="MEDICATION_DESCRIPTION",
            orientation="h",
            color="MEDICATION_COUNT",
            color_continuous_scale=[[0, "#DDEAE5"], [0.55, "#1E6F5C"], [1, "#171411"]],
            title=f"Top {top_n} Medications",
            labels={
                "MEDICATION_COUNT": "Medication Count",
                "MEDICATION_DESCRIPTION": "Medication",
            },
        )

        fig_medications.update_layout(coloraxis_showscale=False)
        fig_medications.update_layout(yaxis={"categoryorder": "total ascending"})

        st.plotly_chart(
            style_chart(fig_medications),
            use_container_width=True,
            config={"displayModeBar": False},
        )


# -------------------------------------------------
# Cost and utilization tab
# -------------------------------------------------
with cost_tab:
    available_years = sorted(trend_df["YEAR"].dropna().unique().tolist())
    default_years = available_years[-5:] if len(available_years) >= 5 else available_years

    control_intro(
        "Filter the time-series chart",
        "The year filter and metric selector only affect this trend chart.",
    )

    filter_col, metric_col = st.columns([1.2, 0.8])

    with filter_col:
        selected_years = st.multiselect(
            "Years",
            available_years,
            default=default_years,
        )

    with metric_col:
        selected_metric = st.selectbox(
            "Metric",
            ["Encounter count", "Total claim cost", "Average claim cost"],
        )

    if not selected_years:
        st.warning("Select at least one year to show the trend chart.")
    else:
        metric_map = {
            "Encounter count": ("ENCOUNTER_COUNT", "Encounter Count", None),
            "Total claim cost": ("TOTAL_CLAIM_COST", "Total Claim Cost", "$"),
            "Average claim cost": ("AVG_CLAIM_COST", "Average Claim Cost", "$"),
        }

        metric_column, metric_label, tick_prefix = metric_map[selected_metric]

        filtered_trend_df = trend_df[trend_df["YEAR"].isin(selected_years)].copy()
        filtered_trend_df["YEAR_LABEL"] = filtered_trend_df["YEAR"].astype(str)

        section_intro(
            "Trend",
            selected_metric,
            "Shows how the selected metric changes by month for the selected years.",
        )

        month_order = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]

        fig_trend = px.line(
            filtered_trend_df,
            x="MONTH_NAME",
            y=metric_column,
            color="YEAR_LABEL",
            markers=True,
            color_discrete_sequence=COLOR_SEQUENCE,
            title=f"{metric_label} by Month",
            category_orders={"MONTH_NAME": month_order},
            labels={
                "MONTH_NAME": "Month",
                metric_column: metric_label,
                "YEAR_LABEL": "Year",
            },
        )

        fig_trend.update_traces(line=dict(width=3), marker=dict(size=7))

        if tick_prefix:
            fig_trend.update_yaxes(tickprefix=tick_prefix, separatethousands=True)

        st.plotly_chart(
            style_chart(fig_trend),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    section_intro(
        "Table",
        "Cost by age group",
        "Keeps exact values available after the chart view.",
    )

    st.dataframe(cost_age_df, use_container_width=True)


# -------------------------------------------------
# Data model tab
# -------------------------------------------------
with data_tab:
    section_intro(
        "Warehouse Design",
        "Modeled Snowflake MART layer",
        "The dashboard reads from curated views instead of raw CSV files. That keeps business logic in Snowflake and makes Streamlit responsible for presentation.",
    )

    model_col_1, model_col_2 = st.columns(2)

    with model_col_1:
        render_html(
            """
            <div class="model-card">
                <h4>Dimensions</h4>
                <p><code>DIM_PATIENT</code></p>
                <p><code>DIM_DATE</code></p>
                <p><code>DIM_CONDITION</code></p>
                <p><code>DIM_MEDICATION</code></p>
                <p><code>DIM_PROCEDURE</code></p>
            </div>
            """
        )

    with model_col_2:
        render_html(
            """
            <div class="model-card">
                <h4>Facts</h4>
                <p><code>FACT_ENCOUNTER</code></p>
                <p><code>FACT_CONDITION</code></p>
                <p><code>FACT_MEDICATION</code></p>
                <p><code>FACT_PROCEDURE</code></p>
            </div>
            """
        )

    st.markdown("### Source views")

    with st.expander("KPI Overview"):
        st.dataframe(kpi_df, use_container_width=True)

    with st.expander("Encounters by Age and Gender"):
        st.dataframe(age_gender_df, use_container_width=True)

    with st.expander("Top Conditions"):
        st.dataframe(top_conditions_df, use_container_width=True)

    with st.expander("Top Medications"):
        st.dataframe(top_medications_df, use_container_width=True)

    with st.expander("Encounter Trends"):
        st.dataframe(trend_df, use_container_width=True)

    with st.expander("Cost by Age Group"):
        st.dataframe(cost_age_df, use_container_width=True)
