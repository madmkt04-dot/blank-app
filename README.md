# MIS Costos Flexografía

Aplicativo MVP en Streamlit para estimación de costos, pricing y gestión presupuestal de órdenes flexográficas.

## Objetivo

Construir un módulo inicial tipo MIS/ERP para cotizar productos flexográficos por orden de trabajo, separando costos técnicos, costos comerciales y estrategias de precio.

## Módulos incluidos

- Datos de OP: producto, cliente, cantidad, avance, carriles y ancho de bobina.
- Materiales: sustrato, tinta y barniz.
- Producción: merma, velocidad, set up, horas máquina y mano de obra.
- Costos fijos de OP: clisé, preprensa y preparación.
- Acabados: troquelado, rebobinado y empaque.
- Costos indirectos: CIF aplicado, administración, ventas, comisión, flete y costo financiero.
- Pricing: precio mínimo, precio por markup, precio técnico por margen sobre venta y precio estratégico por valor.
- Sensibilidad: escenarios de material, merma, tiraje, velocidad, set up y margen.

## Fórmulas principales

```text
Metros lineales netos = Cantidad × Avance / Carriles
Metros lineales totales = Metros netos + Merma arranque + Merma corrida
Área m² = Metros totales × Ancho bobina
Costo sustrato = Área m² × Costo m²
Costo tinta = Área m² × Consumo g/m² × Costo kg / 1000
Horas corrida = Metros totales / Velocidad mL/h
Costo máquina = (Horas set up + Horas corrida) × Tarifa máquina
Costo total = Fabricación + Comercial
Precio por margen sobre venta = Costo total / (1 - Margen objetivo)
```

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Estructura

```text
streamlit_app.py      Interfaz MIS para cotización y escenarios
pricing_engine.py     Motor de cálculo de costos y pricing flexográfico
requirements.txt      Dependencias del MVP
```

## Próximos módulos sugeridos

1. Base de datos de clientes, materiales, máquinas y tarifas.
2. Historial de cotizaciones por cliente y producto.
3. Aprobación de descuentos y márgenes mínimos.
4. Comparativo presupuesto vs real por OP.
5. Exportación de cotización a PDF/Excel.
6. Dashboard de rentabilidad por cliente, máquina, familia y vendedor.
