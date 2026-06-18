from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class FlexoEstimateInput:
    product: str
    customer: str
    quantity_units: float
    advance_m: float
    lanes: int
    web_width_m: float
    substrate_cost_per_m2: float
    ink_consumption_g_m2: float
    ink_cost_per_kg: float
    varnish_consumption_g_m2: float
    varnish_cost_per_kg: float
    startup_waste_m: float
    run_waste_pct: float
    machine_speed_ml_h: float
    setup_hours: float
    machine_rate_h: float
    labor_rate_h: float
    labor_hours_extra: float
    plate_cost: float
    prepress_cost: float
    die_cut_cost: float
    rewind_cost: float
    packing_cost: float
    overhead_pct: float
    admin_sales_pct: float
    commission_pct: float
    freight_cost: float
    finance_pct: float
    markup_on_cost_pct: float
    margin_on_sales_pct: float
    minimum_contribution_pct: float
    strategic_value_premium_pct: float
    market_price: float
    tax_pct: float


def safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def pct(value: float) -> float:
    return value / 100.0


def estimate_flexo_cost(data: FlexoEstimateInput) -> Dict[str, float]:
    """Calcula costo técnico y precios de venta para una OP flexográfica."""
    lanes = max(int(data.lanes), 1)
    quantity = max(data.quantity_units, 0)

    net_linear_m = safe_div(quantity * data.advance_m, lanes)
    run_waste_m = net_linear_m * pct(data.run_waste_pct)
    total_linear_m = net_linear_m + data.startup_waste_m + run_waste_m
    area_m2 = total_linear_m * data.web_width_m

    substrate_cost = area_m2 * data.substrate_cost_per_m2
    ink_cost = area_m2 * data.ink_consumption_g_m2 * data.ink_cost_per_kg / 1000
    varnish_cost = area_m2 * data.varnish_consumption_g_m2 * data.varnish_cost_per_kg / 1000

    run_hours = safe_div(total_linear_m, data.machine_speed_ml_h)
    total_machine_hours = data.setup_hours + run_hours
    machine_cost = total_machine_hours * data.machine_rate_h
    setup_machine_cost = data.setup_hours * data.machine_rate_h
    run_machine_cost = run_hours * data.machine_rate_h

    direct_labor_cost = (total_machine_hours + data.labor_hours_extra) * data.labor_rate_h
    direct_material_cost = substrate_cost + ink_cost + varnish_cost
    fixed_order_cost = data.plate_cost + data.prepress_cost + setup_machine_cost
    finishing_cost = data.die_cut_cost + data.rewind_cost + data.packing_cost

    manufacturing_base = direct_material_cost + machine_cost + direct_labor_cost + data.plate_cost + data.prepress_cost + finishing_cost
    overhead_cost = manufacturing_base * pct(data.overhead_pct)
    manufacturing_cost = manufacturing_base + overhead_cost

    admin_sales_cost = manufacturing_cost * pct(data.admin_sales_pct)
    commission_cost = manufacturing_cost * pct(data.commission_pct)
    finance_cost = manufacturing_cost * pct(data.finance_pct)
    commercial_cost = admin_sales_cost + commission_cost + data.freight_cost + finance_cost
    total_cost = manufacturing_cost + commercial_cost

    price_markup_cost = total_cost * (1 + pct(data.markup_on_cost_pct))
    price_margin_sales = safe_div(total_cost, 1 - pct(data.margin_on_sales_pct))

    variable_cost = direct_material_cost + run_machine_cost + (run_hours * data.labor_rate_h) + data.freight_cost
    minimum_contribution_price = variable_cost * (1 + pct(data.minimum_contribution_pct)) + fixed_order_cost

    technical_price = price_margin_sales
    strategic_price = technical_price * (1 + pct(data.strategic_value_premium_pct))
    tax_amount = technical_price * pct(data.tax_pct)
    price_with_tax = technical_price + tax_amount

    target_allowed_cost = data.market_price * (1 - pct(data.margin_on_sales_pct)) if data.market_price else 0
    target_cost_gap = total_cost - target_allowed_cost if data.market_price else 0

    gross_margin_value = technical_price - manufacturing_cost
    contribution_margin_value = technical_price - variable_cost

    return {
        "quantity_units": quantity,
        "net_linear_m": net_linear_m,
        "startup_waste_m": data.startup_waste_m,
        "run_waste_m": run_waste_m,
        "total_linear_m": total_linear_m,
        "area_m2": area_m2,
        "run_hours": run_hours,
        "setup_hours": data.setup_hours,
        "total_machine_hours": total_machine_hours,
        "substrate_cost": substrate_cost,
        "ink_cost": ink_cost,
        "varnish_cost": varnish_cost,
        "direct_material_cost": direct_material_cost,
        "setup_machine_cost": setup_machine_cost,
        "run_machine_cost": run_machine_cost,
        "machine_cost": machine_cost,
        "direct_labor_cost": direct_labor_cost,
        "plate_cost": data.plate_cost,
        "prepress_cost": data.prepress_cost,
        "finishing_cost": finishing_cost,
        "overhead_cost": overhead_cost,
        "manufacturing_cost": manufacturing_cost,
        "admin_sales_cost": admin_sales_cost,
        "commission_cost": commission_cost,
        "freight_cost": data.freight_cost,
        "finance_cost": finance_cost,
        "commercial_cost": commercial_cost,
        "total_cost": total_cost,
        "variable_cost": variable_cost,
        "fixed_order_cost": fixed_order_cost,
        "price_markup_cost": price_markup_cost,
        "price_margin_sales": price_margin_sales,
        "minimum_contribution_price": minimum_contribution_price,
        "technical_price": technical_price,
        "strategic_price": strategic_price,
        "tax_amount": tax_amount,
        "price_with_tax": price_with_tax,
        "market_price": data.market_price,
        "target_allowed_cost": target_allowed_cost,
        "target_cost_gap": target_cost_gap,
        "unit_cost": safe_div(total_cost, quantity),
        "unit_price": safe_div(technical_price, quantity),
        "cost_per_thousand": safe_div(total_cost, quantity) * 1000,
        "price_per_thousand": safe_div(technical_price, quantity) * 1000,
        "cost_per_linear_m": safe_div(total_cost, total_linear_m),
        "price_per_linear_m": safe_div(technical_price, total_linear_m),
        "cost_per_m2": safe_div(total_cost, area_m2),
        "price_per_m2": safe_div(technical_price, area_m2),
        "gross_margin_value": gross_margin_value,
        "gross_margin_pct": safe_div(gross_margin_value, technical_price) * 100,
        "contribution_margin_value": contribution_margin_value,
        "contribution_margin_pct": safe_div(contribution_margin_value, technical_price) * 100,
        "setup_impact_unit": safe_div(fixed_order_cost, quantity),
        "waste_impact_m": data.startup_waste_m + run_waste_m,
        "waste_impact_pct_of_total": safe_div(data.startup_waste_m + run_waste_m, total_linear_m) * 100,
    }


def build_sensitivity(data: FlexoEstimateInput) -> List[Dict[str, float]]:
    scenarios = [
        ("Base", {}),
        ("Conservador: material +10% y merma +3 pp", {"substrate_cost_per_m2": data.substrate_cost_per_m2 * 1.10, "run_waste_pct": data.run_waste_pct + 3}),
        ("Optimista: velocidad +15% y set up -20%", {"machine_speed_ml_h": data.machine_speed_ml_h * 1.15, "setup_hours": data.setup_hours * 0.80}),
        ("Descuento comercial: margen venta -5 pp", {"margin_on_sales_pct": max(data.margin_on_sales_pct - 5, 0)}),
        ("Tiraje +50%", {"quantity_units": data.quantity_units * 1.50}),
        ("Tiraje -30%", {"quantity_units": data.quantity_units * 0.70}),
        ("Mayor complejidad: set up +30%", {"setup_hours": data.setup_hours * 1.30}),
    ]

    rows: List[Dict[str, float]] = []
    base_dict = asdict(data)
    for name, changes in scenarios:
        scenario_dict = {**base_dict, **changes}
        result = estimate_flexo_cost(FlexoEstimateInput(**scenario_dict))
        rows.append({
            "escenario": name,
            "costo_total": result["total_cost"],
            "precio_tecnico": result["technical_price"],
            "precio_estrategico": result["strategic_price"],
            "costo_unitario": result["unit_cost"],
            "precio_unitario": result["unit_price"],
            "margen_bruto_pct": result["gross_margin_pct"],
            "metros_totales": result["total_linear_m"],
            "horas_maquina": result["total_machine_hours"],
        })
    return rows
