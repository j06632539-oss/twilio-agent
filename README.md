
# Joao - Twilio SMS Agent (FastAPI)

Webhook mínimo para Twilio responder SMS/RCS via IA (OpenAI opcional).

## Endpoints
- `GET /health` → retorna `ok`
- `POST /twilio/inbound` → endpoint para configurar no Twilio (Messaging Service → Integration → Send a webhook)

## Variáveis de ambiente
- `OPENAI_API_KEY` (opcional): se definida, o agente responde com GPT-4o-mini; se não, responde com fallback padrão.

## Rodar local
```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 10000
curl -X POST http://localhost:10000/twilio/inbound       -H "Content-Type: application/x-www-form-urlencoded"       -d "Body=teste&From=+12135550000"
```

## Deploy rápido (Render)
1. Crie um novo Web Service no https://render.com
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. (Opcional) adicione `OPENAI_API_KEY` em **Environment**
5. Copie a URL pública e configure na Twilio: **Messaging Service → Integration → Send a webhook (HTTP POST)** → `https://SEU-APP.onrender.com/twilio/inbound`
