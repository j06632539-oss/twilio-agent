# ======================================
# AUTO-REPLY MESSAGE (BookingKoala Link)
# ======================================

from fastapi import FastAPI, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()

@app.get("/health")
async def health():
    return Response(content="ok", media_type="text/plain")

@app.post("/twilio/inbound")
async def inbound(Body: str = Form(""), From: str = Form("")):
    # Texto de resposta automática
    AUTO_REPLY = (
        "Hello 👋\n"
        "This number is not monitored for messages.\n\n"
        "For assistance, please use one of the following options:\n"
        WHATSAPP_URL = "https://api.whatsapp.com/send?phone=14254949012&text=Hello!%20I’d%20like%20to%20book%20a%20cleaning."
        "• Call/Text: (425) 494-9012\n"
        "Thank you for reaching out!"
    )

    # Cria a resposta TwiML (formato exigido pelo Twilio)
    twiml = MessagingResponse()
    twiml.message(AUTO_REPLY)
    return Response(content=str(twiml), media_type="application/xml")
