# ======================================
# Auto-reply (SMS-first, then Call, then WhatsApp)
# ======================================

import re
from fastapi import FastAPI, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()

# ----- Contact constants -----
CALL_TEXT_NUMBER = "(425) 494-9012"
WHATSAPP_URL = "https://wa.me/14254949012"

# ----- Keyword buckets -----
THANKS_KWS = [
    "thanks", "thank you", "thx", "ty", "sounds good", "ok thank you", "okay thank you",
    "great thanks", "thank u", "appreciate it"
]

RESCHEDULE_KWS = [
    "reschedule", "change", "move", "another time", "different time", "push it",
    "can we do", "change this", "change date", "move my cleaning", "move my service",
    "schedule", "time window"
]

PAUSE_KWS = [
    "pause", "hold", "skip", "skip this", "skip cleaning", "put on hold"
]

CANCEL_KWS = [
    "cancel", "stop service", "stop my service", "no longer need", "won't need",
    "dont need", "do not need", "terminate", "end service"
]

# ----- Message builders -----
def build_default_message() -> str:
    return (
        "Hello 👋\n"
        "This number is not monitored for messages.\n\n"
        f"For assistance, please text us at {CALL_TEXT_NUMBER}.\n"
        f"If urgent, you can also call {CALL_TEXT_NUMBER}.\n"
        f"Optional: WhatsApp {WHATSAPP_URL}\n"
        "Thank you!"
    )

def build_intent_message(intent: str) -> str:
    base_header = "Hello 👋\nThis number is not monitored for messages.\n\n"
    if intent == "reschedule":
        body = (
            "To reschedule, please text us your request at "
            f"{CALL_TEXT_NUMBER}. If urgent, you can also call. "
            f"Optional: WhatsApp {WHATSAPP_URL}"
        )
    elif intent == "pause":
        body = (
            "To pause/hold/skip your cleaning, please text us at "
            f"{CALL_TEXT_NUMBER}. If urgent, you can also call. "
            f"Optional: WhatsApp {WHATSAPP_URL}"
        )
    elif intent == "cancel":
        body = (
            "To cancel, please text us at "
            f"{CALL_TEXT_NUMBER}. If urgent, you can also call. "
            f"Optional: WhatsApp {WHATSAPP_URL}"
        )
    else:
        # fallback generic
        body = (
            f"Please text us at {CALL_TEXT_NUMBER}. If urgent, you can also call. "
            f"Optional: WhatsApp {WHATSAPP_URL}"
        )
    return base_header + body

# ----- Utils -----
def normalize(text: str) -> str:
    text = text or ""
    text = text.lower()
    # keep letters, numbers and spaces to simplify matching
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def contains_any(text: str, keywords: list[str]) -> bool:
    return any(kw in text for kw in keywords)

# ----- Health check -----
@app.get("/health")
async def health():
    return Response(content="ok", media_type="text/plain")

# ----- Twilio inbound webhook -----
@app.post("/twilio/inbound")
async def inbound(Body: str = Form(""), From: str = Form("")):
    norm = normalize(Body)

    # 1) "Thanks / ok" => NO REPLY (return empty <Response/>)
    if contains_any(norm, THANKS_KWS):
        twiml = MessagingResponse()  # empty <Response/>
        return Response(content=str(twiml), media_type="application/xml")

    # 2) Specific intents
    if contains_any(norm, RESCHEDULE_KWS):
        reply_text = build_intent_message("reschedule")
    elif contains_any(norm, PAUSE_KWS):
        reply_text = build_intent_message("pause")
    elif contains_any(norm, CANCEL_KWS):
        reply_text = build_intent_message("cancel")
    else:
        # 3) Generic / unknown => default routing (SMS -> Call -> WhatsApp)
        reply_text = build_default_message()

    twiml = MessagingResponse()
    twiml.message(reply_text)
    return Response(content=str(twiml), media_type="application/xml")
