"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt_data():
    data = load_prompts(PROMPT_FILE)
    # O YAML tem uma chave raiz; retorna o primeiro valor se for dict aninhado
    if isinstance(data, dict):
        keys = list(data.keys())
        if keys and isinstance(data[keys[0]], dict) and "system_prompt" in data[keys[0]]:
            return data[keys[0]]
    return data


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado"
        assert prompt_data["system_prompt"].strip(), "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = prompt_data.get("system_prompt", "")
        role_keywords = ["você é", "you are", "its your job", "sua função", "seu papel", "atue como", "aja como"]
        lower = system_prompt.lower()
        assert any(kw in lower for kw in role_keywords), (
            "O system_prompt não define uma persona/role (ex: 'Você é um Product Manager')"
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data.get("system_prompt", "")
        format_keywords = [
            "user story", "como ", "para que", "critérios de aceitação",
            "dado que", "quando ", "então ", "markdown", "##", "###"
        ]
        lower = system_prompt.lower()
        assert any(kw in lower for kw in format_keywords), (
            "O system_prompt não menciona formato Markdown ou User Story padrão"
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data.get("system_prompt", "")
        few_shot_keywords = [
            "exemplo", "example", "por exemplo", "e.g.", "input:", "output:",
            "entrada:", "saída:", "ex:", "ex.:", "simples", "médio", "complexo"
        ]
        lower = system_prompt.lower()
        assert any(kw in lower for kw in few_shot_keywords), (
            "O system_prompt não parece conter exemplos few-shot (entrada/saída ou casos de exemplo)"
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que não há nenhum [TODO] no texto."""
        system_prompt = prompt_data.get("system_prompt", "")
        assert "TODO" not in system_prompt, "O system_prompt ainda contém marcadores TODO"
        assert "[todo]" not in system_prompt.lower(), "O system_prompt ainda contém marcadores [TODO]"

    def test_minimum_techniques(self, prompt_data):
        """Verifica se pelo menos 2 técnicas foram listadas nos metadados do yaml."""
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list), "O campo 'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas em 'techniques_applied', encontradas: {len(techniques)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])