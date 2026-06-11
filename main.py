"""
Nova AI Systems — Proxy API pour le chatbot du site.
La clé Anthropic reste côté serveur, jamais dans le frontend.

Lancer en local :
    pip install fastapi uvicorn anthropic httpx python-dotenv --break-system-packages
    Copier backend/.env.example → backend/.env et remplir les valeurs
    uvicorn main:app --reload --port 8000

Déploiement : Railway (variable d'env ANTHROPIC_API_KEY dans le dashboard).
Côté frontend : remplacer l'URL du fetch dans index.html par
    https://<ton-app>.up.railway.app/api/chat
et envoyer {system, messages} (supprimer le champ model du frontend).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charge le .env local si présent (développement)
# En production Railway, les variables sont injectées directement
load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic

app = FastAPI(title="Nova Assistant Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://novaaisystems.fr",
        "https://www.novaaisystems.fr",
        "https://zippy-halva-309550.netlify.app",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:5501",
    ],
    allow_methods=["POST"],
    allow_headers=["*"],
)

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MODEL = "claude-haiku-4-5-20251001"  # rapide et économique pour ce rôle
MAX_MESSAGES = 14   # garde-fou serveur (le frontend limite déjà à 5 tours)
MAX_CHARS = 2000    # longueur max d'un message visiteur


class ChatRequest(BaseModel):
    system: str
    messages: list[dict]


class LeadRequest(BaseModel):
    email: str
    topic: str = "general"
    transcript: str = ""
    page: str = ""


@app.post("/api/lead")
def lead(req: LeadRequest):
    """Reçoit un lead du chatbot et envoie la conversation par email via Resend.
    Variables d'env requises : RESEND_API_KEY, LEAD_TO (ex: taha.elbermaki@novaaisystems.fr)."""
    import httpx

    resend_key = os.environ.get("RESEND_API_KEY")
    lead_to = os.environ.get("LEAD_TO", "taha.elbermaki@novaaisystems.fr")
    if not resend_key:
        raise HTTPException(500, "RESEND_API_KEY manquante")
    if len(req.transcript) > 20000:
        req.transcript = req.transcript[:20000]

    body = (
        f"Nouveau lead depuis le chatbot du site\n\n"
        f"Email : {req.email}\n"
        f"Sujet consulté : {req.topic}\n"
        f"Page : {req.page}\n\n"
        f"--- Conversation ---\n{req.transcript}"
    )
    r = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {resend_key}"},
        json={
            "from": "Nova Assistant <leads@novaaisystems.fr>",
            "to": [lead_to],
            "subject": f"🔥 Lead chatbot : {req.email}",
            "text": body,
        },
        timeout=10,
    )
    if r.status_code >= 400:
        raise HTTPException(502, "Envoi email échoué")
    return {"ok": True}



@app.post("/api/chat")
def chat(req: ChatRequest):
    if len(req.messages) > MAX_MESSAGES:
        raise HTTPException(429, "Conversation trop longue — réservez un RDV.")
    for m in req.messages:
        if len(str(m.get("content", ""))) > MAX_CHARS:
            raise HTTPException(413, "Message trop long.")

    response = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=req.system,
        messages=req.messages,
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    # Nettoyer le markdown
    text = text.replace("**", "").replace("*", "").replace("# ", "").replace("## ", "")
    return {"content": [{"type": "text", "text": text}]}


@app.get("/health")
def health():
    return {"status": "ok"}
