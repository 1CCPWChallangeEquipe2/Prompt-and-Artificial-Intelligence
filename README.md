# ChargeGrid Intelligence — Chatbot de Gestão Operacional
## Base Teórica · Sprint 1 · EV Challenge 2026 · GoodWe × FIAP

---

## INTEGRANTES

| Nome              | RM       |
| ----------------- | -------- |
| Arthur Micarelli  | RM571476 |
| Enzo Yudi         | RM570173 |
| Felipe Elze       | RM572024 |
| Inaldo Freitas    | RM569672 |
| Henrique Silveira | RM571803 |


---

## 1. PROBLEMA ABORDADO

Operadores de eletropostos comerciais precisam tomar decisões rápidas sobre consumo de energia,
cobrança e desempenho dos carregadores — mas hoje isso exige acessar dashboards técnicos,
relatórios exportados e planilhas separadas.

O chatbot resolve isso com uma dinâmica conversacional simples: o operador pergunta em
linguagem natural e recebe respostas diretas baseadas nos dados reais do eletroposto também em linguagem natural .

---

## 2. PERSONA

**Operador Comercial de Eletroposto**

Gestor responsável pelo dia a dia de um eletroposto em shopping, hotel ou empresa.
Não é técnico — precisa de respostas rápidas sobre o que está acontecendo com seu
ponto de recarga, quanto está gastando, quanto está ganhando e o que fazer a seguir.

---

## 3. ESCOPO DO CHATBOT

O chatbot funciona como um **assistente de gestão conversacional**: ele consulta os dados
do eletroposto e responde perguntas operacionais em linguagem natural.

**Exemplos de perguntas que o chatbot deve responder:**

| Categoria | Pergunta exemplo |
|-----------|-----------------|
| Consumo geral | "Quanto de energia consumi esse mês no total e por carregador?" |
| Picos de energia | "Tive algum pico de energia essa semana?" |
| Usuários | "Qual foi a pessoa que mais consumiu energia este mês?" |
| Cobrança inteligente | "Baseado no meu histórico, qual modelo de cobrança seria mais vantajoso?" |
| Previsão | "Qual é a previsão de uso para amanhã?" |
| Desempenho | "Qual carregador ficou mais tempo ocioso esse mês?" |
| Financeiro | "Quanto eu teria faturado se cobrasse R$ 1,80/kWh esse mês?" |

**O que o chatbot NÃO faz (v1):**
- Executar ações diretas (ligar/desligar carregadores)
- Responder dúvidas fora do contexto do eletroposto
- Dar assessoria jurídica ou tributária

---

## 4. TECNOLOGIAS

| Componente | Escolha | Justificativa |
|------------|---------|---------------|
| LLM | OpenAI API | Modelos de linguagem natural com boa compreensão de português e dados numéricos |
| Orquestração | LangChain | Facilita gerenciamento de contexto, memória de conversa, integração com banco de dados e execução de fluxos inteligentes |
| Dados do eletroposto | Banco Relacional / Banco Não Relacional | A definição ainda será validada nas próximas etapas do projeto. O modelo relacional oferece maior organização para dados estruturados como sessões de recarga, usuários, faturamento e consumo energético. Já o modelo não relacional oferece maior flexibilidade para armazenar históricos conversacionais, logs operacionais e dados variáveis de telemetria dos carregadores. |
| Linguagem | python | Linguagem amplamente utilizada em IA, integração de APIs, processamento de dados e com vasta gama de bibliotecas |

**Lógica central:** o chatbot não "sabe" os dados de memória — a cada pergunta,
os dados relevantes do eletroposto são buscados e injetados no prompt junto com
a pergunta do usuário. O LLM interpreta e responde em linguagem natural.

---

## 5. FLUXO DE FUNCIONAMENTO

```
Operador digita uma pergunta
          ↓
Sistema identifica o tipo de consulta
(consumo / pico / usuário / previsão /
cobrança / desempenho)
          ↓
 ┌───────────────────────────────┐
 │ A pergunta está no escopo?    │
 └───────────────────────────────┘
          ↓                     ↓
         SIM                   NÃO
          ↓                     ↓
Busca os dados            Chatbot informa que
correspondentes           é especializado em
no banco de dados         gestão de eletropostos
          ↓                     ↓
Monta o prompt com:      Sugere exemplos do que
[System Prompt] +        pode responder dentro
[Dados encontrados] +    desse contexto
[Pergunta do usuário]
          ↓                     ↓
LLM processa as          Resposta exibida
informações              ao operador
          ↓                     ↓
Gera resposta            Retornar ao inicio 
contextualizada          do fluxo
em linguagem natural
          ↓
Resposta exibida ao operador
          ↓
Histórico da conversa é mantido
para perguntas complementares
```

---

## 6. SYSTEM PROMPT INICIAL

```
Você é o assistente de gestão do ChargeGrid Intelligence, plataforma de
eletropostos comerciais da GoodWe × FIAP.

SOBRE QUEM VOCÊ ATENDE:
Você fala com operadores comerciais de eletropostos — gestores responsáveis pelo
dia a dia de pontos de recarga em shoppings, hotéis ou empresas. Eles NÃO são
técnicos. Precisam de respostas rápidas, claras e práticas sobre o que está
acontecendo no eletroposto, quanto estão gastando, quanto estão faturando e o
que fazer a seguir.

SEU PAPEL:
Responder perguntas operacionais do operador com base nos dados reais de consumo,
sessões de recarga e histórico de uso fornecidos a você em cada mensagem.
Você não "memoriza" dados entre chamadas — os dados relevantes são buscados e
injetados no contexto a cada pergunta. Use apenas esses dados para responder.

CATEGORIAS DE PERGUNTAS QUE VOCÊ RESPONDE:
- Consumo geral: total e por carregador, por período
- Picos de energia: identificação de picos acima do teto configurado
- Usuários: quem mais consumiu, padrão de uso, sessões por usuário
- Cobrança inteligente: recomendação de modelo de cobrança (kWh, tempo, sessão)
  com base no perfil histórico do eletroposto
- Previsão de uso: estimativas para os próximos períodos baseadas no histórico
- Desempenho dos carregadores: tempo ocioso, sessões por carregador, eficiência
- Análise financeira: projeções de faturamento por tarifa, comparação de cenários

O QUE VOCÊ NÃO FAZ:
- Não executa ações nos sistemas (não liga, desliga ou reconfigura carregadores)
- Não responde perguntas fora do contexto de gestão do eletroposto
- Não fornece assessoria jurídica ou tributária
- Não inventa números — se os dados não estiverem no contexto, diz claramente

REGRAS:
- Responda sempre em português brasileiro, de forma direta e objetiva.
- Use exclusivamente os dados fornecidos no contexto para embasar cada resposta.
- Se os dados forem insuficientes para responder com precisão, diga isso
  claramente e oriente o operador sobre o que seria necessário.
- Nunca invente métricas, valores ou tendências.
- Adapte o nível de detalhe à pergunta: respostas simples para perguntas simples,
  breakdowns completos quando o operador precisar de análise.

FORMATO DAS RESPOSTAS:
1. Resposta direta primeiro (1–2 frases resumindo o ponto principal).
2. Dados ou breakdown quando necessário (listas simples, sem jargão técnico).
3. Recomendação ou insight adicional quando pertinente — especialmente em
   perguntas de cobrança, desempenho e previsão.

Exemplos de estrutura esperada:
- Para consumo: total → por carregador → destaque se houver anomalia
- Para picos: confirmação → data/hora/valor do pico → comparação com teto
- Para usuários: usuário principal → kWh total → sessões → média por sessão
- Para cobrança: modelo recomendado → motivos → valor estimado sugerido
- Para previsão: horário de pico esperado → consumo estimado → horário de menor uso
- Para financeiro: valor calculado → premissas usadas → comparação de cenários se aplicável

CONTEXTO TÉCNICO DO SISTEMA (para interpretar os dados):
Os eletropostos operam com controle de demanda (peak shaving, load balancing),
protocolos OCPP e MODBUS, modelos de cobrança variados (por kWh, por tempo ou
por sessão) e inteligência artificial para previsão de demanda e otimização do
uso combinado de energia da rede, solar e bateria.

TRATAMENTO DE PERGUNTAS FORA DO ESCOPO:
- Informe educadamente que você é especializado em gestão de eletropostos.
- Não tente responder sobre outros temas.
- Sugira exemplos concretos do que pode ser perguntado:
  "Posso te ajudar com consumo por carregador, picos de energia desta semana,
  faturamento estimado por tarifa, previsão de uso para amanhã ou desempenho
  dos seus carregadores. Qual dessas você quer ver?"
- Mantenha a conversa aberta para que o operador reformule a pergunta.
```

---

## 7. MODELO DE TESTE — PERGUNTAS E RESPOSTAS ESPERADAS

---

**Pergunta 1 — Consumo geral**
> "Quanto de energia consumi esse mês no total e por carregador?"

**Resposta esperada:**
> No mês de maio você consumiu **847 kWh no total**.
>
> Por carregador:
> - Carregador #1 (22 kW): 312 kWh
> - Carregador #2 (22 kW): 298 kWh
> - Carregador #3 (11 kW): 237 kWh

---

**Pergunta 2 — Picos de energia**
> "Tive algum pico de energia essa semana?"

**Resposta esperada:**
> Sim. Na terça-feira às 19h14 foi registrado um pico de **68 kW simultâneos**,
> acima do teto configurado de 60 kW.

---

**Pergunta 3 — Usuário com maior consumo**
> "Qual foi a pessoa que mais consumiu energia este mês?"

**Resposta esperada:**
> O usuário com ID **USR-0047** (Inaldo Freitas) liderou o consumo em maio com **94 kWh**,
> distribuídos em 11 sessões de recarga.
>
> Média por sessão: 8,5 kWh · Duração média: 52 minutos.

---

**Pergunta 4 — Recomendação de modelo de cobrança**
> "Baseado no meu histórico, qual modelo de cobrança seria mais vantajoso para mim?"

**Resposta esperada:**
> Com base nos últimos 30 dias, a maioria das sessões (73%) dura entre 40 e 70
> minutos e consome entre 7 e 12 kWh.
>
> **Recomendação: cobrança por kWh** (R$ 1,80–2,20/kWh estimado para seu perfil).
>
> Motivos:
> - Sessões têm duração e consumo consistentes — sem distorções que prejudiquem o motorista.
> - A cobrança por tempo favoreceria usuários de carros de alta potência, que carregam
>   mais rápido pagando o mesmo.
> - Por kWh é percebido como mais justo e gera menos reclamações.
>
> Uma taxa de desbloqueio de R$ 3–5 por sessão pode cobrir custos fixos operacionais.

---

**Pergunta 5 — Previsão de uso**
> "Qual é a previsão de uso para amanhã?"

**Resposta esperada:**
> Com base nos dados históricos de uso, a previsão é:
>
> - **Pico esperado:** entre 18h e 20h, com até 3 carregadores simultâneos.
> - **Consumo estimado:** 210–240 kWh ao longo do dia.
> - **Horário de menor uso:** 11h–13h (média de 0,8 carregadores ativos).

---

## 8. Primeira Modelagem do Banco

> **Esta modelagem é simplista, com intuito de inspirar as futuras, toda realizada em DataFrames**

> * **df_users**
```
df_users.columns = [
    "user_id",             # ID único do usuário
    "user_name",           # Nome do usuário
    "user_type",           # app_driver / corporate / casual
    "company",             # Empresa vinculada (se existir)
    "vehicle_model",       # Modelo do veículo
    "profile_cluster",     # cluster de uso (frotista/app/esporadico)
    "created_at"           # Data de cadastro
]
```

> * **df_chargers**
```
df_chargers.columns = [
    "charger_id",          # ID único do carregador
    "charger_name",        # Nome amigável
    "site_id",             # ID do eletroposto/local
    "power_kw",            # Potência máxima
    "connector_type",      # Tipo do conector
    "status",              # online/offline/maintenance
    "installation_date"    # Data de instalação
]
```

> * **df_sessions**
```
df_sessions.columns = [
    "session_id",          # ID da sessão
    "user_id",             # FK -> users
    "charger_id",          # FK -> chargers
    "start_ts",            # Início da sessão
    "end_ts",              # Fim da sessão
    "duration_min",        # Duração em minutos
    "energy_kwh",          # Energia consumida
    "avg_power_kw",        # Potência média
    "pricing_model",       # kwh/time/session/subscription
    "price_per_kwh",       # Valor cobrado por kWh
    "session_cost_brl",    # Valor total da sessão
    "payment_method",      # pix/card/rfid/app
    "session_status"       # completed/interrupted/error
]
```

> * **df_energy_hourly**
```
df_energy_hourly.columns = [
    "timestamp",               # Timestamp da hora
    "site_id",                 # ID do eletroposto
    "site_load_kw",            # Consumo total do site
    "solar_generation_kw",     # Geração solar
    "battery_level_percent",   # Nível da bateria
    "battery_flow_kw",         # + descarregando / - carregando
    "grid_import_kw",          # Energia puxada da rede
    "active_chargers",         # Quantos carregadores ativos
    "peak_limit_kw",           # Limite contratado
    "peak_flag"                # True/False para pico
]
```

> **Relações entre os Data Frames**
```
df_users
    user_id
        ↓

df_sessions
    user_id
    charger_id
        ↓

df_chargers
    charger_id
```

---

* Sprint 1 — EV Challenge 2026 · GoodWe × FIAP
