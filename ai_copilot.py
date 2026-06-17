import json
import os
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


def _money(value: float) -> str:
    return f"S/ {value:,.2f}"


def _pct(value: float) -> str:
    return f"{value:,.2f}%"


def build_copilot_context(input_data: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    """Builds a compact context for the AI copilot without exposing secrets."""
    return {
        "op": {
            "producto": getattr(input_data, "product", ""),
            "cliente": getattr(input_data, "customer", ""),
            "cantidad": result.get("quantity_units", 0),
            "metros_netos": result.get("net_linear_m", 0),
            "metros_totales": result.get("total_linear_m", 0),
            "area_m2": result.get("area_m2", 0),
            "horas_setup": result.get("setup_hours", 0),
            "horas_corrida": result.get("run_hours", 0),
            "horas_maquina_total": result.get("total_machine_hours", 0),
        },
        "costos": {
            "material_directo": result.get("direct_material_cost", 0),
            "maquina": result.get("machine_cost", 0),
            "mano_obra": result.get("direct_labor_cost", 0),
            "acabados": result.get("finishing_cost", 0),
            "cif": result.get("overhead_cost", 0),
            "comercial": result.get("commercial_cost", 0),
            "costo_total": result.get("total_cost", 0),
            "costo_variable": result.get("variable_cost", 0),
            "costo_fijo_op": result.get("fixed_order_cost", 0),
        },
        "pricing": {
            "precio_minimo_contribucion": result.get("minimum_contribution_price", 0),
            "precio_markup": result.get("price_markup_cost", 0),
            "precio_tecnico": result.get("technical_price", 0),
            "precio_estrategico": result.get("strategic_price", 0),
            "precio_con_igv": result.get("price_with_tax", 0),
            "precio_mercado": result.get("market_price", 0),
            "costo_permitido_target": result.get("target_allowed_cost", 0),
            "brecha_target": result.get("target_cost_gap", 0),
        },
        "kpi": {
            "costo_unitario": result.get("unit_cost", 0),
            "precio_unitario": result.get("unit_price", 0),
            "costo_por_millar": result.get("cost_per_thousand", 0),
            "costo_por_metro_lineal": result.get("cost_per_linear_m", 0),
            "costo_por_m2": result.get("cost_per_m2", 0),
            "margen_bruto_pct": result.get("gross_margin_pct", 0),
            "margen_contribucion_pct": result.get("contribution_margin_pct", 0),
            "impacto_setup_unitario": result.get("setup_impact_unit", 0),
            "merma_m": result.get("waste_impact_m", 0),
            "merma_pct_total": result.get("waste_impact_pct_of_total", 0),
        },
    }


def rule_based_recommendations(result: Dict[str, Any]) -> List[str]:
    """Deterministic recommendations when no API key is configured."""
    recs: List[str] = []
    contribution_value = float(result.get("contribution_margin_value", 0) or 0)
    gross_margin = float(result.get("gross_margin_pct", 0) or 0)
    waste_pct = float(result.get("waste_impact_pct_of_total", 0) or 0)
    target_gap = float(result.get("target_cost_gap", 0) or 0)
    market_price = float(result.get("market_price", 0) or 0)
    unit_cost = float(result.get("unit_cost", 0) or 0)
    setup_impact = float(result.get("setup_impact_unit", 0) or 0)

    if contribution_value <= 0:
        recs.append("No aceptar la OP en estas condiciones: el margen de contribución no cubre adecuadamente el costo variable.")
    else:
        recs.append("La OP genera contribución positiva; puede evaluarse comercialmente si no desplaza pedidos más rentables.")

    if gross_margin < 20:
        recs.append("El margen bruto es bajo; revisar descuento, costo de sustrato, merma o tarifa máquina antes de aprobar.")
    elif gross_margin >= 30:
        recs.append("El margen bruto es saludable; controlar consumo real y merma para proteger la rentabilidad.")

    if waste_pct > 10:
        recs.append("La merma es crítica: validar arranque, registro, estabilidad de material, color y tiempo de preparación.")

    if unit_cost and setup_impact / unit_cost > 0.25:
        recs.append("El set up pesa demasiado en el costo unitario; conviene aumentar tiraje, agrupar pedidos o reducir preparación.")

    if market_price and target_gap > 0:
        recs.append("El costo interno supera el costo permitido por mercado; aplicar target costing antes de competir por precio.")

    if not recs:
        recs.append("La cotización no muestra alertas críticas con las reglas actuales.")
    return recs


def build_executive_summary(result: Dict[str, Any]) -> str:
    return (
        f"Precio técnico: {_money(float(result.get('technical_price', 0) or 0))}. "
        f"Costo total: {_money(float(result.get('total_cost', 0) or 0))}. "
        f"Margen bruto: {_pct(float(result.get('gross_margin_pct', 0) or 0))}. "
        f"Costo unitario: {_money(float(result.get('unit_cost', 0) or 0))}. "
        f"Merma total: {float(result.get('waste_impact_m', 0) or 0):,.2f} mL."
    )


def analyze_with_ai(
    question: str,
    context: Dict[str, Any],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """Calls the OpenAI API. If there is no key, returns a local rule-based analysis."""
    key = api_key or os.getenv("OPENAI_API_KEY")
    selected_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not key or OpenAI is None:
        result_like = {
            **context.get("costos", {}),
            **context.get("pricing", {}),
            **context.get("kpi", {}),
        }
        return "\n".join(f"- {item}" for item in rule_based_recommendations(result_like))

    client = OpenAI(api_key=key)
    system_prompt = (
        "Eres un copiloto senior de costos flexográficos. "
        "Tu rol es analizar una cotización de flexografía industrial, explicar los drivers de costo, "
        "detectar riesgos, recomendar precio y decir si conviene aceptar, negociar o rechazar la OP. "
        "No inventes datos. Si falta información, indica 'dato requerido'. "
        "Diferencia margen sobre costo y margen sobre venta. "
        "Responde en español, en tono ejecutivo y accionable."
    )
    user_prompt = {
        "pregunta_usuario": question,
        "contexto_cotizacion": context,
        "formato_salida": [
            "Resumen ejecutivo",
            "Principales drivers de costo",
            "Alertas de rentabilidad",
            "Recomendación de precio",
            "Decisión sugerida: aceptar, negociar, recalcular o rechazar",
            "Acciones de mejora",
        ],
    }

    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or "No se obtuvo respuesta del copiloto IA."
