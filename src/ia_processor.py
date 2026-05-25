from google import genai
from google.genai import types
import json


def extrair_dados(texto: str, api_key: str) -> dict:
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(api_version="v1"),
    )

    prompt = f"""Extraia informações de contato com vereador e retorne SOMENTE JSON válido, sem markdown.

Campos: nome, sobrenome, cidade, telefone, fonte (Ligação/WhatsApp/E-mail/Instagram/Indicação),
status (use exatamente: Sem resposta, Não atendida, Número inexistente, Falha no contato, Sem interesse, Contato realizado, Agendado),
observacoes. Campos não mencionados retornam string vazia.

Texto: {texto}"""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
    except Exception as exc:
        msg = str(exc)
        if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
            raise ValueError(
                "Cota da API esgotada. Aguarde alguns minutos e tente novamente.\n"
                "Para mais detalhes: ai.google.dev/gemini-api/docs/rate-limits"
            )
        raise

    raw = response.text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"A IA não retornou JSON válido. Resposta recebida:\n{raw[:300]}")
