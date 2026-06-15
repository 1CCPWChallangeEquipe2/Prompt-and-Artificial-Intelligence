import pandas as pd
import numpy as np

from datetime import datetime, timedelta


# ─────────────────────────────────────────────
# GERAÇÃO DOS CSVs MOCKADOS
# ─────────────────────────────────────────────

def generate_mock_csvs(
    dias=5,
    sessoes_min=1,
    sessoes_max=3
):
    """
    Gera arquivos CSV simulando um sistema de eletroposto
    com baixo volume de dados para testes rápidos.

    CSVs gerados:
    - users.csv
    - chargers.csv
    - sessions.csv
    - energy_hourly.csv

    Retorna:
        dict com os caminhos dos arquivos gerados
    """

    np.random.seed(42)

    hoje = datetime(2026, 6, 14)

    # ─────────────────────────────────────────
    # USERS
    # ─────────────────────────────────────────

    df_users = pd.DataFrame({
        "user_id": [
            "USR-0001",
            "USR-0023",
            "USR-0047",
            "USR-0088",
            "USR-0102"
        ],

        "user_name": [
            "Carlos Souza",
            "Ana Lima",
            "Inaldo Freitas",
            "Beatriz Costa",
            "Pedro Alves"
        ],

        "user_type": [
            "app_driver",
            "corporate",
            "app_driver",
            "casual",
            "corporate"
        ],

        "company": [
            None,
            "TechCorp",
            None,
            None,
            "LogiStar"
        ],

        "vehicle_model": [
            "BYD Seal",
            "Volvo XC40 Recharge",
            "Fiat 500e",
            "Renault Kwid E",
            "Chevrolet Bolt"
        ],

        "profile_cluster": [
            "app",
            "frotista",
            "app",
            "esporadico",
            "frotista"
        ],

        "created_at": [
            "2025-01-10",
            "2025-03-22",
            "2025-02-05",
            "2026-01-18",
            "2025-11-30"
        ]
    })

    # ─────────────────────────────────────────
    # CHARGERS
    # ─────────────────────────────────────────

    df_chargers = pd.DataFrame({
        "charger_id": [
            "CHR-01",
            "CHR-02",
            "CHR-03"
        ],

        "charger_name": [
            "Carregador #1",
            "Carregador #2",
            "Carregador #3"
        ],

        "site_id": [
            "SITE-SP-01",
            "SITE-SP-01",
            "SITE-SP-01"
        ],

        "power_kw": [
            22,
            22,
            11
        ],

        "connector_type": [
            "CCS2",
            "CCS2",
            "Type2"
        ],

        "status": [
            "online",
            "online",
            "online"
        ],

        "installation_date": [
            "2024-06-01",
            "2024-06-01",
            "2024-09-15"
        ]
    })

    # ─────────────────────────────────────────
    # SESSIONS (BAIXO VOLUME)
    # ─────────────────────────────────────────

    session_rows = []

    session_id = 1

    for day_offset in range(dias):

        data = hoje - timedelta(days=day_offset)

        # poucas sessões por dia
        for _ in range(
            np.random.randint(
                sessoes_min,
                sessoes_max + 1
            )
        ):

            user = np.random.choice(
                df_users["user_id"].tolist()
            )

            charger = np.random.choice(
                ["CHR-01", "CHR-02", "CHR-03"]
            )

            hora = np.random.randint(8, 20)

            inicio = data.replace(
                hour=hora,
                minute=np.random.randint(0, 60)
            )

            dur = np.random.randint(20, 60)

            fim = inicio + timedelta(
                minutes=int(dur)
            )

            energia = round(
                np.random.uniform(3, 12),
                2
            )

            preco = round(
                np.random.uniform(1.80, 2.00),
                2
            )

            session_rows.append({

                "session_id":
                    f"SES-{session_id:04d}",

                "user_id":
                    user,

                "charger_id":
                    charger,

                "start_ts":
                    inicio,

                "end_ts":
                    fim,

                "duration_min":
                    dur,

                "energy_kwh":
                    energia,

                "avg_power_kw":
                    round(
                        energia / (dur / 60),
                        2
                    ),

                "pricing_model":
                    "kwh",

                "price_per_kwh":
                    preco,

                "session_cost_brl":
                    round(
                        energia * preco,
                        2
                    ),

                "payment_method":
                    np.random.choice(
                        ["pix", "card"]
                    ),

                "session_status":
                    "completed",
            })

            session_id += 1

    df_sessions = pd.DataFrame(session_rows)

    # ─────────────────────────────────────────
    # ENERGY HOURLY (MENOR VOLUME)
    # ─────────────────────────────────────────

    energy_rows = []

    # apenas 2 dias
    for day_offset in range(2):

        data = hoje - timedelta(days=day_offset)

        for hora in range(24):

            active = (
                np.random.randint(0, 3)
                if 8 <= hora <= 20
                else 0
            )

            solar = round(
                np.random.uniform(0, 10),
                2
            ) if 8 <= hora <= 17 else 0

            load = round(
                active * np.random.uniform(5, 15)
                + np.random.uniform(1, 3),
                2
            )

            energy_rows.append({

                "timestamp":
                    data.replace(
                        hour=hora,
                        minute=0
                    ),

                "site_id":
                    "SITE-SP-01",

                "site_load_kw":
                    load,

                "solar_generation_kw":
                    solar,

                "battery_level_percent":
                    np.random.randint(30, 90),

                "battery_flow_kw":
                    round(
                        np.random.uniform(-3, 3),
                        2
                    ),

                "grid_import_kw":
                    round(
                        max(0, load - solar),
                        2
                    ),

                "active_chargers":
                    active,

                "peak_limit_kw":
                    60.0,

                "peak_flag":
                    load > 60.0,
            })

    df_energy_hourly = pd.DataFrame(
        energy_rows
    )

    # ─────────────────────────────────────────
    # EXPORTAÇÃO DOS CSVs
    # ─────────────────────────────────────────

    users_csv = "..\\dados\\users.csv"
    chargers_csv = "..\\dados\\chargers.csv"
    sessions_csv = "..\\dados\\sessions.csv"
    energy_csv = "..\\dados\\energy_hourly.csv"

    df_users.to_csv(users_csv, index=False)
    df_chargers.to_csv(chargers_csv, index=False)
    df_sessions.to_csv(sessions_csv, index=False)
    df_energy_hourly.to_csv(energy_csv, index=False)

    # ─────────────────────────────────────────
    # LOG
    # ─────────────────────────────────────────

    print("CSV gerados com sucesso:")
    print(f"Users: {len(df_users)}")
    print(f"Chargers: {len(df_chargers)}")
    print(f"Sessions: {len(df_sessions)}")
    print(f"Energy rows: {len(df_energy_hourly)}")

    # ─────────────────────────────────────────
    # RETORNO
    # ─────────────────────────────────────────

    return {
        "users_csv": users_csv,
        "chargers_csv": chargers_csv,
        "sessions_csv": sessions_csv,
        "energy_hourly_csv": energy_csv
    }



generate_mock_csvs()