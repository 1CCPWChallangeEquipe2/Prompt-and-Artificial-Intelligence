# EV Challenge — GoodWe | Sprint 03

Evolução do ChargeGrid Intelligence para uma arquitetura com agente de IA (LangChain).

## INTEGRANTES

| Nome              | RM       |
| ----------------- | -------- |
| Arthur Micarelli  | RM571476 |
| Enzo Yudi         | RM570173 |
| Felipe Elze       | RM572024 |
| Inaldo Freitas    | RM569672 |
| Henrique Silveira | RM571803 |


## Componentes
- Agente LangChain (`create_agent`) com 9 Tools (consumo, picos, usuários, cobrança, previsão, desempenho, financeiro, institucional GoodWe, saudação)
- Memória por sessão via `RunnableWithMessageHistory` + `InMemoryChatMessageHistory`
- Guardrail dedicado (pré-agente), cobrindo escopo, Prompt Injection e temas sensíveis (jurídico/financeiro/elétrico). Ele usa saída estruturada do LangChain (`with_structured_output` + Pydantic) para devolver uma categoria, roda com `temperature=0` e responde cada bloqueio indicando o profissional adequado (ver seção "Guardrail" abaixo)
- Comparação entre dois modelos configuráveis via `.env` (`MODEL_A` / `MODEL_B`)
- Mesmos CSVs da Sprint 2, com correção do bug de "data atual" (ver Seção 1 de `testes/testes.py`)
- CLI interativa no notebook (`run_chatbot`)
- O notebook agora importa tudo de `chatbot_core.py` em vez de duplicar o código — só tem uma versão do núcleo do agente

## Estrutura do projeto
```
Sprint-3/
├── chatbot_core.py                          # Núcleo do agente (extraído do notebook)
├── chargegrid_chatbot_sprint3.ipynb
├── requirements.txt
├── relatorio_modelos.md                     # Refazer com base em testes/resultado.txt
├── relatorio_evolucao_sprint3.pdf
├── integrantes.txt
├── dados/
│   ├── chargers.csv / energy_hourly.csv / sessions.csv / users.csv
└── testes/
    └── testes.py                            # ARQUIVO ÚNICO — roda tudo
```

## Configuração dos modelos (`.env`)
Crie um arquivo `.env` na raiz do projeto:
```env
OPENAI_API_KEY=sua_chave_aqui
MODEL_A=gpt-4o-mini
MODEL_B=outro_modelo_que_sua_conta_tenha_acesso
```

Se você não sabe quais modelos sua chave pode usar (por exemplo, se
`gpt-4o` retornar erro 403 "does not have access to model"), rode:
```bash
python testes/testes.py --listar-modelos
```
Isso lista os modelos de chat disponíveis para a sua conta, para você
escolher um `MODEL_B` válido. Se só houver um modelo disponível, o
sistema continua funcionando (usando o mesmo modelo nas duas pontas),
mas avisa isso claramente no resultado — a comparação entre 2 modelos
é exigência do enunciado (Seção 5) e deve ser resolvida assim que você
tiver acesso a um segundo modelo.

## Execução

**Chatbot interativo:** abra `chargegrid_chatbot_sprint3.ipynb`
e execute as células em ordem (ou chame `chatbot_core.run_chatbot()`).

**Todos os testes de uma vez:**
```bash
python testes/testes.py
```
Isso roda, em sequência:
1. Comparativo de arquitetura antes×depois (não usa IA)
2. Classificação do guardrail: confere se as perguntas normais são liberadas e se os casos de segurança caem na categoria certa (mostra `Acertos do guardrail: X/17`)
3. Testes funcionais (5 perguntas)
4. Testes de memória (2 cenários, 3 turnos cada), com `MODEL_A` e `MODEL_B`
5. Testes de segurança (Prompt Injection + escopo + jurídico/financeiro/elétrico)
6. Comparação de latência entre `MODEL_A` e `MODEL_B`

O resultado completo é salvo em texto simples em `testes/resultado.txt`.

## Guardrail

Toda mensagem passa primeiro pelo guardrail (`classificar_mensagem` em
`chatbot_core.py`), que devolve uma destas categorias:

| Categoria | O que acontece |
|---|---|
| `PERMITIDO` | A mensagem segue para o agente |
| `PROMPT_INJECTION` | Recusa e informa que não revela instruções internas |
| `FORA_DO_ESCOPO` | Informa que o assunto está fora do escopo e sugere o que o chatbot faz |
| `JURIDICO` | Não dá parecer e recomenda procurar um advogado |
| `FINANCEIRO_PESSOAL` | Não recomenda investimentos e indica um profissional financeiro certificado |
| `ELETRICO_PERIGOSO` | Não orienta desativar proteções e indica um eletricista habilitado |

Regras importantes:
- O prompt do guardrail descreve o escopo do projeto. Perguntas sobre consumo, picos, usuários, cobrança, faturamento, previsão, desempenho e GoodWe são `PERMITIDO`, mesmo escritas em primeira pessoa ("quanto consumi").
- Faturamento e modelo de cobrança do eletroposto **não** são aconselhamento financeiro.
- Na dúvida, a mensagem é `PERMITIDO`: o agente principal tem as mesmas regras de segurança no system prompt.
- Se a chamada ao guardrail der erro, a mensagem segue para o agente (em vez de derrubar o chatbot). Nos testes, esse erro aparece como `ERRO_API`.

### Correção feita após os primeiros testes
Na primeira versão, o guardrail bloqueou todas as perguntas normais. O prompt
mandava bloquear o que estivesse "fora do escopo", mas não dizia qual era o
escopo; a saída era um texto livre `ALLOWED`/`BLOCKED`; e todo bloqueio
recebia a mesma mensagem genérica. A versão atual corrige os três pontos
(escopo descrito com exemplos, categoria via saída estruturada e mensagem
específica por categoria).

## Como gerar o relatório a partir dos testes
1. Rode `python testes/testes.py`.
2. Abra `testes/resultado.txt`.
3. Copie o conteúdo e cole em uma IA pedindo para gerar o relatório de
   evolução (Seção 7 do enunciado) e/ou preencher `relatorio_modelos.md`
   com base nesses resultados reais.
