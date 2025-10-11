# -*- coding: utf-8 -*-
"""
📤 Exportador del Cotizador Universal Unificado

Copia el archivo generado en:
    codigo/datos/tratamiento_de_cotizacion/cotizador_universal_unificado.csv

Hacia:
    app/absorcion/datos/cotizador_universal_unificado.csv

💡 Esta etapa representa la 'fase de absorción de datos' lista para ser consumida
por motores de arbitraje o análisis externo.
"""

import sys
from pathlib import Path
import shutil
import pandas as pd
from datetime import datetime

# --- Configuración de rutas ---
APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from codigo.config import DATOS_DIR  # type: ignore

# Origen y destino
SRC_FILE = DATOS_DIR / "tratamiento_de_cotizacion" / "cotizador_universal_unificado.csv"
DEST_DIR = APP_DIR / "absorcion" / "datos"
DEST_FILE = DEST_DIR / "cotizador_universal_unificado.csv"


def main():
    if not SRC_FILE.exists():
        print(f"❌ No se encontró el archivo fuente: {SRC_FILE}")
        sys.exit(1)

    DEST_DIR.mkdir(parents=True, exist_ok=True)

    # Leer y copiar archivo
    df = pd.read_csv(SRC_FILE, dtype=str)
    shutil.copy2(SRC_FILE, DEST_FILE)

    print("\n📤 Exportación completada")
    print(f"📦 Origen : {SRC_FILE}")
    print(f"📥 Destino: {DEST_FILE}")
    print(f"📊 Registros exportados: {len(df)}")
    print(f"🕒 Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Verificación rápida del contenido
    print("\n🔹 Columnas detectadas:")
    print(", ".join(df.columns.tolist()))

    print("\n✅ Cotizador universal disponible para absorción de datos.")


if __name__ == "__main__":
    main()
