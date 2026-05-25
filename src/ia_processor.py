from google import genai
import json


def extrair_dados(texto: str, api_key: str) -> dict:
    client = genai.Client(api_key=api_key)

    prompt = f"""Extraia informações de contato com vereador e retorne SOMENTE JSON válido, sem markdown.

Campos: nome, sobrenome, cidade, telefone, fonte (Ligação/WhatsApp/E-mail/Instagram/Indicação),
status (use exatamente: Sem resposta, Não atendida, Número inexistente, Falha no contato, Sem interesse, Contato realizado, Agendado),
observacoes. Campos não mencionados retornam string vazia.

Texto: {texto}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
        )
    except Exception as exc:
        msg = str(exc)
        if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
            raise ValueError(
                "Cota da API esgotada. Aguarde alguns minutos e tente novamente.\n"
                "Limite gratuito: 30 req/min e 1500 req/dia."
            )
        if "NOT_FOUND" in msg or "404" in msg:
            raise ValueError(
                "Modelo não encontrado. Verifique se a chave do AI Studio está correta."
            )
        raise

    raw = response.text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"A IA não retornou JSON válido. Resposta recebida:\n{raw[:300]}")
