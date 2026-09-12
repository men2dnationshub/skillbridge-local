"""Shared visual components and brand styling."""

from __future__ import annotations

import html

import streamlit as st


def apply_brand_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { color: #061A40; }
        .hero {
            background: linear-gradient(135deg, #061A40 0%, #0B5ED7 100%);
            color: white;
            padding: 2.4rem;
            border-radius: 1.25rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 12px 30px rgba(6, 26, 64, 0.16);
        }
        .hero .eyebrow {
            color: #F4B41A;
            font-weight: 800;
            letter-spacing: 0.12em;
            font-size: 0.78rem;
        }
        .hero h1 { color: white; margin: 0.4rem 0 0.8rem; }
        .hero p { color: #E8F1FF; font-size: 1.08rem; margin: 0; max-width: 760px; }
        .status-pill {
            display: inline-block;
            padding: 0.45rem 0.75rem;
            border-radius: 999px;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .status-ready { background: #DDF7E8; color: #116B3A; }
        .status-pending { background: #FFF3CD; color: #755A00; }
        .footer { color: #5D6B82; font-size: 0.85rem; margin-top: 3rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(eyebrow: str, title: str, subtitle: str) -> None:
    safe_eyebrow = html.escape(eyebrow)
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    st.markdown(
        f"""
        <section class="hero">
            <div class="eyebrow">{safe_eyebrow}</div>
            <h1>{safe_title}</h1>
            <p>{safe_subtitle}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def status_badge(label: str, is_ready: bool) -> None:
    css_class = "status-ready" if is_ready else "status-pending"
    st.markdown(
        f'<span class="status-pill {css_class}">{html.escape(label)}</span>',
        unsafe_allow_html=True,
    )


def render_placeholder(title: str, description: str, milestone: str) -> None:
    apply_brand_styles()
    st.title(title)
    st.write(description)
    st.info(f"Planned for {milestone}. The current release contains the secure application shell.")
    st.markdown("#### What this area will include")


def render_footer(app_name: str) -> None:
    st.markdown(
        f'<p class="footer">{html.escape(app_name)} · Calabar pilot · MVP Milestone 1</p>',
        unsafe_allow_html=True,
    )

