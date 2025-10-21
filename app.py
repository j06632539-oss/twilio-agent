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
async def inbound(Body: str = Form(""), From: str = Form("")):
    reply_text = generate_reply(Body)
    twiml = MessagingResponse()
    twiml.message(reply_text)
    return Response(content=str(twiml), media_type="application/xml")
