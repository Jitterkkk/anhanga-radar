from groq import Groq
import json

_MODEL = "llama-3.3-70b-versatile"

_CAMPOS = (
    "nome, sobrenome, cidade, telefone, "
    "fonte (Ligação/WhatsApp/E-mail/Instagram/Indicação), "
    "status (use exatamente: Sem resposta, Não atendida, Número inexistente, "
    "Falha no contato, Sem interesse, Contato realizado, Agendado), "
    "observacoes. Campos não mencionados retornam string vazia."
)


def _chamar_groq(api_key, prompt):
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        msg = str(exc)
        if "rate_limit" in msg.lower() or "429" in msg:
            raise ValueError(
                "Limite de requisições atingido. Aguarde alguns segundos e tente novamente.\n"
                "Limite gratuito: 30 req/min e 14.400 req/dia."
            )
        if "invalid_api_key" in msg.lower() or "401" in msg:
            raise ValueError("Chave da API inválida. Verifique sua chave em console.groq.com")
        raise


def _parse_json(raw):
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"A IA não retornou JSON válido. Resposta recebida:\n{raw[:300]}")


def extrair_dados(texto: str, api_key: str) -> dict:
    prompt = (
        "Extraia informações de contato com vereador e retorne SOMENTE JSON válido, sem markdown.\n\n"
        f"Campos: {_CAMPOS}\n\nTexto: {texto}"
    )
    raw = _chamar_groq(api_key, prompt)
    return _parse_json(raw)


def extrair_multiplos(texto: str, api_key: str) -> list:
    prompt = (
        "Extraia TODOS os contatos com vereadores do texto abaixo.\n"
        "Cada parágrafo ou bloco separado por linha em branco é um contato diferente.\n"
        "Retorne SOMENTE um array JSON válido, sem markdown. Cada elemento deve ter:\n"
        f"{_CAMPOS}\n\n"
        f"Texto:\n{texto}"
    )
    raw = _chamar_groq(api_key, prompt)
    result = _parse_json(raw)
    if isinstance(result, dict):
        result = [result]
    return result
