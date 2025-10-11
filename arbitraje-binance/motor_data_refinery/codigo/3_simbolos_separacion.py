"""
Separa símbolos del archivo funcional en:
- cotizador_directo   (quote == USDT)
- cotizador_invertido (base  == USDT)
- cotizador_indirecto (ninguno == USDT)

Entrada:
    - Lee simbolos_spot_<exchange>.csv desde codigo/datos/estandar/
    - El activo de referencia (INTERESADO_EN) se define en el código.
Salida:
    - CSVs en codigo/datos/tratamiento_de_cotizacion/
      (solo columnas symbol, base, quote)
"""

import sys
from pathlib import Path
import pandas as pd

# --- Configuración de rutas ---
APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from codigo.config import EXCHANGE_ID, DATOS_DIR

# --- Parámetros configurables ---
INTERESADO_EN = "USDT"  # 💡 podés cambiarlo a BUSD, EUR, ARS, etc.

INPUT_PATH = DATOS_DIR / "estandar" / f"simbolos_spot_{EXCHANGE_ID}.csv"
OUTPUT_DIR = DATOS_DIR / "tratamiento_de_cotizacion"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    if not INPUT_PATH.exists():
        print(f"❌ No se encontró el archivo de entrada: {INPUT_PATH}")
        sys.exit(1)

    # Cargar la tabla funcional
    df = pd.read_csv(INPUT_PATH, dtype=str)
    if df.empty:
        print("⚠️ El archivo está vacío.")
        sys.exit(0)

    # Normalizar texto
    for col in ("symbol", "base", "quote"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    # ✅ Mantener solo columnas esenciales
    columnas_relevantes = [c for c in ("symbol", "base", "quote") if c in df.columns]
    df = df[columnas_relevantes]

    # Separar según el activo de referencia
    directo   = df[df["quote"] == INTERESADO_EN]
    invertido = df[df["base"]  == INTERESADO_EN]
    indirecto = df[(df["base"] != INTERESADO_EN) & (df["quote"] != INTERESADO_EN)]

    # Exportar CSVs (solo symbol, base, quote)
    out_directo   = OUTPUT_DIR / f"cotizador_directo_{INTERESADO_EN}.csv"
    out_invertido = OUTPUT_DIR / f"cotizador_invertido_{INTERESADO_EN}.csv"
    out_indirecto = OUTPUT_DIR / f"cotizador_indirecto_{INTERESADO_EN}.csv"

    directo.to_csv(out_directo, index=False)
    invertido.to_csv(out_invertido, index=False)
    indirecto.to_csv(out_indirecto, index=False)

    print(f"✅ Exportados en {OUTPUT_DIR}")
    print(f"✔ cotizador_directo_{INTERESADO_EN}.csv:   {len(directo)} símbolos")
    print(f"✔ cotizador_invertido_{INTERESADO_EN}.csv: {len(invertido)} símbolos")
    print(f"✔ cotizador_indirecto_{INTERESADO_EN}.csv: {len(indirecto)} símbolos")


if __name__ == "__main__":
    main()
