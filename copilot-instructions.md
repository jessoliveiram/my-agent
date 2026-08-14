# Copilot / Assistant Instructions (workspace)

Objetivo
- Auxiliar no desenvolvimento deste agente que integra Google Calendar e Gemini.

Context
- Este repositório contém um exemplo de integração com Google Calendar e Gemini (Generative AI).
- Todas as expecificações estão documentadas em `context.md` e `agent.md`.

Como eu trabalho aqui
- Faça mudanças pequenas e testáveis via `apply_patch`.
- Sempre execute testes locais antes de criar mudanças maiores: `pytest -q`.
- Use um ambiente virtual Python (`.venv`) e instale dependências com `pip install -r requirements.txt`.
- Utilize instruções em README.md e .agent.md para entender o propósito, persona, ferramentas permitidas e restrições do agente.

Regras importantes
- NUNCA adiciona chaves, credenciais ou `credentials.json` ao repositório.
- Se precisar de credenciais, instrua o usuário a adicioná-las ao `.env` e documente os nomes das variáveis de ambiente.
- Prefira alterações isoladas; explique as razões e os trade-offs em poucas linhas.

Style e qualidade
- Sugira e aplique pequenas refatorações que melhorem legibilidade e testabilidade.
- Ao propor alterações automáticas, sempre inclua um plano de teste rápido (comandos a executar).
- Mantenha o código consistente com as práticas recomendadas da linguagem e do framework.
- Siga as convenções de nomenclatura e estilo do projeto.

Testes e execução
- Ativar venv (PowerShell):
```powershell
venv\Scripts\Activate
pip install -r requirements.txt
pytest -q
```
- Executar o app (exemplo):
```powershell
python -m src.main
```

Se precisar de mais contexto, peça: 1) arquivo(s) a modificar, 2) objetivo curto (1-2 frases), 3) requisitos de teste.
