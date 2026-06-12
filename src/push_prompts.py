"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

PROMPT_NAME = "bug_to_user_story_v2"
INPUT_PATH = "prompts/bug_to_user_story_v2.yml"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
        return False

    repo_full_name = f"{username}/{prompt_name}"
    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])

    try:
        client = Client()
        url = client.push_prompt(repo_full_name, object=prompt, is_public=True)
        print(f"✅ Prompt enviado com sucesso: {url}")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    print_section_header("Push de Prompt Otimizado para o LangSmith Hub")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    print(f"Carregando prompt de: {INPUT_PATH}")
    yaml_data = load_yaml(INPUT_PATH)
    if yaml_data is None:
        print(f"❌ Falha ao carregar {INPUT_PATH}")
        return 1

    prompt_data = yaml_data.get(PROMPT_NAME)
    if prompt_data is None:
        print(f"❌ Chave '{PROMPT_NAME}' não encontrada no YAML")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✅ Prompt válido")

    success = push_prompt_to_langsmith(PROMPT_NAME, prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
