# SMPMRB — Sistema de monitoreo de puentes municipales

Proyecto del curso GPY1102 (Gestión de Proyectos de Software, Duoc UC), caso 6. El sistema apoya a la Dirección de Obras Municipales (DOM) de la Municipalidad del Biobío en el monitoreo y la mantención de dos puentes piloto, usando los sensores de vibración e inclinación que ya están instalados en ellos.

Este repositorio contiene el avance del software al 20 de octubre de 2026, según el cronograma del proyecto.

## Estado actual

Implementado:

- Registro de puentes (HU-01): código único, componentes, sensores asociados y nivel de criticidad.
- Base de datos SQLite con las tablas de puentes, componentes, sensores, umbrales y mediciones.
- Catálogo de canales de un conjunto de datos público de sensores de puentes (ver `docs/LEVANTAMIENTO_IOT.md`).
- Validación que impide guardar mediciones de un sensor que aún no tiene acceso a la API del proveedor.
- Proveedor simulado local. Genera una lectura de prueba por sensor, con origen `simulado`. No cierra el acceso a la API.

Pendiente:

- Nombre y ubicación oficiales de los dos puentes, que debe entregar la DOM.
- URL y credenciales reales de la API del proveedor de los sensores. El token `simulado-local` no las reemplaza.
- Revisión de los umbrales por un ingeniero estructural. Los valores adoptados por el equipo ya están cargados (ver `docs/LEVANTAMIENTO_IOT.md`).
- Módulos de alertas, panel de monitoreo y planificación de mantenimiento.

## Requisitos

- Python 3.12 o superior. No usa dependencias externas.

## Uso

Desde la raíz del repositorio (PowerShell):

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m smpmrb.estado
python -m smpmrb.proveedor_simulado
```

El último comando guarda 12 lecturas de prueba en `data/smpmrb.sqlite`. Volver a ejecutarlo reemplaza las de ese mismo instante.

El segundo comando crea la base en `data/smpmrb.sqlite` (ignorada por git) y muestra el estado de cada tarea del cronograma.

## Estructura

```
src/smpmrb/   código fuente
tests/        pruebas unitarias
data/         encabezado del archivo público de sensores
docs/         arquitectura, inventario de datos, fuentes revisadas y criterio de medición
```

El detalle de qué datos se necesitan por puente y dónde consultarlos está en `docs/INVENTARIO_DATOS.md`.
