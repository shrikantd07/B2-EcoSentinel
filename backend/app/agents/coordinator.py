from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class EcoState(TypedDict, total=False):
    area: str

    air_input: dict
    water_input: dict
    waste_input: dict

    air_report: dict
    water_report: dict
    waste_report: dict

    final_report: dict


def air_node(state: EcoState):
    from .air_agent import analyze_air

    result = analyze_air(state["air_input"]["aqi"])

    return {
        "air_report": result
    }


def water_node(state: EcoState):
    from .water_agent import analyze_water

    data = state["water_input"]

    result = analyze_water(
        data["ph"],
        data["dissolved_oxygen"],
        data["turbidity"],
    )

    return {
        "water_report": result
    }


def waste_node(state: EcoState):
    from .waste_agent import analyze_waste

    data = state["waste_input"]

    result = analyze_waste(
        data["litter_count"],
        data["severe_litter"],
    )

    return {
        "waste_report": result
    }


def coordinator_node(state: EcoState):
    air = state["air_report"]
    water = state["water_report"]
    waste = state["waste_report"]

    reports = [air, water, waste]

    scores = [
        report["score"]
        for report in reports
    ]

    average_score = sum(scores) / len(scores)

    if average_score >= 70:
        overall_risk = "HIGH"
    elif average_score >= 40:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    contributors = [
        report["agent"]
        for report in reports
        if report["risk_level"] == "HIGH"
    ]

    reasoning = (
        f"Combined environmental risk is {overall_risk}. "
        f"Specialist agents evaluated air, water, and waste signals. "
        f"The strongest contributing signal(s) are: "
        f"{', '.join(contributors) if contributors else 'none'}."
    )

    coordinator_report = {
        "score": round(average_score, 2),
        "risk_level": overall_risk,
        "reasoning": reasoning,
        "contributors": contributors,
    }

    final_report = {
        "area": state["area"],
        "overall_risk": overall_risk,
        "air": air,
        "water": water,
        "waste": waste,
        "coordinator": coordinator_report,
    }

    return {
        "final_report": final_report
    }


def build_graph():
    graph = StateGraph(EcoState)

    graph.add_node("air_agent", air_node)
    graph.add_node("water_agent", water_node)
    graph.add_node("waste_agent", waste_node)
    graph.add_node("coordinator", coordinator_node)

    graph.add_edge(START, "air_agent")
    graph.add_edge(START, "water_agent")
    graph.add_edge(START, "waste_agent")

    graph.add_edge("air_agent", "coordinator")
    graph.add_edge("water_agent", "coordinator")
    graph.add_edge("waste_agent", "coordinator")

    graph.add_edge("coordinator", END)

    return graph.compile()


eco_graph = build_graph()