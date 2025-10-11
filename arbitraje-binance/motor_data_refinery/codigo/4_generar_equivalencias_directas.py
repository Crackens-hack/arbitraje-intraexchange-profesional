"""
Genera equivalencias directas entre BASE y USDT usando los símbolos directos ya filtrados.

Entrada:
    - codigo/datos/tratamiento_de_cotizacion/directo_USDT.csv

Salida:
    - codigo/datos/tratamiento_de_cotizacion/1_usdt_equivale.csv
    - codigo/datos/tratamiento_de_cotizacion/1_base_equivale_tantos_usdt.csv

Ejemplo:
    base,1_usdt_equivale_base
    BTC,0.0000147
    ETH,0.0002941
    ...
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

INTERESADO_EN = "USDT"  # 💡 Podés cambiarlo si querés (BUSD, EUR, etc.)

INPUT_PATH = DATOS_DIR / "tratamiento_de_cotizacion" / f"directo_{INTERESADO_EN}.csv"
OUTPUT_DIR = DATOS_DIR / "tratamiento_de_cotizacion"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_USDT_EQUIVALE = OUTPUT_DIR / "1_usdt_equivale.csv"
OUTPUT_BASE_EQUIVALE = OUTPUT_DIR / "1_base_equivale_tantos_usdt.csv"


def main():
    if not INPUT_PATH.exists():
        print(f"❌ No se encontró el archivo de entrada: {INPUT_PATH}")
        sys.exit(1)

    df = pd.read_csv(INPUT_PATH, dtype=str)
    if df.empty:
        print("⚠️ El archivo está vacío.")
        sys.exit(0)

    # Normalizar columnas
    for col in ("symbol", "base", "quote"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    # --- Conexión CCXT ---
    ex_class = getattr(ccxt, EXCHANGE_ID)
    exchange = ex_class(CCXT_OPTIONS)
    exchange.load_markets()

    # --- Obtener todos los tickers de una sola vez ---
    tickers = exchange.fetch_tickers()

    rows_base_a_usdt = []
    rows_usdt_a_base = []

    for _, row in df.iterrows():
        symbol = row.get("symbol")
        base = row.get("base")
        if not symbol or not base:
            continue

        t = tickers.get(symbol)
        if not t:
            print(f"⚠️ No se encontró ticker para {symbol}")
            continue

        last = t.get("last") or t.get("close") or t.get("info", {}).get("lastPrice")
        if not last:
            print(f"⚠️ Sin precio para {symbol}")
            continue

        precio = Decimal(str(last))
        if precio <= 0:
            continue

        # 1 base = X usdt
        rows_base_a_usdt.append({"base": base, "1_base_equivale_usdt": f"{precio:.10f}"})

        # 1 usdt = X base
        rows_usdt_a_base.append({"base": base, "1_usdt_equivale_base": f"{(Decimal('1') / precio):.18f}"})

    # --- Guardar resultados ---
    pd.DataFrame(rows_usdt_a_base).to_csv(OUTPUT_USDT_EQUIVALE, index=False)
    pd.DataFrame(rows_base_a_usdt).to_csv(OUTPUT_BASE_EQUIVALE, index=False)

    print(f"✅ Generado {OUTPUT_USDT_EQUIVALE}")
    print(f"✅ Generado {OUTPUT_BASE_EQUIVALE}")
    print(f"✔️ Total de pares procesados: {len(rows_usdt_a_base)}")


if __name__ == "__main__":
    main()
