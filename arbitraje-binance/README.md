Arbitraje Binance — Stack de desarrollo y sujeto de prueba

Propósito
- Servir como laboratorio principal (y base de negocio) para el motor de arbitraje triangular con ICI.
- Montajes y tooling pensados para modularidad, trazabilidad y baja latencia.

Servicios clave
- `motor_data_refinery`: refina y estandariza datos crudos para consumo rápido por realtime.
- `motor_reactor_realtime`: decide/ejecuta arbitraje en <3 ms lógicos; minimiza latencias.
- `motor_sentinel`: observa, agrega y envía eventos al hub.
- `event_hub` (externo, en `beacon_node/`): recolector WS y notificador.

Montajes (racional)
- `../:ro` → `/workspace/1-repo-global-solo-lectura`: vista completa en solo lectura dentro del contenedor (contexto sin riesgo).
- `../.git:/workspace/<motor>/.git:rw`: mapea el .git global al motor para commits locales por contenedor (trazabilidad de cambios del motor).
- `./<motor>:/workspace/<motor>:rw`: código del motor en RW.
- Volumen `workspace_root_<motor>:/workspace`: raíz RW del contenedor (asegura persistencia de home/workspace y prioridad de submontajes).
- Logs y outputs específicos del servicio montados en rutas del motor.

Variables relevantes (ejemplos)
- `HUB_WS_URL`: URL WS hacia Event Hub (por defecto `ws://event_hub:8080/ws`).
- Credenciales DB/Redis/TZ según `.env`.

Flujo recomendado en contenedor
1) Entrar al contenedor del motor correspondiente.
2) Trabajar solo dentro del directorio del motor.
3) Hacer commits atómicos y registrar cambios según tu flujo habitual.

Notas
- Este stack no busca “un botón y listo”: Dominus valida manualmente formatos por exchange; la carga de estandarización vive en refinery.
