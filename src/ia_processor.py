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

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    raw = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)
