"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_REPO = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith():
    """Faz pull do prompt do LangSmith Hub e salva localmente."""
    print_section_header("Pull de Prompts do LangSmith Hub")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return False

    print(f"Pulling prompt: {PROMPT_REPO}")
    client = Client()
    prompt = client.pull_prompt(PROMPT_REPO, dangerously_pull_public_prompt=True)

    messages = prompt.messages
    system_prompt = ""
    user_prompt = ""

    for msg in messages:
        content = ""
        if hasattr(msg, "prompt") and hasattr(msg.prompt, "template"):
            content = msg.prompt.template
        elif hasattr(msg, "content"):
            content = msg.content

        role = type(msg).__name__.lower()
        if "system" in role:
            system_prompt = content
        elif "human" in role or "user" in role:
            user_prompt = content

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if save_yaml(prompt_data, OUTPUT_PATH):
        print(f"Prompt salvo em: {OUTPUT_PATH}")
        return True
    else:
        print("Falha ao salvar prompt.")
        return False


def main():
    """Função principal"""
    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
