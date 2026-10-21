# Medición del avance

El avance se mide contra la línea de base del proyecto. Las fechas planificadas no se modifican: si una tarea venció, se registra como atrasada.

El estado de cada tarea se calcula a partir de lo que existe en la base de datos (puentes confirmados, sensores con acceso, umbrales con valor y mediciones guardadas), no a partir de porcentajes estimados. Para obtenerlo:

```powershell
$env:PYTHONPATH = "src"
python -m smpmrb.estado
```

## Estados

| Estado | Descripción |
|---|---|
| `atrasado_hecho` | Terminada después de la fecha planificada. |
| `atrasado_parcial` | Vencida, con una parte terminada y otra que depende de un tercero. |
| `bloqueado` | No puede avanzar por falta de credenciales o de umbrales validados. |
| `no_iniciado` | Aún no comienza. |

## Situación al 20/10/2026

- **Registro de infraestructura (1.4.2)**, planificado al 29/09. El módulo valida el código obligatorio y evita duplicados, pero los dos puentes no tienen nombre ni ubicación oficiales. Estado: `atrasado_parcial`.
- **Acceso a la API (1.3.4)**, planificado al 30/09, y **validación de conectividad (1.3.5)**, planificada al 12/10. No hay credenciales. Estado: `bloqueado`. Los porcentajes del corte del 6/10 (85% y 40%) no se actualizan sin una nueva medición.
- **Reglas de alerta (1.4.4)**, planificadas al 03/11. No se inician hasta tener umbrales y mediciones. Esta fecha está en riesgo.
