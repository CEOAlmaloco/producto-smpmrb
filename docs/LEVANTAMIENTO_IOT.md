# Levantamiento de la fuente de datos

Revisión realizada el 20 de octubre de 2026.

Según el caso, los sensores de vibración e inclinación ya están instalados en los dos puentes y un proveedor externo entrega sus datos mediante una API. Hasta ahora no se conoce el nombre del proveedor, la URL de la API ni las credenciales de acceso, por lo que las tareas 1.3.4 (acceso a la API) y 1.3.5 (validación de conectividad) siguen pendientes.

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

## Umbrales

Los umbrales de vibración e inclinación están creados sin valor. Deben ser definidos por la contraparte de ingeniería estructural, no por el equipo de desarrollo.
