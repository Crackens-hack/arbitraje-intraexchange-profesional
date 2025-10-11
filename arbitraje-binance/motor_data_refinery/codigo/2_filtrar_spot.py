"""
Filtra la tabla estandarizada (symbols_estandar_<exchange>.csv)
usando criterios declarativos (criterios_filtrados.csv)
y la lista fiat_tokens de fiat.py para descartar pares fiat.

Genera:
  - simbolos_spot_<exchange>.csv  (limpio, sin claves de filtro)
  - descartados_spot_<exchange>.csv (con motivo y claves de control)
"""

import sys
from pathlib import Path
import pandas as pd

# ─────────── Paths y configuración ───────────
APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from codigo.config import EXCHANGE_ID, DATOS_DIR
from codigo.static.fiat import fiat_tokens   # ✅ lista global de fiat
# (fiat.py debe estar en codigo/static/fiat.py)

# Rutas de entrada/salida
CRITERIOS_PATH = APP_DIR / "codigo" / "static" / "criterios_filtrados.csv"
INPUT_PATH = DATOS_DIR / "estandar" / f"symbols_estandar_{EXCHANGE_ID}.csv"
OUTPUT_DIR = DATOS_DIR / "estandar"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─────────── Helpers ───────────
def _norm(v: str) -> str:
    """Normaliza valores para comparar (True→1, False→0, strings→upper)."""
    v = str(v).strip().lower()
    if v in {"true", "1", "yes"}:
        return "1"
    if v in {"false", "0", "no"}:
        return "0"
    return v.upper()

def cargar_criterios() -> dict[str, set[str]]:
    """Lee criterios_filtrados.csv y devuelve dict campo→valores_permitidos."""
    if not CRITERIOS_PATH.exists():
        print(f"❌ No existe el archivo de criterios: {CRITERIOS_PATH}")
        sys.exit(1)

    df = pd.read_csv(CRITERIOS_PATH, dtype=str)
    criterios = {}
    for _, row in df.iterrows():
        campo = str(row["campo"]).strip()
        valores = str(row["permitidos"]).strip()
        if campo.startswith("__"):  # ignorar __OUTPUT__ u otros meta
            continue
        if valores:
            criterios[campo] = {_norm(v) for v in valores.split(";")}
    return criterios

def aplicar_criterios(df: pd.DataFrame, criterios: dict[str, set[str]]):
    """Aplica los criterios sobre el DataFrame estandar y devuelve (funcional, descartados)."""
    funcional, descartados = [], []
    fiat_upper = {f.upper() for f in fiat_tokens}

    for _, row in df.iterrows():
        valido = True
        motivo = []

        for campo, permitidos in criterios.items():
            if campo not in df.columns:
                continue

            valor = _norm(row[campo])

            # 🚫 Si el campo tiene NOT_FIAT y su valor está en fiat_tokens
            if "NOT_FIAT" in permitidos and valor in fiat_upper:
                valido = False
                motivo.append(f"{campo}=FIAT")

            # 🧩 Si no cumple con los valores permitidos
            elif valor not in permitidos and "NOT_FIAT" not in permitidos:
                valido = False
                motivo.append(f"{campo}='{valor}' no permitido")

        if valido:
            funcional.append(row)
        else:
            r = row.copy()
            r["motivo_descartado"] = "; ".join(motivo)
            descartados.append(r)

    return pd.DataFrame(funcional), pd.DataFrame(descartados)

# ─────────── Main ───────────
def main():
    if not INPUT_PATH.exists():
        print(f"❌ No existe el CSV de entrada: {INPUT_PATH}")
        sys.exit(1)

    df = pd.read_csv(INPUT_PATH, dtype=str)
    criterios = cargar_criterios()

    df_funcional, df_descartados = aplicar_criterios(df, criterios)

    # Quitamos las columnas de control (presentes en criterios)
    campos_a_excluir = set(criterios.keys())
    df_funcional = df_funcional.drop(columns=[c for c in campos_a_excluir if c in df_funcional.columns])

    out_func = OUTPUT_DIR / f"simbolos_spot_{EXCHANGE_ID}.csv"
    out_desc = OUTPUT_DIR / f"descartados_spot_{EXCHANGE_ID}.csv"

    df_funcional.to_csv(out_func, index=False)
    df_descartados.to_csv(out_desc, index=False)

    print(f"✅ {len(df_funcional)} funcionales guardados en {out_func}")
    print(f"📄 {len(df_descartados)} descartados guardados en {out_desc}")

if __name__ == "__main__":
    main()
