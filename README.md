# MIS Costos Flexografia

Aplicativo MVP en Streamlit para estimacion de costos, pricing, gestion presupuestal y analisis con IA para ordenes flexograficas.

## Objetivo

Construir un modulo inicial tipo MIS/ERP para cotizar productos flexograficos por orden de trabajo, separando costos tecnicos, costos comerciales, estrategias de precio y recomendaciones gerenciales con IA.

## Modulos incluidos

- Datos de OP: producto, cliente, cantidad, avance, carriles y ancho de bobina.
- Materiales: sustrato, tinta y barniz.
- Produccion: merma, velocidad, set up, horas maquina y mano de obra.
- Costos fijos de OP: clise, preprensa y preparacion.
- Acabados: troquelado, rebobinado y empaque.
- Costos indirectos: CIF aplicado, administracion, ventas, comision, flete y costo financiero.
- Pricing: precio minimo, precio por markup, precio tecnico por margen sobre venta y precio estrategico por valor.
- Sensibilidad: escenarios de material, merma, tiraje, velocidad, set up y margen.
- Copiloto IA: explicacion de la cotizacion, alertas de rentabilidad, recomendacion de precio y decision sugerida.

## Integracion IA

El archivo `ai_copilot.py` agrega un copiloto de costos flexograficos. La IA recibe el contexto de la cotizacion calculada y puede responder preguntas como:

```text
Analiza esta cotizacion y dime si conviene aceptarla, negociarla o recalcularla.
Por que esta OP salio cara?
Que pasa si reduzco set up o merma?
Cual es el mayor riesgo de rentabilidad?
```

La IA no reemplaza el motor de calculo. El calculo oficial lo realiza `pricing_engine.py`; el copiloto interpreta, explica y recomienda.

## Configuracion

Puedes configurar la clave mediante variable de entorno `OPENAI_API_KEY` y opcionalmente el modelo mediante `OPENAI_MODEL`. Si no configuras clave, el sistema sigue funcionando con recomendaciones por reglas internas.

## Como ejecutarlo

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Estructura

```text
streamlit_app.py      Interfaz MIS para cotizacion, escenarios y copiloto IA
pricing_engine.py     Motor de calculo de costos y pricing flexografico
ai_copilot.py         Modulo de IA para analisis gerencial de cotizaciones
requirements.txt      Dependencias del MVP
```
