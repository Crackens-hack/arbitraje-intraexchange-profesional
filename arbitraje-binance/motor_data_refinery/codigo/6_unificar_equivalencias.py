# -*- coding: utf-8 -*-
"""
💠 COTIZADOR UNIVERSAL UNIFICADO 💠
Unifica las cotizaciones directas (precio real CCXT) e indirectas (derivadas)
en un solo archivo maestro.

Entradas:
  - codigo/datos/tratamiento_de_cotizacion/1_usdt_equivale_indirectos.csv
  - codigo/datos/tratamiento_de_cotizacion/directo_USDT.csv

Salida:
  - codigo/datos/tratamiento_de_cotizacion/cotizador_universal_unificado.csv

Columnas finales:
  symbol | base | quote | 1_usdt_equivale_base | cotizacion_indirecta | fuente
"""

import sys
from pathlib import Path
import pandas as pd
import ccxt
from decimal import Decimal, getcontext

# --- Precisión alta ---
getcontext().prec = 50

# --- Configuración base ---
APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))
from codigo.config import EXCHANGE_ID, CCXT_OPTIONS, DATOS_DIR  # type: ignore

INTERESADO_EN = "USDT"
BASE_PATH = DATOS_DIR / "tratamiento_de_cotizacion"

INPUT_DIRECTO = BASE_PATH / f"directo_{INTERESADO_EN}.csv"
INPUT_INDIRECTO_EQUIV = BASE_PATH / "1_usdt_equivale_indirectos.csv"
OUTPUT_UNIFICADO = BASE_PATH / "cotizador_universal_unificado.csv"


def cargar_df(path: Path) -> pd.DataFrame:
    """Carga CSV si existe, normalizando columnas clave."""
    if not path.exists():
        print(f"⚠️ No se encontró {path.name}")
        return pd.DataFrame()
    df = pd.read_csv(path, dtype=str)
    for col in ("symbol", "base", "quote"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
    return df


def main():
    df_dir = cargar_df(INPUT_DIRECTO)
    df_ind = cargar_df(INPUT_INDIRECTO_EQUIV)

    if df_dir.empty and df_ind.empty:
        print("❌ No hay datos directos ni indirectos para unificar.")
        sys.exit(1)

    # --- Conexión CCXT ---
    ex_class = getattr(ccxt, EXCHANGE_ID)
    exchange = ex_class(CCXT_OPTIONS)
    exchange.load_markets()
    tickers = exchange.fetch_tickers()

    rows = []

    # --- 1️⃣ Procesar directos (precio real CCXT) ---
    for _, row in df_dir.iterrows():
        symbol, base, quote = row.get("symbol"), row.get("base"), row.get("quote")
        if not symbol or not base or quote != INTERESADO_EN:
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

        rows.append({
            "symbol": symbol,
            "base": base,
            "quote": quote,
            "1_usdt_equivale_base": f"{(Decimal('1') / precio):.18f}",
            "cotizacion_indirecta": False,
            "fuente": "CCXT directo"
        })

    # --- 2️⃣ Procesar indirectos (ya derivados) ---
    if not df_ind.empty:
        col_equiv = next((c for c in df_ind.columns if "1_usdt_equivale_base" in c.lower()), None)
        if not col_equiv:
            raise KeyError("❌ No se encontró la columna 1_usdt_equivale_base en los indirectos")

        for _, row in df_ind.iterrows():
            symbol, base, quote = row.get("symbol"), row.get("base"), row.get("quote")
            val = row.get(col_equiv)
            if not symbol or not base or not val:
                continue

            rows.append({
                "symbol": symbol,
                "base": base,
                "quote": quote,
                "1_usdt_equivale_base": str(val),
                "cotizacion_indirecta": True,
                "fuente": "Indirecto derivado"
            })

    # --- 3️⃣ Unificar y guardar ---
    df_out = pd.DataFrame(rows)
    df_out.drop_duplicates(subset=["symbol"], inplace=True)
    df_out.to_csv(OUTPUT_UNIFICADO, index=False)

    # --- 4️⃣ Reporte final ---
    n_total = len(df_out)
    n_ind = len(df_out[df_out["cotizacion_indirecta"] == True])
    n_dir = n_total - n_ind
    print(f"\n💠 Cotizador universal unificado generado exitosamente 💠")
    print(f"📄 Archivo: {OUTPUT_UNIFICADO}")
    print(f"🔹 Directos CCXT : {n_dir}")
    print(f"🔹 Indirectos     : {n_ind}")
    print(f"🔸 Total tokens   : {n_total}\n")


if __name__ == "__main__":
    main()
# --- Fin del código ---