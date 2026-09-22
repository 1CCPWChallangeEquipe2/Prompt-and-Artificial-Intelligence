# %%
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv


# %%
# ─────────────────────────────────────────────
# CLIENTE OPENAI
# ─────────────────────────────────────────────
load_dotenv(dotenv_path="..\.env")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# %%
df_chargers = pd.read_csv(r"..\dados\chargers.csv")
df_energy_hourly = pd.read_csv(r"..\dados\energy_hourly.csv")
df_sessions = pd.read_csv(r"..\dados\sessions.csv")
df_users = pd.read_csv(r"..\dados\users.csv")


# %% [markdown]
# ## FUNÇÕES DE CONSULTA AOS DATAFRAMES
# 

# %%
# ─────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────

def garantir_datetime(df, coluna):
    """
    Garante que uma coluna esteja em datetime.
    """

    df = df.copy()

    if not pd.api.types.is_datetime64_any_dtype(
        df[coluna]
    ):
        df[coluna] = pd.to_datetime(
            df[coluna],
            errors="coerce"
        )

    return df


# ─────────────────────────────────────────────
# CONSUMO
# ─────────────────────────────────────────────

def get_dados_consumo(
    df_sessions,
    df_chargers
):

    df_sessions = garantir_datetime(
        df_sessions,
        "start_ts"
    )

    agora = datetime.now()

    df_mes = df_sessions[
        (df_sessions["start_ts"].dt.month == agora.month) &
        (df_sessions["start_ts"].dt.year == agora.year)
    ].copy()

    energia_total = round(
        df_mes["energy_kwh"].sum(),
        2
    )

    consumo_por_carregador = (
        df_mes.groupby("charger_id")
        .agg({
            "energy_kwh": "sum",
            "session_id": "count"
        })
        .rename(columns={
            "energy_kwh": "energia_total_kwh",
            "session_id": "total_sessoes"
        })
        .reset_index()
    )

    ultimas_sessoes = (
        df_mes.sort_values(
            "start_ts",
            ascending=False
        )
        .head(10)[[
            "session_id",
            "charger_id",
            "energy_kwh",
            "duration_min",
            "session_cost_brl",
            "start_ts"
        ]]
    )

    return f"""
=== RESUMO DE CONSUMO ===

Mês referência:
{agora.month:02d}/{agora.year}

Energia total consumida:
{energia_total} kWh


=== CONSUMO POR CARREGADOR ===
{consumo_por_carregador.to_string(index=False)}


=== ÚLTIMAS SESSÕES ===
{ultimas_sessoes.to_string(index=False)}


=== CARREGADORES CADASTRADOS ===
{df_chargers.to_string(index=False)}
"""


# ─────────────────────────────────────────────
# PICOS
# ─────────────────────────────────────────────

def get_dados_picos(
    df_energy_hourly
):

    df_energy_hourly = garantir_datetime(
        df_energy_hourly,
        "timestamp"
    )

    semana_atras = (
        datetime.now() - timedelta(days=7)
    )

    df_semana = df_energy_hourly[
        df_energy_hourly["timestamp"]
        >= semana_atras
    ].copy()

    picos = df_semana[
        df_semana["peak_flag"] == True
    ]

    maior_carga = round(
        df_semana["site_load_kw"].max(),
        2
    )

    media_carga = round(
        df_semana["site_load_kw"].mean(),
        2
    )

    return f"""
=== RESUMO ENERGÉTICO ===

Maior carga observada:
{maior_carga} kW

Carga média:
{media_carga} kW

Quantidade de picos:
{len(picos)}


=== EVENTOS DE PICO ===
{picos.head(10).to_string(index=False)}


=== LEITURAS RECENTES ===
{df_semana.tail(20).to_string(index=False)}
"""


# ─────────────────────────────────────────────
# USUÁRIOS
# ─────────────────────────────────────────────

def get_dados_usuarios(
    df_sessions,
    df_users
):

    df_sessions = garantir_datetime(
        df_sessions,
        "start_ts"
    )

    agora = datetime.now()

    df_mes = df_sessions[
        (df_sessions["start_ts"].dt.month == agora.month) &
        (df_sessions["start_ts"].dt.year == agora.year)
    ].copy()

    ranking = (
        df_mes.groupby("user_id")
        .agg({
            "energy_kwh": "sum",
            "session_id": "count"
        })
        .rename(columns={
            "energy_kwh": "energia_total_kwh",
            "session_id": "total_sessoes"
        })
        .reset_index()
        .sort_values(
            "energia_total_kwh",
            ascending=False
        )
    )

    ranking = ranking.merge(
        df_users[
            ["user_id", "user_name"]
        ],
        on="user_id",
        how="left"
    )

    ultimas_sessoes = (
        df_mes.sort_values(
            "start_ts",
            ascending=False
        )
        .head(10)[[
            "session_id",
            "user_id",
            "energy_kwh",
            "session_cost_brl",
            "start_ts"
        ]]
    )

    return f"""
=== RESUMO DE USUÁRIOS ===

Total de usuários:
{len(df_users)}

Total de sessões no mês:
{len(df_mes)}

Usuário com maior consumo:
{ranking.iloc[0]["user_name"]
if len(ranking) > 0 else "N/A"}


=== RANKING DE CONSUMO ===
{ranking.head(10).to_string(index=False)}


=== ÚLTIMAS SESSÕES ===
{ultimas_sessoes.to_string(index=False)}


=== USUÁRIOS CADASTRADOS ===
{df_users.to_string(index=False)}
"""


# ─────────────────────────────────────────────
# COBRANÇA
# ─────────────────────────────────────────────

def get_dados_cobranca(
    df_sessions
):

    df_sessions = garantir_datetime(
        df_sessions,
        "start_ts"
    )

    data_limite = (
        datetime.now() - timedelta(days=30)
    )

    df_30 = df_sessions[
        df_sessions["start_ts"]
        >= data_limite
    ].copy()

    media_energia = round(
        df_30["energy_kwh"].mean(),
        2
    )

    media_duracao = round(
        df_30["duration_min"].mean(),
        2
    )

    ticket_medio = round(
        df_30["session_cost_brl"].mean(),
        2
    )

    if media_energia > 12:
        recomendacao = "Cobrança por kWh"

    elif media_duracao > 60:
        recomendacao = "Cobrança por tempo"

    else:
        recomendacao = "Cobrança por sessão"

    resumo_usuario = (
        df_30.groupby("user_id")
        .agg({
            "energy_kwh": "sum",
            "duration_min": "mean",
            "session_cost_brl": "mean"
        })
        .reset_index()
    )

    return f"""
=== ANÁLISE DE COBRANÇA ===

Média de energia:
{media_energia} kWh

Média de duração:
{media_duracao} min

Ticket médio:
R$ {ticket_medio}

Modelo recomendado:
{recomendacao}


=== RESUMO POR USUÁRIO ===
{resumo_usuario.to_string(index=False)}


=== SESSÕES ANALISADAS ===
{df_30.tail(15).to_string(index=False)}
"""


# ─────────────────────────────────────────────
# PREVISÃO
# ─────────────────────────────────────────────

def get_dados_previsao(
    df_sessions
):

    df_sessions = garantir_datetime(
        df_sessions,
        "start_ts"
    )

    df = df_sessions.copy()

    df["dia_semana"] = (
        df["start_ts"]
        .dt.day_name()
    )

    df["hora"] = (
        df["start_ts"]
        .dt.hour
    )

    sessoes_por_dia = (
        df.groupby("dia_semana")
        .size()
        .reset_index(name="total_sessoes")
    )

    horarios_pico = (
        df.groupby("hora")
        .size()
        .reset_index(name="total")
        .sort_values(
            "total",
            ascending=False
        )
    )

    media_diaria = round(
        len(df) / max(
            df["start_ts"].dt.date.nunique(),
            1
        ),
        2
    )

    previsao_amanha = round(
        media_diaria * 1.05,
        0
    )

    return f"""
=== PREVISÃO DE USO ===

Média diária de sessões:
{media_diaria}

Previsão de sessões amanhã:
{int(previsao_amanha)}


=== HORÁRIOS DE PICO ===
{horarios_pico.head(10).to_string(index=False)}


=== USO POR DIA DA SEMANA ===
{sessoes_por_dia.to_string(index=False)}


=== HISTÓRICO RECENTE ===
{df.tail(20).to_string(index=False)}
"""


# ─────────────────────────────────────────────
# DESEMPENHO
# ─────────────────────────────────────────────

def get_dados_desempenho(
    df_sessions,
    df_chargers
):

    df_sessions = garantir_datetime(
        df_sessions,
        "start_ts"
    )

    agora = datetime.now()

    df_mes = df_sessions[
        (df_sessions["start_ts"].dt.month == agora.month) &
        (df_sessions["start_ts"].dt.year == agora.year)
    ].copy()

    desempenho = (
        df_mes.groupby("charger_id")
        .agg({
            "session_id": "count",
            "energy_kwh": "sum",
            "avg_power_kw": "mean"
        })
        .rename(columns={
            "session_id": "total_sessoes",
            "energy_kwh": "energia_total_kwh",
            "avg_power_kw": "potencia_media_kw"
        })
        .reset_index()
    )

    desempenho = desempenho.merge(
        df_chargers[
            ["charger_id", "charger_name"]
        ],
        on="charger_id",
        how="left"
    )

    return f"""
=== DESEMPENHO DOS CARREGADORES ===

Total de carregadores:
{len(df_chargers)}

Total de sessões:
{len(df_mes)}


=== RANKING DE DESEMPENHO ===
{desempenho.sort_values(
    'energia_total_kwh',
    ascending=False
).to_string(index=False)}


=== ÚLTIMAS SESSÕES ===
{df_mes.tail(15).to_string(index=False)}
"""


# ─────────────────────────────────────────────
# FINANCEIRO
# ─────────────────────────────────────────────

def get_dados_financeiro(
    df_sessions
):

    df_sessions = garantir_datetime(
        df_sessions,
        "start_ts"
    )

    agora = datetime.now()

    df_mes = df_sessions[
        (df_sessions["start_ts"].dt.month == agora.month) &
        (df_sessions["start_ts"].dt.year == agora.year) &
        (df_sessions["session_status"] == "completed")
    ].copy()

    faturamento_total = round(
        df_mes["session_cost_brl"].sum(),
        2
    )

    ticket_medio = round(
        df_mes["session_cost_brl"].mean(),
        2
    )

    faturamento_pagamento = (
        df_mes.groupby("payment_method")
        .agg({
            "session_cost_brl": "sum",
            "session_id": "count"
        })
        .rename(columns={
            "session_cost_brl":
                "faturamento_total_brl",
            "session_id":
                "total_sessoes"
        })
        .reset_index()
    )

    return f"""
=== RESUMO FINANCEIRO ===

Mês referência:
{agora.month:02d}/{agora.year}

Faturamento total:
R$ {faturamento_total}

Ticket médio:
R$ {ticket_medio}


=== FATURAMENTO POR PAGAMENTO ===
{faturamento_pagamento.to_string(index=False)}


=== SESSÕES CONCLUÍDAS ===
{df_mes.tail(20).to_string(index=False)}
"""

# %% [markdown]
# ## ORQUESTRADOR
# 

# %%
TIPOS_PERGUNTA = [
    "consumo_geral",
    "picos_energia",
    "usuario_top",
    "recomendacao_cobranca",
    "previsao_uso",
    "desempenho_carregadores",
    "analise_financeira",
    "goodwe",
    "normal",
    "fora_de_escopo",
]

SYSTEM_ORQUESTRADOR = f"""
Você é um classificador de intenções para um chatbot de gestão de eletropostos.
Dada a mensagem do usuário, retorne APENAS um JSON com a chave "tipo".

Tipos possíveis: {json.dumps(TIPOS_PERGUNTA)}

Exemplos:
- "Quanto consumi esse mês?"           → {{"tipo": "consumo_geral"}}
- "Tive pico essa semana?"             → {{"tipo": "picos_energia"}}
- "Quem mais usou energia?"            → {{"tipo": "usuario_top"}}
- "Qual modelo de cobrança é melhor?"  → {{"tipo": "recomendacao_cobranca"}}
- "Previsão de uso amanhã?"            → {{"tipo": "previsao_uso"}}
- "Qual carregador ficou ocioso?"      → {{"tipo": "desempenho_carregadores"}}
- "Quanto faturaria com R$1,80/kWh?"  → {{"tipo": "analise_financeira"}}
- "Do que se trata a GoodWe?"        → {{"tipo": "goodwe"}}
- "Olá, como vai?"                    → {{"tipo": "normal"}}
- "Como está o tempo?"                 → {{"tipo": "fora_de_escopo"}}

Retorne APENAS o JSON, sem texto adicional.
""".strip()

SYSTEM_AGENTE_PRINCIPAL = """
Você é o assistente de gestão do ChargeGrid Intelligence, plataforma de eletropostos comerciais da GoodWe × FIAP.

OBJETIVO
Ajudar operadores comerciais de eletropostos com respostas rápidas, claras e práticas sobre consumo, faturamento, uso, desempenho e previsão de demanda.

PÚBLICO
Os usuários não são técnicos. Use linguagem simples, direta e objetiva.

REGRAS PRINCIPAIS
- Responda sempre em português brasileiro.
- Use apenas os dados fornecidos no contexto.
- Não memorize dados entre chamadas.
- Nunca invente métricas, valores ou tendências.
- Se faltarem dados, informe claramente.

ESCOPO
Você pode responder sobre:
- Consumo geral e por carregador
- Picos de energia
- Usuários e sessões
- Cobrança inteligente
- Previsão de uso
- Desempenho dos carregadores
- Análise financeira
- GoodWe 


FORMATO DAS RESPOSTAS
1. Resposta direta primeiro
2. Dados ou breakdown quando necessário
3. Insight ou recomendação adicional se pertinente
4. Sem respostas vagas ou genéricas
5. Respostas sempre dentro do necessario, sem exagerar ou fornecer informações além do necessário

PADRÕES
- Consumo: total → carregadores → anomalias
- Picos: horário → valor → comparação com limite
- Usuários: consumo → sessões → média
- Cobrança: modelo recomendado → motivo
- Previsão: pico esperado → consumo estimado
- Financeiro: valor → premissas → cenários

CONTEXTO TÉCNICO
Os eletropostos utilizam controle de demanda, OCPP, MODBUS, cobrança por kWh/tempo/sessão e IA para previsão e otimização energética.

FORA DO ESCOPO
Informe educadamente que você é especializado em gestão de eletropostos e sugira perguntas relacionadas ao tema.

""".strip()


# %% [markdown]
# ## Agente Orquestrador

# %%
def orquestrador(pergunta: str) -> str:
    """Classifica a pergunta e retorna o tipo."""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_ORQUESTRADOR},
            {"role": "user",   "content": pergunta},
        ],
        temperature=0.3,
        max_tokens=50,
    )
    raw = resp.choices[0].message.content.strip()
    try:
        return json.loads(raw).get("tipo", "fora_de_escopo")
    except json.JSONDecodeError:
        return "fora_de_escopo"


def buscar_dados(tipo: str, df_users, df_chargers, df_sessions, df_energy) -> str | None:
    """Retorna o conteúdo bruto do DataFrame relevante como string."""
    if tipo == "consumo_geral":
        return get_dados_consumo(df_sessions, df_chargers)
    elif tipo == "picos_energia":
        return get_dados_picos(df_energy)
    elif tipo == "usuario_top":
        return get_dados_usuarios(df_sessions, df_users)
    elif tipo == "recomendacao_cobranca":
        return get_dados_cobranca(df_sessions)
    elif tipo == "previsao_uso":
        return get_dados_previsao(df_sessions)
    elif tipo == "desempenho_carregadores":
        return get_dados_desempenho(df_sessions, df_chargers)
    elif tipo == "analise_financeira":
        return get_dados_financeiro(df_sessions)
    elif tipo == "goodwe":
        return "Informações sobre a GoodWe: A GoodWe é uma empresa líder em soluções de energia renovável, especializada em inversores solares, sistemas de armazenamento de energia e soluções de carregamento para veículos elétricos. Fundada em 2010, a empresa tem se destacado por sua inovação tecnológica, qualidade de produtos e compromisso com a sustentabilidade. A GoodWe oferece uma ampla gama de produtos para residências, empresas e projetos de grande escala, contribuindo para a transição global para fontes de energia mais limpas e eficientes."
    elif tipo == "normal":
        return "Resposta breve e voltando ao foco principal sobre gestão de eletropostos"
    else:
        return None  # fora de escopo

# %% [markdown]
# ## Agente Principal

# %%
def agente_principal(pergunta: str, dados: str | None, historico: list[dict]) -> str:
    """Gera resposta em linguagem natural com base nos dados brutos injetados."""
    if dados is None:
        return (
            "Sou especializado em gestão de eletropostos e não consigo ajudar com esse tema.\n\n"
            "Posso te ajudar com:\n"
            "• Consumo por carregador\n"
            "• Picos de energia desta semana\n"
            "• Faturamento estimado por tarifa\n"
            "• Previsão de uso para amanhã\n"
            "• Desempenho dos seus carregadores\n\n"
            "Qual dessas você quer ver?"
        )

    mensagens = [{"role": "system", "content": SYSTEM_AGENTE_PRINCIPAL}]
    mensagens.extend(historico)
    mensagens.append({
        "role": "user",
        "content": (
            f"Pergunta do operador: {pergunta}\n\n"
            f"Dados do eletroposto:\n{dados}"
        ),
    })

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensagens,
        temperature=0.4,
        max_tokens=600,
    )
    return resp.choices[0].message.content.strip()




## Como não temoms o sistema de previsão feito, a espectativa é que a ultima pergunta seja respondida que não é possível ser realizada a previsão

# %%
PERGUNTAS_TESTE = [
    "Quanto de energia consumi esse mês no total e por carregador?",
    "Tive algum pico de energia essa semana?",
    "Qual foi a pessoa que mais consumiu energia este mês?",
    "Baseado no meu histórico, qual modelo de cobrança seria mais vantajoso para mim?",
    "Qual é a previsão de uso para amanhã?",
]


def run_tests():
    print("=" * 70)
    print("  MODELO DE TESTE — ChargeGrid Intelligence · Sprint 2")
    print("=" * 70)

    for i, pergunta in enumerate(PERGUNTAS_TESTE, start=1):
        print(f"\n{'─'*70}")
        print(f"  TESTE {i}")
        print(f"  Pergunta: {pergunta}")
        print(f"{'─'*70}")

        classificacao = orquestrador(pergunta)
        print(f"  [Orquestrador] Tipo identificado: {classificacao}")

        dados_json = buscar_dados(classificacao, df_users, df_chargers, df_sessions, df_energy_hourly)
        resposta = agente_principal(pergunta, dados_json, [])

        print(f"\n  Resposta:\n")
        for linha in resposta.split("\n"):
            print(f"    {linha}")

    print(f"\n{'='*70}")
    print("  Testes concluídos.")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()

# %%



