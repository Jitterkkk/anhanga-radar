import json
import re
import google.generativeai as genai
from google.api_core.exceptions import PermissionDenied, Unauthenticated

MODELO = "gemini-2.0-flash"

CAMPOS = ["nome", "sobrenome", "cidade", "telefone", "fonte", "status", "observacoes"]

SYSTEM_PROMPT = """\
Você é um assistente que extrai dados estruturados de relatos de prospecção comercial \
com vereadores para a empresa Anhangá.AI.

Dado um texto em linguagem natural descrevendo um contato com um vereador, retorne \
EXCLUSIVAMENTE um objeto JSON válido com exatamente estes campos:

{
  "nome":        "<primeiro nome do vereador, ou vazio>",
  "sobrenome":   "<sobrenome do vereador, ou vazio>",
  "cidade":      "<cidade do vereador, ou vazio>",
  "telefone":    "<número de telefone mencionado, ou vazio>",
  "fonte":       "<canal usado: Ligação | WhatsApp | E-mail | Visita | outro>",
  "status":      "<resumo do desfecho: ex. Não atendeu | Caixa postal | Sem interesse | Recusou | Número errado>",
  "observacoes": "<qualquer detalhe relevante não coberto pelos outros campos, ou vazio>"
}

Regras:
- Se um campo não for mencionado no texto, use string vazia "".
- Não invente informações que não estejam no relato.
- Retorne apenas o JSON, sem markdown, sem explicações, sem texto adicional.\
"""


def extrair_dados(texto: str, api_key: str) -> dict:
    """Chama a API do Google Gemini e retorna dicionário com os campos extraídos."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=MODELO,
        system_instruction=SYSTEM_PROMPT,
    )

    try:
        resposta = model.generate_content(texto)
    except (PermissionDenied, Unauthenticated):
        raise ValueError(
            "API Key inválida. Verifique em aistudio.google.com"
        )

    raw = resposta.text.strip()
    dados = _parsear_json(raw)
    return _normalizar(dados)


# ── helpers ──────────────────────────────────────────────────────────────────

def _parsear_json(raw: str) -> dict:
    """Extrai e parseia o JSON da resposta, tolerando markdown ao redor."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        raw = match.group()
    return json.loads(raw)


def _normalizar(dados: dict) -> dict:
    """Garante que todos os campos existam e sejam strings."""
    return {campo: str(dados.get(campo, "") or "").strip() for campo in CAMPOS}
