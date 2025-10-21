import os
from fastapi import FastAPI, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

# (Opcional) Integração com OpenAI, se quiser IA automática no futuro
try:
    from openai import OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception:
    OPENAI_API_KEY = ""
    openai_client = None

app = FastAPI()

SYSTEM_PROMPT = (
    "Você é o assistente da Mega/Casa Cleaning (PT/EN/ES). "
    "Seja direto, cordial e pró-ativo. Para orçamento, peça: ZIP, nº de quartos, nº de banheiros "
    "e tipo (Standard/Deep/Move-Out/Airbnb). Sugira janelas 8–10, 10–12 e 13–15."
)

def generate_reply(user_text: str) -> str:
    if not openai_client:
        return (
            "Olá! Para estimar sua limpeza, me informe ZIP, nº de quartos/banheiros e o tipo "
            "(Standard/Deep/Move-Out). Posso oferecer janelas 8–10, 10–12 ou 13–15. Qual prefere?"
        )
    try:
        chat = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text or ""},
            ],
            temperature=0.4,
        )
        return (chat.choices[0].message.content or "").strip() or "Como posso ajudar?"
    except Exception:
        return (
            "Olá! Para estimar sua limpeza, me informe ZIP, nº de quartos/banheiros e o tipo "
            "(Standard/Deep/Move-Out). Posso oferecer janelas 8–10, 10–12 ou 13–15. Qual prefere?"
        )

@app.get("/health")
async def health():
    return Response(content="ok", media_type="text/plain")

@app.post("/twilio/inbound")
@app.post("/twilio/inbound")
async def inbound(Body: str = Form(""), From: str = Form("")):
    reply = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Response>'
        '<Message>'
        "Hello! To estimate your cleaning, please provide your ZIP code, number of bedrooms and bathrooms, "
        "and the type of service (Standard / Deep / Move-Out). "
        "We can offer time windows between 8–10 AM, 10–12 PM, or 1–3 PM. Which one do you prefer?"
        '</Message>'
        '</Response>'
    )

    # This line ensures Twilio reads it correctly as an XML response
    return Response(content=reply, media_type="application/xml")
