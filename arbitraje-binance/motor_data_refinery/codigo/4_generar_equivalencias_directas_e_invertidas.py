"""
Genera equivalencias directas e invertidas entre BASE y USDT usando los símbolos filtrados.

Entrada:
    - codigo/datos/tratamiento_de_cotizacion/directo_USDT.csv
    - codigo/datos/tratamiento_de_cotizacion/invertido_USDT.csv

Salida:
    - codigo/datos/tratamiento_de_cotizacion/1_usdt_equivale.csv
    - codigo/datos/tratamiento_de_cotizacion/1_base_equivale_tantos_usdt.csv
"""

import sys
from pathlib import Path
import pandas as pd
import ccxt
from decimal import Decimal, getcontext

# --- Precisión alta ---
getcontext().prec = 50

# --- Configuración principal ---
APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from codigo.config import EXCHANGE_ID, CCXT_OPTIONS, DATOS_DIR  # type: ignore

INTERESADO_EN = "USDT"

BASE_PATH = DATOS_DIR / "tratamiento_de_cotizacion"
INPUT_DIRECTO = BASE_PATH / f"directo_{INTERESADO_EN}.csv"
INPUT_INVERTIDO = BASE_PATH / f"invertido_{INTERESADO_EN}.csv"

OUTPUT_USDT_EQUIVALE = BASE_PATH / "1_usdt_equivale.csv"
OUTPUT_BASE_EQUIVALE = BASE_PATH / "1_base_equivale_tantos_usdt.csv"


def cargar_df(path: Path) -> pd.DataFrame:
    if not path.exists():
        print(f"⚠️ No se encontró: {path}")
        return pd.DataFrame()
    df = pd.read_csv(path, dtype=str)
    for col in ("symbol", "base", "quote"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
    return df


def main():
    df_dir = cargar_df(INPUT_DIRECTO)
    df_inv = cargar_df(INPUT_INVERTIDO)

    if df_dir.empty and df_inv.empty:
        print("❌ No hay datos en directo ni invertido.")
        sys.exit(1)

    # --- Conexión CCXT ---
    ex_class = getattr(ccxt, EXCHANGE_ID)
    exchange = ex_class(CCXT_OPTIONS)
    exchange.load_markets()

    # Obtener tickers una sola vez
    tickers = exchange.fetch_tickers()

    rows_base_a_usdt = []  # 1 base = X usdt
    rows_usdt_a_base = []  # 1 usdt = X base

    # Procesar directos (base/USDT)
    for _, row in df_dir.iterrows():
        symbol, base = row.get("symbol"), row.get("base")
        if not symbol or not base:
            continue

        t = tickers.get(symbol)
        if not t:
            continue
        last = t.get("last") or t.get("close") or t.get("info", {}).get("lastPrice")
        if not last:
            continue
        precio = Decimal(str(last))
        if precio <= 0:
            continue

        rows_base_a_usdt.append({"base": base, "1_base_equivale_usdt": f"{precio:.10f}"})
        rows_usdt_a_base.append({"base": base, "1_usdt_equivale_base": f"{(Decimal('1') / precio):.18f}"})

    # Procesar invertidos (USDT/quote)
    for _, row in df_inv.iterrows():
        symbol, quote = row.get("symbol"), row.get("quote")
        if not symbol or not quote:
            continue

        t = tickers.get(symbol)
        if not t:
            continue
        last = t.get("last") or t.get("close") or t.get("info", {}).get("lastPrice")
        if not last:
            continue
        precio = Decimal(str(last))
        if precio <= 0:
            continue

        # En este caso el precio ya es "1 usdt = X quote"
        rows_usdt_a_base.append({"base": quote, "1_usdt_equivale_base": f"{precio:.18f}"})
        # Su inverso es "1 quote = X usdt"
        rows_base_a_usdt.append({"base": quote, "1_base_equivale_usdt": f"{(Decimal('1') / precio):.10f}"})

    # --- Guardar resultados ---
    pd.DataFrame(rows_usdt_a_base).to_csv(OUTPUT_USDT_EQUIVALE, index=False)
    pd.DataFrame(rows_base_a_usdt).to_csv(OUTPUT_BASE_EQUIVALE, index=False)

    print(f"✅ Generado {OUTPUT_USDT_EQUIVALE}")
    print(f"✅ Generado {OUTPUT_BASE_EQUIVALE}")
    print(f"✔️ Total directo+invertido: {len(rows_usdt_a_base)} equivalencias")


if __name__ == "__main__":
    main()
