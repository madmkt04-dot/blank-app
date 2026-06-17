import streamlit as st

from ai_copilot import analyze_with_ai, build_copilot_context, build_executive_summary, rule_based_recommendations
from pricing_engine import FlexoEstimateInput, build_sensitivity, estimate_flexo_cost


st.set_page_config(page_title="MIS Costos Flexografía", layout="wide")


def money(value: float) -> str:
    return f"S/ {value:,.2f}"


def number(value: float, suffix: str = "") -> str:
    return f"{value:,.2f}{suffix}"


def get_secret(name: str, default: str = "") -> str:
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


st.title("Módulo MIS de estimación de costos y pricing flexográfico")
st.caption("MVP con motor de costos, pricing, sensibilidad y copiloto IA para análisis gerencial de cotizaciones.")

with st.sidebar:
    st.header("Datos de la OP")
    product = st.text_input("Producto", "Etiqueta adhesiva flexográfica")
    customer = st.text_input("Cliente", "Cliente demo")
    quantity_units = st.number_input("Cantidad solicitada (unidades)", min_value=0.0, value=100000.0, step=1000.0)
    advance_m = st.number_input("Avance / desarrollo longitudinal (m)", min_value=0.0, value=0.10, step=0.01, format="%.4f")
    lanes = st.number_input("Carriles útiles", min_value=1, value=2, step=1)
    web_width_m = st.number_input("Ancho de bobina (m)", min_value=0.0, value=0.33, step=0.01, format="%.4f")

    st.header("Materiales")
    substrate_cost_per_m2 = st.number_input("Costo sustrato (S/ por m²)", min_value=0.0, value=1.80, step=0.10)
    ink_consumption_g_m2 = st.number_input("Consumo tinta (g/m²)", min_value=0.0, value=3.50, step=0.10)
    ink_cost_per_kg = st.number_input("Costo tinta (S/ por kg)", min_value=0.0, value=85.0, step=1.0)
    varnish_consumption_g_m2 = st.number_input("Consumo barniz (g/m²)", min_value=0.0, value=1.20, step=0.10)
    varnish_cost_per_kg = st.number_input("Costo barniz (S/ por kg)", min_value=0.0, value=45.0, step=1.0)

    st.header("Merma y producción")
    startup_waste_m = st.number_input("Merma de arranque (mL)", min_value=0.0, value=250.0, step=10.0)
    run_waste_pct = st.number_input("Merma de corrida (%)", min_value=0.0, value=3.0, step=0.5)
    machine_speed_ml_h = st.number_input("Velocidad efectiva (mL/h)", min_value=1.0, value=3600.0, step=100.0)
    setup_hours = st.number_input("Tiempo de set up (h)", min_value=0.0, value=1.20, step=0.10)
    machine_rate_h = st.number_input("Tarifa máquina (S/ h)", min_value=0.0, value=220.0, step=10.0)
    labor_rate_h = st.number_input("Costo MOD (S/ h)", min_value=0.0, value=35.0, step=1.0)
    labor_hours_extra = st.number_input("Horas MOD extra", min_value=0.0, value=0.50, step=0.10)

    st.header("Costos fijos de OP y acabados")
    plate_cost = st.number_input("Clisé / placas (S/)", min_value=0.0, value=450.0, step=10.0)
    prepress_cost = st.number_input("Preprensa (S/)", min_value=0.0, value=120.0, step=10.0)
    die_cut_cost = st.number_input("Troquelado (S/)", min_value=0.0, value=180.0, step=10.0)
    rewind_cost = st.number_input("Rebobinado (S/)", min_value=0.0, value=100.0, step=10.0)
    packing_cost = st.number_input("Empaque (S/)", min_value=0.0, value=80.0, step=10.0)

    st.header("Pricing")
    overhead_pct = st.number_input("Costos indirectos fabricación (%)", min_value=0.0, value=12.0, step=0.5)
    admin_sales_pct = st.number_input("Gasto adm. y ventas (%)", min_value=0.0, value=7.0, step=0.5)
    commission_pct = st.number_input("Comisión comercial (%)", min_value=0.0, value=3.0, step=0.5)
    freight_cost = st.number_input("Flete / despacho (S/)", min_value=0.0, value=150.0, step=10.0)
    finance_pct = st.number_input("Costo financiero (%)", min_value=0.0, value=1.5, step=0.5)
    markup_on_cost_pct = st.number_input("Markup sobre costo (%)", min_value=0.0, value=30.0, step=1.0)
    margin_on_sales_pct = st.number_input("Margen objetivo sobre venta (%)", min_value=0.0, max_value=95.0, value=25.0, step=1.0)
    minimum_contribution_pct = st.number_input("Contribución mínima sobre variable (%)", min_value=0.0, value=15.0, step=1.0)
    strategic_value_premium_pct = st.number_input("Premium estratégico / valor (%)", min_value=0.0, value=8.0, step=1.0)
    market_price = st.number_input("Precio mercado referencial (S/)", min_value=0.0, value=0.0, step=100.0)
    tax_pct = st.number_input("IGV / impuesto (%)", min_value=0.0, value=18.0, step=1.0)

input_data = FlexoEstimateInput(
    product=product,
    customer=customer,
    quantity_units=quantity_units,
    advance_m=advance_m,
    lanes=int(lanes),
    web_width_m=web_width_m,
    substrate_cost_per_m2=substrate_cost_per_m2,
    ink_consumption_g_m2=ink_consumption_g_m2,
    ink_cost_per_kg=ink_cost_per_kg,
    varnish_consumption_g_m2=varnish_consumption_g_m2,
    varnish_cost_per_kg=varnish_cost_per_kg,
    startup_waste_m=startup_waste_m,
    run_waste_pct=run_waste_pct,
    machine_speed_ml_h=machine_speed_ml_h,
    setup_hours=setup_hours,
    machine_rate_h=machine_rate_h,
    labor_rate_h=labor_rate_h,
    labor_hours_extra=labor_hours_extra,
    plate_cost=plate_cost,
    prepress_cost=prepress_cost,
    die_cut_cost=die_cut_cost,
    rewind_cost=rewind_cost,
    packing_cost=packing_cost,
    overhead_pct=overhead_pct,
    admin_sales_pct=admin_sales_pct,
    commission_pct=commission_pct,
    freight_cost=freight_cost,
    finance_pct=finance_pct,
    markup_on_cost_pct=markup_on_cost_pct,
    margin_on_sales_pct=margin_on_sales_pct,
    minimum_contribution_pct=minimum_contribution_pct,
    strategic_value_premium_pct=strategic_value_premium_pct,
    market_price=market_price,
    tax_pct=tax_pct,
)

result = estimate_flexo_cost(input_data)

top1, top2, top3, top4 = st.columns(4)
top1.metric("Costo total", money(result["total_cost"]), help="Costo fabricación + costo comercial")
top2.metric("Precio técnico", money(result["technical_price"]), help="Precio calculado por margen sobre venta")
top3.metric("Margen bruto", number(result["gross_margin_pct"], "%"), help="Sobre precio técnico")
top4.metric("Precio unitario", money(result["unit_price"]), help="Precio técnico / cantidad")

tabs = st.tabs(["Resumen OP", "Costos", "Pricing", "Sensibilidad", "Copiloto IA"])

tab_resumen, tab_costos, tab_pricing, tab_sensibilidad, tab_ai = tabs

with tab_resumen:
    st.subheader("Resumen técnico de la orden")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("**Producto:**", input_data.product)
        st.write("**Cliente:**", input_data.customer)
        st.write("**Cantidad:**", number(result["quantity_units"]))
        st.write("**Área impresa:**", number(result["area_m2"], " m²"))
    with c2:
        st.write("**Metros netos:**", number(result["net_linear_m"], " mL"))
        st.write("**Metros totales:**", number(result["total_linear_m"], " mL"))
        st.write("**Merma total:**", number(result["waste_impact_m"], " mL"))
        st.write("**Merma sobre total:**", number(result["waste_impact_pct_of_total"], "%"))
    with c3:
        st.write("**Horas corrida:**", number(result["run_hours"], " h"))
        st.write("**Horas set up:**", number(result["setup_hours"], " h"))
        st.write("**Horas máquina total:**", number(result["total_machine_hours"], " h"))
        st.write("**Impacto set up unitario:**", money(result["setup_impact_unit"]))

    st.info("El set up, clisé y preprensa son costos fijos de OP. A mayor tiraje, se diluyen por unidad; a menor tiraje, elevan el precio unitario.")

with tab_costos:
    st.subheader("Estructura de costos")
    cost_rows = [
        {"bloque": "Material directo", "concepto": "Sustrato", "importe": money(result["substrate_cost"])},
        {"bloque": "Material directo", "concepto": "Tinta", "importe": money(result["ink_cost"])},
        {"bloque": "Material directo", "concepto": "Barniz", "importe": money(result["varnish_cost"])},
        {"bloque": "Máquina", "concepto": "Set up", "importe": money(result["setup_machine_cost"])},
        {"bloque": "Máquina", "concepto": "Corrida", "importe": money(result["run_machine_cost"])},
        {"bloque": "MOD", "concepto": "Mano de obra directa", "importe": money(result["direct_labor_cost"])},
        {"bloque": "Fijo OP", "concepto": "Clisé / placas", "importe": money(result["plate_cost"])},
        {"bloque": "Fijo OP", "concepto": "Preprensa", "importe": money(result["prepress_cost"])},
        {"bloque": "Acabados", "concepto": "Troquelado + rebobinado + empaque", "importe": money(result["finishing_cost"])},
        {"bloque": "Indirectos", "concepto": "CIF aplicado", "importe": money(result["overhead_cost"])},
        {"bloque": "Comercial", "concepto": "Adm. ventas + comisión + flete + financiero", "importe": money(result["commercial_cost"])},
    ]
    st.table(cost_rows)

    st.subheader("Indicadores unitarios")
    unit_rows = [
        {"indicador": "Costo unitario", "valor": money(result["unit_cost"])},
        {"indicador": "Costo por millar", "valor": money(result["cost_per_thousand"])},
        {"indicador": "Costo por metro lineal", "valor": money(result["cost_per_linear_m"])},
        {"indicador": "Costo por m²", "valor": money(result["cost_per_m2"])},
    ]
    st.table(unit_rows)

with tab_pricing:
    st.subheader("Estrategias de precio")
    price_rows = [
        {"estrategia": "Precio mínimo por contribución", "valor": money(result["minimum_contribution_price"]), "uso": "Pedidos especiales o capacidad ociosa"},
        {"estrategia": "Precio por markup sobre costo", "valor": money(result["price_markup_cost"]), "uso": "Cotización rápida tipo costo + %"},
        {"estrategia": "Precio técnico por margen sobre venta", "valor": money(result["technical_price"]), "uso": "Precio recomendado de control gerencial"},
        {"estrategia": "Precio estratégico por valor", "valor": money(result["strategic_price"]), "uso": "Entrega rápida, complejidad, calidad o urgencia"},
        {"estrategia": "Precio con impuesto", "valor": money(result["price_with_tax"]), "uso": "Precio técnico + IGV/impuesto"},
    ]
    st.table(price_rows)

    if result["market_price"] > 0:
        st.subheader("Target costing vs mercado")
        target_rows = [
            {"indicador": "Precio mercado", "valor": money(result["market_price"])},
            {"indicador": "Costo permitido por margen objetivo", "valor": money(result["target_allowed_cost"])},
            {"indicador": "Brecha de costo", "valor": money(result["target_cost_gap"])},
        ]
        st.table(target_rows)
        if result["target_cost_gap"] > 0:
            st.warning("El costo interno supera el costo permitido por el mercado. Revisar material, merma, set up, velocidad o margen.")
        else:
            st.success("El costo interno entra dentro del costo permitido por el mercado.")

    st.subheader("Regla de decisión")
    st.write("Acepta una OP de bajo margen solo si cubre el costo variable, aporta contribución positiva y existe capacidad ociosa. No conviene aceptarla si desplaza pedidos más rentables, exige crédito riesgoso o genera reprocesos no considerados.")

with tab_sensibilidad:
    st.subheader("Análisis de sensibilidad")
    sensitivity_rows = build_sensitivity(input_data)
    formatted_rows = []
    for row in sensitivity_rows:
        formatted_rows.append({
            "escenario": row["escenario"],
            "costo_total": money(row["costo_total"]),
            "precio_tecnico": money(row["precio_tecnico"]),
            "precio_estrategico": money(row["precio_estrategico"]),
            "costo_unitario": money(row["costo_unitario"]),
            "precio_unitario": money(row["precio_unitario"]),
            "margen_bruto": number(row["margen_bruto_pct"], "%"),
            "metros_totales": number(row["metros_totales"], " mL"),
            "horas_maquina": number(row["horas_maquina"], " h"),
        })
    st.table(formatted_rows)
    st.caption("Simula rápidamente el efecto de tiraje, merma, set up, velocidad, margen y material sobre el precio final.")

with tab_ai:
    st.subheader("Copiloto IA de costos flexográficos")
    st.write("La IA usa el resultado de la cotización actual para explicar drivers de costo, riesgos, precio sugerido y decisión comercial. Si no configuras API key, funcionará con reglas internas básicas.")

    context = build_copilot_context(input_data, result)
    st.markdown("**Resumen automático de la OP**")
    st.info(build_executive_summary(result))

    with st.expander("Ver contexto que recibirá la IA"):
        st.json(context)

    api_key = st.text_input("OpenAI API key", value=get_secret("OPENAI_API_KEY", ""), type="password", help="No se guarda en el repositorio. También puedes usar st.secrets o variable de entorno OPENAI_API_KEY.")
    model = st.text_input("Modelo", value=get_secret("OPENAI_MODEL", "gpt-4o-mini"))
    question = st.text_area(
        "Pregunta al copiloto",
        value="Analiza esta cotización y dime si conviene aceptarla, negociarla o recalcularla. Indica los principales riesgos y acciones de mejora.",
        height=120,
    )

    c_ai1, c_ai2 = st.columns(2)
    with c_ai1:
        st.markdown("**Recomendaciones rápidas por reglas**")
        for item in rule_based_recommendations(result):
            st.write("-", item)

    with c_ai2:
        if st.button("Analizar con IA"):
            with st.spinner("Analizando cotización..."):
                answer = analyze_with_ai(question=question, context=context, api_key=api_key.strip() or None, model=model.strip() or None)
                st.markdown(answer)
