# app.py — SMS agent (FastAPI + Twilio) — neutral, formal tone
# Flow: 1) ZIP  2) Bedrooms/Bathrooms  3) Cleaning Type  4) Time Window

import re
from typing import Dict

from fastapi import FastAPI, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()

# -----------------------------
# Simple in-memory sessions (demo).
# For production, store this in Redis/DB.
# -----------------------------
SESSIONS: Dict[str, Dict] = {}

ALLOWED_TYPES = {
    "standard": "Standard",
    "deep": "Deep",
    "move-out": "Move-Out",
    "move out": "Move-Out",
    "moveout": "Move-Out",
}

WINDOWS = {
    "8-10": "8–10 AM",
    "8–10": "8–10 AM",
    "10-12": "10–12 PM",
    "10–12": "10–12 PM",
    "1-3": "1–3 PM",
    "1–3": "1–3 PM",
}


def twiml(message: str) -> Response:
    """Return a proper TwiML response with the correct XML Content-Type."""
    r = MessagingResponse()
    r.message(message)
    return Response(content=str(r), media_type="application/xml")


def start_message() -> str:
    return (
        "Hello! Thank you for reaching out. Could you please share your ZIP code so we can "
        "calculate an estimate for your cleaning?"
    )


@app.get("/health")
async def health():
    return Response(content="ok", media_type="text/plain")


@app.post("/twilio/inbound")
async def inbound(Body: str = Form(""), From: str = Form("")):
    """
    Handles the 4-step flow:
      1) Ask ZIP
      2) Ask bedrooms and bathrooms
      3) Ask cleaning type (Standard / Deep / Move-Out)
      4) Offer time windows (8–10 AM, 10–12 PM, 1–3 PM)
    Type RESET anytime to restart the flow.
    """
    text = (Body or "").strip()
    phone = (From or "").strip()

    # Allow reset at any time
    if text.upper() in {"RESET", "RESTART"}:
        SESSIONS.pop(phone, None)
        SESSIONS[phone] = {"stage": "awaiting_zip"}
        return twiml(start_message())

    # Start a new session if needed
    session = SESSIONS.get(phone)
    if not session:
        SESSIONS[phone] = {"stage": "awaiting_zip"}
        return twiml(start_message())

    stage = session.get("stage")

    # ---- 1) ZIP ------------------------------------------------------------
    if stage == "awaiting_zip":
        m = re.search(r"\b(\d{5})\b", text)
        if not m:
            return twiml("Kindly provide a valid 5-digit ZIP code (e.g., 90210).")
        session["zip"] = m.group(1)
        session["stage"] = "awaiting_bedbath"
        return twiml(
            "Thank you. How many bedrooms and bathrooms does the home have? "
            "(e.g., 3 bedrooms, 2 bathrooms)."
        )

    # ---- 2) Bedrooms / Bathrooms ------------------------------------------
    if stage == "awaiting_bedbath":
        # Extract two numbers in any order, e.g., "3 bed 2 bath"
        nums = re.findall(r"\b\d+\b", text)
        if len(nums) < 2:
            return twiml(
                "Please provide both numbers — bedrooms and bathrooms "
                "(e.g., 3 bedrooms, 2 bathrooms)."
            )
        session["bedrooms"], session["bathrooms"] = nums[0], nums[1]
        session["stage"] = "awaiting_type"
        return twiml(
            "Great. Which type of cleaning do you need: Standard, Deep, or Move-Out?"
        )

    # ---- 3) Cleaning type --------------------------------------------------
    if stage == "awaiting_type":
        norm = text.lower()
        ctype = None
        for k, v in ALLOWED_TYPES.items():
            if k in norm:
                ctype = v
                break
        if not ctype:
            return twiml("Please choose one: Standard, Deep, or Move-Out.")
        session["type"] = ctype
        session["stage"] = "awaiting_window"
        return twiml(
            "We can offer availability windows 8–10 AM, 10–12 PM, or 1–3 PM. "
            "Which slot do you prefer? (You may also suggest another day/time.)"
        )

    # ---- 4) Time window ----------------------------------------------------
    if stage == "awaiting_window":
        norm = text.replace(" ", "").replace("am", "").replace("pm", "").lower()
        chosen = None
        for key, label in WINDOWS.items():
            if key in norm:
                chosen = label
                break
        if not chosen:
            return twiml(
                "Please choose one of these windows: 8–10 AM, 10–12 PM, or 1–3 PM. "
                "You may also propose another time."
            )

        session["window"] = chosen
        session["stage"] = "done"

        summary = (
            "Perfect — I have everything I need:\n"
            f"• ZIP: {session['zip']}\n"
            f"• Bedrooms: {session['bedrooms']}  • Bathrooms: {session['bathrooms']}\n"
            f"• Cleaning type: {session['type']}\n"
            f"• Preferred time: {session['window']}\n\n"
            "Our team will confirm availability and send your quote shortly. "
            "If you need to start over at any time, reply with RESET."
        )
        return twiml(summary)

    # Fallback if stage is unknown
    return twiml("I’m here to help. If you’d like to start over, reply with RESET.")
