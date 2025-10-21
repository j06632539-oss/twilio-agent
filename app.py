# ======================================
# AUTO-REPLY MESSAGE  (WhatsApp + Call/SMS)
# ======================================

from fastapi import FastAPI, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()

# --- Contatos ---
WHATSAPP_URL = (
    "https://wa.me/14254949012"
    "?text=Hello%21%20I%27d%20like%20to%20book%20a%20cleaning."
)
CALL_TEXT_NUMBER = "(425) 494-9012"

# --- Mensagem automática ---
AUTO_REPLY = (
    "Hello 👋\n"
    "This number is not monitored for messages.\n\n"
    "For assistance, please use one of the following options:\n"
    f"• WhatsApp: {WHATSAPP_URL}\n"
    f"• Call/Text: {CALL_TEXT_NUMBER}\n\n"
    "Thank you for reaching out!"
)

@app.get("/health")
async def health():
    return Response(content="ok", media_type="text/plain")

@app.post("/twilio/inbound")
async def inbound(Body: str = Form(""), From: str = Form("")):
    twiml = MessagingResponse()
    twiml.message(AUTO_REPLY)
    return Response(content=str(twiml), media_type="application/xml")
