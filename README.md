Perfecto 💪 — acá tenés el archivo **Markdown listo** para reemplazar directamente el original.
Podés copiarlo y guardarlo como:
📄 `arbitraje-binance/README.md`

---

````markdown
# Reform-Arbi — Motor de Arbitraje Triangular (Binance Lab)

## Resumen
- **Objetivo:** motor de arbitraje triangular intra-exchange (USDT → A → B → USDT; variantes con USDC) con ICI (Interés Compuesto Inmediato).  
  Cada ciclo reinvierte inmediatamente el resultado para lograr crecimiento exponencial (~1 % diario sostenido como meta).  
- **Tesis de Dominus:** el ICI maximiza rendimiento cuando se arriesga todo el capital, pero con control estricto y datos ultra precisos.  
  Por eso la arquitectura prioriza **datos limpios (refinería)** y **decisiones sub-milisegundo (realtime)**.  
- **Estado actual:** laboratorio en Binance (fase operativa base, modular y extensible a otros exchanges).

---

## Arquitectura (visión general)
- **Monorepo único** organizado por servicios independientes.  
- **Stack Binance (`arbitraje-binance/`):**
  - `motor_data_refinery`: ingesta, filtrado y estandarización de datos.
  - `motor_reactor_realtime`: decisión y ejecución de arbitrajes en tiempo real.
  - `motor_sentinel`: observabilidad, métricas y eventos.
  - `event_hub`: recolector de eventos y canal de notificación/control remoto.  
- **Diseño modular:** cada motor corre en su propio contenedor Docker, aislado del resto, comunicándose solo mediante red interna (`backbone`) y servicios compartidos (`mariadb`, `redis`).  

---

## Flujo de trabajo
1. **Refinería (`motor_data_refinery`)**
   - Limpia y unifica datos crudos desde APIs o CCXT.  
   - Calcula cotizaciones directas (USDT→X) e indirectas (USDT→A→B, A/B).  
   - Simula slippage multi-escenario, estima capacidad de absorción y genera triadas candidatas.  
   - Produce artefactos listos (CSV o tablas normalizadas) para consumo por el motor de realtime.  

2. **Realtime (`motor_reactor_realtime`)**
   - Evalúa triadas en tiempo real (< 3 ms por decisión).  
   - Calcula spread neto esperado (fees + slippage).  
   - Determina tamaño de orden (ICI) según riesgo y absorción.  
   - Ejecuta órdenes en el exchange y registra resultados.  

3. **Sentinel (`motor_sentinel`)**
   - Monitorea métricas, errores y señales.  
   - Envía eventos al `event_hub` vía WebSocket (`ws://event_hub:8080/ws`).  
   - Puede generar alertas o activar pausas automáticas ante condiciones anómalas.  

4. **Event Hub (`beacon_node` / `event_hub`)**
   - WebSocket server que agrega los eventos de los sentinels.  
   - Puede enviar notificaciones externas (por ejemplo Telegram) o aceptar comandos de control remoto (pausa, reconfiguración).  

---

## Arranque rápido (desarrollo local)
1. **Requisitos:** Docker + Docker Compose + archivo `.env` con credenciales y parámetros del stack.  
2. **Levantar servicios:**
   ```bash
   docker compose up -d
````

3. **Entrar a un motor:**

   ```bash
   docker compose exec motor_data_refinery bash
   docker compose exec motor_reactor_realtime bash
   docker compose exec motor_sentinel bash
   ```
4. **Logs y monitoreo:**
   Consultar en tiempo real los logs de cada motor o del hub con:

   ```bash
   docker logs -f <nombre_servicio>
   ```

---

## Estructura esencial del repositorio

```
arbitraje-binance/
├── docker-compose.yml          # Stack Binance (servicios y redes)
├── .env                        # Variables de entorno
├── motor_data_refinery/        # Procesamiento de datos
├── motor_reactor_realtime/     # Ejecución en tiempo real
├── motor_sentinel/             # Observabilidad y métricas
└── beacon_node/ (event_hub)    # Hub de eventos y notificaciones
```

---

## Privacidad y seguridad

* Todo el código y la configuración son **de uso privado y controlado**.
* Los contenedores están **aislados entre sí** y solo comparten servicios de datos internos.
* No hay dependencias externas (Codex, workspace global ni sistemas de sincronización automática).
* Se recomienda desplegar en un **VPS cercano a los servidores de Binance** para minimizar latencia.

---

## Siguientes pasos sugeridos

* Definir esquema final del artefacto “producto listo” entre refinería y realtime.
* Implementar métricas y alertas automáticas en `motor_sentinel`.
* Crear un script de backtest básico con los artefactos de la refinería.
* Añadir soporte multi-exchange (Kraken, Bybit, etc.) manteniendo el mismo formato modular.

---

### 🧩 Nota técnica

> A partir de la versión actual, Reform-Arbi elimina completamente cualquier dependencia de **Codex**, **workspace compartido** o **volúmenes globales**.
> Cada motor opera dentro de su propio contenedor con raíz `/app` y comunicación solo mediante red interna de Docker.

```

---

¿Querés que también te prepare la misma limpieza para el documento de arquitectura global (`ARQUITECTURA.md`)? Así los dos quedan totalmente consistentes y sin referencias a Codex.
```
v