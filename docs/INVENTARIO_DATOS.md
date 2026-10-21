# Inventario de datos de los dos puentes

Revisión del 20 de octubre de 2026. Describe qué datos necesita el sistema por cada puente, de dónde salen, cómo llegan y cuáles están disponibles hoy.

## Qué pide el caso

El caso 6 limita el proyecto a dos puentes de una municipalidad de la Región del Biobío y a tres tipos de medición:

1. Vibración (sensor).
2. Inclinación (sensor).
3. Condición visual, registrada por inspectores.

Las cinco funcionalidades obligatorias son registro de infraestructura, captura de mediciones, reglas de alerta, panel de monitoreo y planificación de mantenimiento. Además se exige al menos una integración. En este proyecto esa integración es la API de la plataforma IoT del proveedor de los sensores.

Solo la vibración y la inclinación llegan por la integración. La condición visual la ingresa el inspector en el sistema, y la ficha del puente la entrega la DOM.

## Inventario por puente

### 1. Ficha del puente (HU-01, tarea 1.4.2)

| Dato | Tipo | Origen | Disponible hoy |
|---|---|---|---|
| Código | texto | DOM o catastro MOP | Sí, en el catastro MOP |
| Nombre | texto | DOM o catastro MOP | Sí, en el catastro MOP |
| Ubicación (lat, lon) | decimal | Catastro MOP | Sí |
| Camino y rol | texto | Catastro MOP | En 211 de 787 puentes del Biobío |
| Cauce o quebrada | texto | Catastro MOP | En 610 de 787 |
| Largo, ancho total y de calzada | metros | Catastro MOP | En la mayoría |
| Número de cepas y de vigas | entero | Catastro MOP | En pocos (42 y 148 de 787) |
| Material de vigas, estribos y piso | texto | Catastro MOP | Casi vacío |
| Año de construcción | entero | Catastro MOP | En 52 de 787 |
| Estado del puente | texto | Catastro MOP | Vacío en los 787 |
| Criticidad | texto | DOM | No |
| Componentes (tablero, viga, estribo) | lista | Equipo, a validar por la DOM | Supuesto del equipo |

### 2. Mediciones de sensores (HU-02, tareas 1.3.x y 1.4.3)

Por cada componente se asume un sensor de vibración y uno de inclinación: seis sensores por puente y doce en total.

| Dato | Tipo | Unidad | Origen | Disponible hoy |
|---|---|---|---|---|
| Puente | texto | — | API del proveedor | No |
| Sensor | texto | — | API del proveedor | No |
| Tipo | `vibracion` / `inclinacion` | — | API del proveedor | No |
| Valor | decimal | m/s² (vibración), grados (inclinación) | API del proveedor | No |
| Fecha y hora | ISO 8601 | — | API del proveedor | No |

Estos cinco campos son los que fija la especificación de integración del equipo.

Hay algo que se debe acordar con el proveedor: en los conjuntos públicos revisados, la vibración se mide entre 100 y 200 veces por segundo. Seis sensores a 200 Hz generan unos 104 millones de lecturas diarias por puente. Para reglas de alerta y un panel no se necesita la señal completa, por lo que conviene pedir valores resumidos por intervalo (por ejemplo, valor máximo y RMS cada 10 minutos). Esto es una propuesta, no un dato confirmado.

### 3. Inspección visual (HU-03, tarea 1.4.3)

| Dato | Tipo | Origen |
|---|---|---|
| Puente y componente | referencia | Registro |
| Fecha | fecha | Inspector |
| Inspector | texto | Inspector |
| Condición | escala definida por la DOM | Inspector |
| Observación | texto | Inspector |
| Fotografía | archivo | Inspector |

No viene de ninguna API: se captura en el sistema. Falta que la DOM defina la escala de condición.

### 4. Umbrales (tarea 1.3.2)

| Dato | Tipo | Origen | Disponible hoy |
|---|---|---|---|
| Variable | `vibracion` / `inclinacion` | Equipo | Sí |
| Valor límite | decimal | Contraparte estructural | No |
| Unidad | texto | Equipo | Sí |
| Validado por | texto | Contraparte estructural | No |

### 5. Datos generados por el sistema (tareas 1.4.4 a 1.4.6)

Alertas (medición, umbral, fecha, estado), tareas de mantenimiento (componente, responsable, fecha programada, estado) e historial. No dependen de una fuente externa, sino de los puntos anteriores.

## Dónde consultar los datos

### Catastro de puentes del MOP (API pública)

Es la única API pública chilena encontrada con datos de puentes. Trae la ficha, no mediciones de sensores. Los puentes son de la Dirección de Vialidad, no municipales.

- Descripción del servicio: <https://rest-sit.mop.gob.cl/arcgis/rest/services/VIALIDAD/Puentes/MapServer/0>
- Lista de campos: <https://rest-sit.mop.gob.cl/arcgis/rest/services/VIALIDAD/Puentes/MapServer/layers>
- Puentes de la Región del Biobío (código de región `08`), en formato tabla: <https://rest-sit.mop.gob.cl/arcgis/rest/services/VIALIDAD/Puentes/MapServer/0/query?where=REGION%3D%2708%27&outFields=*&outSR=4326&f=html>
- Visor de mapas y descargas (SHP, KMZ, GDB): <https://mapasvialidad.mop.gob.cl/>

Provincias: `0801` Concepción, `0802` Arauco, `0803` Biobío. La API entrega hasta 1.000 registros por consulta.

### Puentes de referencia elegidos

Mientras la DOM no entregue sus dos puentes, se usan como referencia dos puentes reales del catastro, elegidos porque están en la misma comuna, en el mismo camino y con la ficha más completa:

| Código | Nombre | Camino | Largo | Ancho | Cepas | Vigas | Piso | Año | Coordenadas |
|---|---|---|---|---|---|---|---|---|---|
| 68P20012 | Puente Huillines I | P-20, Carampangue – Arauco – Llico | 40 m | 10,3 m | 1 | 6 | Asfalto | 1981 | -37.24644, -73.25361 |
| 68P20013 | Puente Huillines II | P-20, Carampangue – Arauco – Llico | 36 m | 10,3 m | 1 | 6 | Asfalto | 1981 | -37.24546, -73.26047 |

Consulta directa de ambos: <https://rest-sit.mop.gob.cl/arcgis/rest/services/VIALIDAD/Puentes/MapServer/0/query?where=CODIGO_PUENTE+IN+%28%2768P20012%27%2C%2768P20013%27%29&outFields=*&outSR=4326&f=html>

En el sistema deben quedar marcados como referencia del catastro MOP, pendientes de confirmación por la DOM.

### Mediciones de sensores (conjuntos públicos, no APIs)

| Conjunto | Qué trae | Enlace |
|---|---|---|
| Puente de prueba de Múnich | Inclinación (grados, 100 Hz), deformación, fuerza y temperatura. No trae aceleración. | <https://github.com/imcs-compsim/munich-bridge-data> |
| Puente ferroviario KW51, Bélgica | Aceleración, deformación, desplazamiento y temperatura, antes y después de una reparación. Archivos mensuales de 186 MB a 4 GB. | <https://zenodo.org/records/3745914> |
| Puente de Vänersborg, Suecia | Aceleración (m/s², 200 Hz) e inclinación (grados). 551,7 MB. | <https://zenodo.org/records/8300495> |
| Camber | Plataforma abierta con formato de una fila por lectura (`timestamp`, `point`, `value`, `unit`). | <https://github.com/vukovicvl/camber> |

### Monitoreo de puentes en Chile

Hay puentes instrumentados (Bicentenario, ferroviario sobre el Biobío, Treng Treng Kay Kay), pero los datos se consultan en portales privados de cada proveedor. La licitación del Treng Treng Kay Kay en Mercado Público describe el servicio (revisión de sensores y reporte mensual de máximos y mínimos), pero no publica el formato de los datos.

## Situación respecto del cronograma

| Fase | Fecha planificada | Qué se puede hacer con lo disponible |
|---|---|---|
| 1.3.1 Levantamiento IoT | 16/09/2026 | Hecho con fuentes públicas. Falta la documentación del proveedor real. |
| 1.3.2 Umbrales | 30/09/2026 | Bloqueado: depende de la contraparte estructural. |
| 1.3.3 Correspondencia sensor-componente | 23/09/2026 | Parcial: hay seis sensores por puente, sin código del proveedor. |
| 1.3.4 Acceso a la API | 30/09/2026 | Bloqueado: sin URL ni credenciales. |
| 1.3.5 Validación de conectividad | 12/10/2026 | Bloqueado. |
| 1.4.2 Registro de infraestructura | 29/09/2026 | Se puede completar con los dos puentes de referencia del catastro MOP. |
| 1.4.3 Captura de mediciones | después de 1.3.5 | Se puede construir contra una API simulada; la carga real espera a 1.3.5. |
| 1.4.4 Reglas de alerta | 03/11/2026 | Se puede programar la lógica; los valores esperan a 1.3.2. |
| 1.4.5 Panel de monitoreo | 24/11/2026 | Se puede construir con datos de referencia y simulados. |
| 1.4.6 Planificación de mantenimiento | 24/11/2026 | No depende de terceros. |
| 1.5 Pruebas integrales y aceptación | dic 2026 | La prueba 1.5.2.6 exige la API real. |
| 1.6 Piloto, capacitación y cierre | 06/01 al 25/02/2027 | Requiere datos reales en ambos puentes. |

## Orden de trabajo por incremento

El incremento comprometido en el sprint review de la EV2 es el registro de infraestructura de los dos puentes (1.4.2, HU-01). Captura, alertas, panel y mantenimiento no entran en este incremento. El orden siguiente respeta las fechas de la línea de base:

| Incremento | Contenido | Fecha planificada | Condición para cerrarlo |
|---|---|---|---|
| Actual | Registro de los dos puentes con la ficha del catastro MOP, componentes y sensores | 29/09/2026 (atrasado) | La DOM confirma los puentes o acepta los de referencia |
| Siguiente | Captura de mediciones contra una API simulada, con los cinco campos acordados | Después de 1.3.5 | Cambiar a la API real cuando lleguen las credenciales |
| Siguiente | Reglas de alerta con umbrales de prueba | 03/11/2026 | Reemplazar los umbrales de prueba por los validados (1.3.2) |
| Cierre de 1.4 (MVP) | Panel de monitoreo y planificación de mantenimiento | 24/11/2026 | Pruebas 1.5 en diciembre |

Preparar la API simulada mientras se espera al proveedor está dentro de lo acordado: la planilla de seguimiento del 06/10 indica para 1.4.3 «no forzar: esperar 1.3.4/1.3.5; preparar mock». No cambia el alcance ni las fechas.

## Propuesta para el MVP con panel

El MVP al cierre de 1.4 (24/11/2026) puede mostrar el panel de la Municipalidad del Biobío con los datos que sí existen y con una API simulada del proveedor para lo que falta. Una posible organización con Docker Compose:

| Servicio | Función | Datos |
|---|---|---|
| `proveedor-simulado` | Expone `GET /mediciones?puente=&desde=` con los cinco campos acordados | Inclinación tomada del archivo real de Múnich; vibración tomada de KW51 o Vänersborg si se descarga un tramo, o generada y marcada como simulada |
| `captura` | Consulta la API cada cierto intervalo, valida los cinco campos y guarda | — |
| `db` | Base de datos (SQLite o PostgreSQL) | Ficha de los dos puentes desde el catastro MOP |
| `panel` | Estado de los puentes, últimas mediciones, alertas y tareas de mantenimiento | — |

Condiciones para que la simulación no se confunda con el sistema real:

- Cada medición guarda su origen (`simulado` o `api_proveedor`), y el panel lo muestra.
- Los umbrales del MVP se etiquetan como de prueba, no como valores validados.
- Al recibir las credenciales reales, solo cambian la URL y la autenticación de `captura`; el resto del sistema se mantiene.
