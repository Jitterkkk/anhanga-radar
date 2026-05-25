import google.generativeai as genai
import json

def extrair_dados(texto: str, api_key: str) -> dict:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={"temperature": 0.1}
    )
    prompt = f"""Extraia informações de contato com vereador e retorne SOMENTE JSON válido, sem markdown.

Campos: nome, sobrenome, cidade, telefone, fonte (Ligação/WhatsApp/E-mail/Instagram/Indicação),
status (use exatamente: Sem resposta, Não atendida, Número inexistente, Falha no contato, Sem interesse, Contato realizado, Agendado),
observacoes. Campos não mencionados retornam string vazia.

Texto: {texto}"""

    response = model.generate_content(prompt)
    raw = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)
