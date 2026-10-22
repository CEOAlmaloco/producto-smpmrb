# Arquitectura

El sistema contempla cinco funciones: registro de infraestructura, captura de mediciones, reglas de alerta, panel de monitoreo y planificación de mantenimiento. A la fecha solo está implementado el registro, y de forma parcial.

## Flujo de datos

```
Sensores instalados en el puente (no forman parte del proyecto)
        │
        ▼
Plataforma IoT del proveedor  ──  API (URL y credenciales pendientes)
        │
        ▼
Módulo de captura (smpmrb.medicion)
        │
        ▼
Base de datos SQLite
        ├── puentes, componentes y sensores   (smpmrb.registro)
        ├── umbrales: 3 niveles por variable, adoptados por el equipo
        └── mediciones
```

Mientras no exista acceso a la API, el módulo de captura rechaza una medición que se presente como proveniente del proveedor. `smpmrb.proveedor_simulado` puede guardar lecturas de prueba con origen `simulado`. Esas lecturas no cierran las tareas 1.3.4 ni 1.3.5.

El conjunto de datos público de Múnich se usa solo como referencia del formato de los datos. Sus canales se guardan en una tabla aparte (`canal_publico`) y no se asocian a los puentes del piloto.

## Tecnologías

- Python 3.12, solo biblioteca estándar.
- SQLite como base de datos.
- `unittest` para las pruebas.

Todavía no hay interfaz web. El panel de monitoreo corresponde a la tarea 1.4.5 del cronograma, con fecha de término el 24/11/2026.

## Fuera de alcance

- Un tercer puente.
- Compra o instalación de sensores.
- Algoritmos predictivos.
