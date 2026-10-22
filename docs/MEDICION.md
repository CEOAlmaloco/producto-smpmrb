# Medición del avance

El avance se mide contra la línea de base del proyecto. Las fechas planificadas no se modifican: si una tarea venció, se registra como atrasada.

El estado de cada tarea se calcula a partir de lo que existe en la base de datos (puentes confirmados, sensores con acceso, umbrales cargados y mediciones guardadas), no a partir de porcentajes estimados. Para obtenerlo:

```powershell
$env:PYTHONPATH = "src"
python -m smpmrb.estado
```

## Estados

| Estado | Descripción |
|---|---|
| `atrasado_hecho` | Terminada después de la fecha planificada. |
| `atrasado_parcial` | Vencida, con una parte terminada y otra que depende de un tercero. |
| `bloqueado` | No puede avanzar por falta de credenciales del proveedor. |
| `no_iniciado` | Aún no comienza. |

## Situación al 21/10/2026

- **Umbrales (1.3.2)**, planificados al 30/09. El equipo adoptó el 21/10 valores tomados de normas publicadas (ver `LEVANTAMIENTO_IOT.md`). Estado: `atrasado_hecho`. La revisión de la contraparte queda para antes de la puesta en marcha.

- **Registro de infraestructura (1.4.2)**, planificado al 29/09. El módulo valida el código obligatorio y evita duplicados, pero los dos puentes no tienen nombre ni ubicación oficiales. Estado: `atrasado_parcial`.
- **Acceso a la API (1.3.4)**, planificado al 30/09, y **validación de conectividad (1.3.5)**, planificada al 12/10. No hay credenciales. Estado: `bloqueado`. En el corte del 26/10 se mantienen los últimos valores reportados (85% y 40%, del 06/10), porque no hay una medición nueva. El módulo `proveedor_simulado` no cuenta como evidencia de estas tareas.
- **Reglas de alerta (1.4.4)**, planificadas al 03/11. Los umbrales ya están; falta tener mediciones reales. Esta fecha está en riesgo.
