# archivo: app/absorcion/generar_schema_orderbook.py

import ccxt
import json
from pathlib import Path

# === Configuración ===
EXCHANGE_ID = 'binance'   # Cambiá por 'bybit', 'kraken', etc.
SYMBOL = 'BTC/USDT'
LIMIT = 20

# === Inicializar exchange ===
exchange_class = getattr(ccxt, EXCHANGE_ID)
exchange = exchange_class({'enableRateLimit': True})

# === Obtener orderbook real ===
orderbook = exchange.fetch_order_book(SYMBOL, limit=LIMIT)

# === Inferir estructura ===
def infer_schema(obj):
    """Recorre la estructura y devuelve tipos sin valores."""
    if isinstance(obj, dict):
        return {k: infer_schema(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        if not obj:
            return "list[?]"
        return [infer_schema(obj[0])]
    else:
        return type(obj).__name__

schema_structure = {
    "exchange": EXCHANGE_ID,
    "symbol": SYMBOL,
    "limit": LIMIT,
    "schema_inferido": infer_schema(orderbook)
}

# === Guardar plantilla ===
BASE_DIR = Path(__file__).resolve().parent  # app/absorcion
DATOS_DIR = BASE_DIR / "datos"
DATOS_DIR.mkdir(parents=True, exist_ok=True)

schema_file = DATOS_DIR / f"plantilla_schema_orderbook_{EXCHANGE_ID}_{SYMBOL.replace('/', '-')}.json"

with open(schema_file, "w", encoding="utf-8") as f:
    json.dump(schema_structure, f, indent=4, ensure_ascii=False)

print(f"✅ Plantilla real del schema guardada en: {schema_file}")
