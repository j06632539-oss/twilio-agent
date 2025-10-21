
import os
from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse

# Optional: OpenAI for smarter replies (set OPENAI_API_KEY to enable)
try:
    from openai import OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception:
    OPENAI_API_KEY = ""
    openai_client = None

app = FastAPI()

SYSTEM_PROMPT = (
    "Você é o assistente da Casa/Mega Cleaning (PT/EN/ES). "
    "Seja direto, cordial e pró-ativo. Para orçamento, peça: ZIP, nº de quartos, nº de banheiros "
    "e tipo (Standard/Deep/Move-Out/Airbnb). Sugira 3 janelas (8–10, 10–12, 13–15). "
    "Nunca confirme reserva sem endereço + telefone + e-mail."
)

def generate_reply(user_text: str) -> str:
    # Fallback simples sem OpenAI
    if not openai_client:
        return (
            "Olá! Para estimar sua limpeza, me informe ZIP, nº de quartos/banheiros "
            "e o tipo (Standard/Deep/Move-Out). Posso oferecer janelas 8–10, 10–12 ou 13–15. "
            "Qual prefere?"
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
        return (chat.choices[0].message.content or "").strip() or "Certo! Como posso ajudar?"
    except Exception as e:
        # Em caso de erro com OpenAI, volta para fallback
        return (
            "Oi! Para estimar, preciso do ZIP, nº de quartos/banheiros e tipo de limpeza "
            "(Standard/Deep/Move-Out). Posso oferecer 8–10, 10–12 ou 13–15."
        )

@app.get("/health", response_class=PlainTextResponse)
async def health():
    return "ok"

@app.post("/twilio/inbound", response_class=PlainTextResponse)
async def twilio_inbound(Body: str = Form(""), From: str = Form("")):
    # 1) Gera resposta do agente
    reply_text = generate_reply(Body)

    # 2) Constrói TwiML (obrigatório para Twilio)
    twiml = MessagingResponse()
    twiml.message(reply_text)
    return str(twiml)
