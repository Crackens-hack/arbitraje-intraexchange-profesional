# codigo/5_generar_equivalencias_indirectas.py
"""
Genera equivalencias indirectas entre BASE y USDT
usando los símbolos sin USDT (indirectos) y las equivalencias ya calculadas.

Entrada:
    - codigo/datos/tratamiento_de_cotizacion/indirecto_USDT.csv
    - codigo/datos/tratamiento_de_cotizacion/1_usdt_equivale.csv

Lógica:
    - Si la quote del par existe en 1_usdt_equivale.csv → el par es ruteable
    - Se obtiene su precio desde CCXT y se calcula:
        1_usdt_equivale_quote  (desde CSV)
        1_usdt_equivale_base   = 1_usdt_equivale_quote / precio_par

Salida:
    - codigo/datos/tratamiento_de_cotizacion/1_usdt_equivale_indirectos.csv
    - codigo/datos/tratamiento_de_cotizacion/no_ruteables_indirectos.csv
    - resumen de coherencia (% de pares ruteables)
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
INPUT_INDIRECTO = BASE_PATH / f"indirecto_{INTERESADO_EN}.csv"
INPUT_EQUIV = BASE_PATH / "1_usdt_equivale.csv"
OUTPUT_RUTEABLES = BASE_PATH / "1_usdt_equivale_indirectos.csv"
OUTPUT_NO_RUTEABLES = BASE_PATH / "no_ruteables_indirectos.csv"


def main():
    if not INPUT_INDIRECTO.exists():
        print(f"❌ No se encontró el archivo de indirectos: {INPUT_INDIRECTO}")
        sys.exit(1)
    if not INPUT_EQUIV.exists():
        print(f"❌ No se encontró el archivo de equivalencias: {INPUT_EQUIV}")
        sys.exit(1)

    df_indir = pd.read_csv(INPUT_INDIRECTO, dtype=str)
    df_eq = pd.read_csv(INPUT_EQUIV, dtype=str)

    if df_indir.empty:
        print("⚠️ No hay pares indirectos para procesar.")
        sys.exit(0)
    if df_eq.empty:
        print("⚠️ No hay equivalencias de USDT disponibles.")
        sys.exit(0)

    # Normalizar texto y nombres de columnas
    df_indir.columns = [c.strip().lower() for c in df_indir.columns]
    df_eq.columns = [c.strip().lower() for c in df_eq.columns]

    for df in (df_indir, df_eq):
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    # Detectar nombre real de la columna de equivalencias
    col_equiv = next((c for c in df_eq.columns if "1_usdt_equivale_base" in c.lower()), None)
    if not col_equiv:
        raise KeyError("❌ No se encontró la columna '1_usdt_equivale_base' en el CSV de equivalencias.")

    eq_map = dict(zip(df_eq["base"], df_eq[col_equiv]))

    # Conexión CCXT
    ex_class = getattr(ccxt, EXCHANGE_ID)
    exchange = ex_class(CCXT_OPTIONS)
    exchange.load_markets()
    tickers = exchange.fetch_tickers()

    ruteables, no_ruteables = [], []

    for _, row in df_indir.iterrows():
        symbol = row.get("symbol")
        base = row.get("base")
        quote = row.get("quote")
        if not symbol or not base or not quote:
            continue

        if quote not in eq_map:
            no_ruteables.append(row)
            continue

        ticker = tickers.get(symbol)
        if not ticker:
            no_ruteables.append(row)
            continue

        last = ticker.get("last") or ticker.get("close") or ticker.get("info", {}).get("lastPrice")
        if not last:
            no_ruteables.append(row)
            continue

        try:
            precio = Decimal(str(last))
            if precio <= 0:
                continue

            usdt_vs_quote = Decimal(str(eq_map[quote]))
            usdt_vs_base = usdt_vs_quote / precio

            ruteables.append({
                "symbol": symbol,
                "base": base,
                "quote": quote,
                "1_usdt_equivale_quote": f"{usdt_vs_quote:.18f}",
                "1_usdt_equivale_base": f"{usdt_vs_base:.18f}",
                "precio_base_vs_quote": f"{precio:.10f}"
            })
        except Exception as e:
            print(f"⚠️ Error en {symbol}: {e}")
            no_ruteables.append(row)

    # Guardar resultados
    pd.DataFrame(ruteables).to_csv(OUTPUT_RUTEABLES, index=False)
    pd.DataFrame(no_ruteables).to_csv(OUTPUT_NO_RUTEABLES, index=False)

    total = len(df_indir)
    tot_rut = len(ruteables)
    tot_no = len(no_ruteables)
    ratio = (tot_rut / total * 100) if total else 0

    print("\n📊 --- Resumen de coherencia ---")
    print(f"🔹 Total de pares indirectos: {total}")
    print(f"🔹 Ruteables: {tot_rut}")
    print(f"🔹 No ruteables: {tot_no}")
    print(f"✅ Cobertura de rutas: {ratio:.2f}%")
    if ratio < 50:
        print("⚠️ Advertencia: baja cobertura. Revisa equivalencias directas o liquidez del exchange.")
    else:
        print("👌 Cobertura aceptable para simulaciones.")

    print(f"\n📄 Archivos generados:")
    print(f"   - {OUTPUT_RUTEABLES}")
    print(f"   - {OUTPUT_NO_RUTEABLES}")


if __name__ == "__main__":
    main()
