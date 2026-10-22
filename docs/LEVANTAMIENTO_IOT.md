# Levantamiento de la fuente de datos

Revisión realizada el 20 de octubre de 2026.

Según el caso, los sensores de vibración e inclinación ya están instalados en los dos puentes y un proveedor externo entrega sus datos mediante una API. Hasta ahora no se conoce el nombre del proveedor, la URL de la API ni las credenciales de acceso, por lo que las tareas 1.3.4 (acceso a la API) y 1.3.5 (validación de conectividad) siguen pendientes. El repositorio incluye un proveedor simulado (`smpmrb.proveedor_simulado`) para probar la captura. Su token `simulado-local` no es una credencial del proveedor.

Como referencia del formato, se revisaron conjuntos de datos públicos de monitoreo de puentes.

## Formato mínimo definido por el equipo

La especificación de integración del proyecto establece que cada medición debe incluir:

| Campo | Descripción |
|---|---|
| puente | Identificador del puente |
| sensor | Identificador del sensor |
| tipo | `vibracion` o `inclinacion` |
| valor | Valor numérico medido |
| fecha y hora | Momento de la medición |

El sistema consulta la API del proveedor; no recibe datos enviados por el proveedor. El formato de respuesta (JSON o CSV), la autenticación y la frecuencia de consulta se definirán cuando se tenga acceso a la documentación de la API.

## Fuentes revisadas

### Puente de prueba de Múnich (descargado)

Repositorio [imcs-compsim/munich-bridge-data](https://github.com/imcs-compsim/munich-bridge-data), licencia MIT. Se descargó `ReferenceState/ReferenceStateINCAt100Hz.csv.zip` (1,1 MB). Aunque el nombre termina en `.zip`, el archivo que se obtiene al descomprimirlo es un CSV.

- Codificación Windows (cp1252), separador coma, frecuencia de muestreo de 100 Hz.
- Encabezado: `Time (-),INC-01 [deg],INC-01 Filtered [deg]`
- Primera fila: `2022-03-07 16:35:15.600,0.0013118329225108,2.39921319825824e-10`

El archivo contiene solo inclinación, en grados, con la señal original y la señal filtrada. No incluye vibración ni un identificador de puente.

El artículo asociado (Jaelani et al., Steel Construction, 2023) describe la instrumentación completa: 8 acelerómetros uniaxiales Metra KS48 C, 8 triaxiales Metra KS823B y 10 inclinómetros Seika SB1 U. Esos datos no están en el archivo descargado, por lo que no se cargaron en la base.

### Puente de Vänersborg, Suecia (no descargado)

Conjunto publicado por IoTBridge AB en Zenodo (551,7 MB), con aceleraciones, deformaciones e inclinación. No se descargó por su tamaño. El artículo asociado documenta las columnas:

- `ts`: fecha y hora (UTC).
- `ch_18` a `ch_22`: aceleración en m/s².
- `ch_25`: inclinación en grados.
- Muestreo de 200 Hz y coma como separador decimal.

### Camber (plataforma de código abierto)

Repositorio [vukovicvl/camber](https://github.com/vukovicvl/camber). Importa archivos CSV con una fila por lectura (`timestamp`, `point`, `value`, `unit`) y expone un endpoint local `POST /measurements`. Es el formato más parecido al definido por el equipo.

### Puentes instrumentados en Chile

Existen sistemas de monitoreo en el Puente Bicentenario (MOP), en el puente ferroviario sobre el río Biobío (EFE, con equipos Resensys) y en el puente Treng Treng Kay Kay (Sixense). En todos los casos los datos se consultan en portales privados de cada proveedor y no hay ejemplos públicos del formato.

## Conclusiones para la integración

- La vibración se entrega como una serie de aceleraciones en m/s², muestreada entre 100 y 200 veces por segundo, no como un valor único.
- La inclinación se entrega en grados y puede venir acompañada de una versión filtrada.
- En los archivos revisados, el puente y el tipo de medición no vienen en cada fila, sino en el nombre del archivo o en la descripción del canal. El módulo de captura deberá agregar esos datos al guardar cada medición.

## Componentes y sensores del piloto

Cada puente del piloto tiene registrados tres componentes (tablero, viga principal y estribo), cada uno con un sensor de vibración y uno de inclinación. Los sensores no tienen aún el código asignado por el proveedor; se completará cuando se entregue el acceso a la API.

## Umbrales (tarea 1.3.2)

El equipo adoptó el 21/10/2026 umbrales tomados de normas publicadas. Quedan cargados en la tabla `umbral` y son los valores vigentes del sistema. La contraparte estructural los revisa antes de la puesta en marcha (criterio 4.3 del alcance); si propone otros valores, se cambian en la tabla sin tocar el código.

| Variable | Cómo se calcula | Atención | Alerta | Crítico | Fuente |
|---|---|---|---|---|---|
| Vibración | Aceleración vertical pico del componente en ventanas de 1 minuto | 0,5 m/s² | 1,0 m/s² | 2,5 m/s² | Sétra 2006 y HiVoSS (clases de confort: máximo < 0,5; medio 0,5–1,0; mínimo 1,0–2,5; inaceptable > 2,5). EN 1990 Anexo A2 recomienda 0,7 m/s² |
| Inclinación | Cambio respecto de la referencia del sensor (promedio de sus primeros 30 días), con promedio móvil de 1 hora | 0,115° (0,002 rad) | 0,229° (0,004 rad) | 0,458° (0,008 rad) | AASHTO LRFD 10.5.2.2: distorsión angular tolerable de 0,004 rad en puentes continuos y 0,008 rad en tramos simples |

Límites de estos valores:

- Los de vibración son criterios de confort y servicio, no de capacidad estructural. Sirven para detectar un comportamiento anormal, no para diagnosticar daño.
- AASHTO define la distorsión angular entre fundaciones. Aquí se usa como aproximación para el giro de un componente.
- La inclinación se compara contra su propia referencia y no contra cero, porque cada sensor queda montado con un ángulo distinto. El promedio de 1 hora filtra el ciclo térmico del día.
- Un nivel se activa cuando se supera en 3 lecturas consecutivas, para no alertar por un golpe aislado.
- Si un sensor pasa más de 60 minutos sin enviar datos, se genera una alerta técnica de «sin datos» dirigida a TI y al proveedor.

### Condición visual

El Manual de Carreteras del MOP (Vol. 7, 7.204.306 y 7.204.307) califica los deterioros por severidad baja, media o alta. El proyecto agrega «crítica» para los casos en que el inspector ve un riesgo inmediato para los usuarios.

| Severidad registrada | Nivel en el sistema | Ejemplos |
|---|---|---|
| Baja | Normal (queda registrada) | Fisuras superficiales, suciedad en juntas o drenajes |
| Media | Atención | Corrosión que avanza, saltaduras de hormigón, juntas dañadas |
| Alta | Alerta | Armadura expuesta, apoyo desplazado, socavación incipiente |
| Crítica | Crítico | Socavación que deja a la vista la fundación, desplazamiento visible del tablero, falla de un apoyo |

### Qué pasa en cada nivel

| Nivel | Quién recibe la alerta | Acción | Plazo |
|---|---|---|---|
| Atención | DOM, en el panel | Se revisa el componente en la próxima inspección rutinaria | 30 días |
| Alerta | DOM, en el panel y por correo | La DOM programa una inspección del componente y la asigna a un inspector | 7 días |
| Crítico | DOM, aviso inmediato | Inspección extraordinaria. La DOM decide si restringe el tránsito y convoca al especialista. El sistema registra la decisión, no cierra el puente | 24 horas |
