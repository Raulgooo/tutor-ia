from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy

from app.schemas import TutorState
from app.nodes import (
    pre_analysis_node,
    route_after_pre_analysis,
    tutor_node,
    negative_node,
    post_analysis_node,
    route_after_post_analysis,
)

flow = StateGraph(TutorState)
# Solo añadi retry policy en el nodo tutor por que es el mas critico y no quiero meter mas politicas por ahora.
flow.add_node("pre_analysis", pre_analysis_node)
flow.add_node("tutor", tutor_node, retry=RetryPolicy(max_attempts=2))
flow.add_node("negative_feedback", negative_node)
flow.add_node("post_analysis", post_analysis_node)

flow.add_edge(START, "pre_analysis")

flow.add_conditional_edges(
    "pre_analysis",
    route_after_pre_analysis,
    {
        "is_cheat": "negative_feedback",
        "is_safe": "tutor"              
    }
)

flow.add_edge("tutor", "post_analysis")

flow.add_conditional_edges(
    "post_analysis",
    route_after_post_analysis,
    {
        "end_valid": END,                
        "end_invalid": "negative_feedback"
    }
)


flow.add_edge("negative_feedback", END)

graph = flow.compile()
