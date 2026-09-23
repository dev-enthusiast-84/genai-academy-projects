"""Execution graph after the durable, application-owned human approval boundary."""
from typing import Callable, TypedDict

from langgraph.graph import END, START, StateGraph


class ExecutionState(TypedDict):
    request_id: str
    interrupted: bool


def execute_with_audit(engine, user, request_id, audit: Callable[[str], None], stop_after=None):
    """Resume via Engine's saved approval/retries, never through a model write tool.

    The callback performs independent verification and (in live mode) model audit.
    No graph checkpoint duplicates Engine's authoritative persisted request state.
    """
    def execute(state):
        req = engine.delete_approved_records(state['request_id'], user, stop_after=stop_after)
        return {'interrupted': req['status'] == 'interrupted'}

    def verify_and_audit(state):
        audit(state['request_id'])
        return {}

    graph = StateGraph(ExecutionState)
    graph.add_node('execute_approved_scope', execute)
    graph.add_node('verify_and_audit', verify_and_audit)
    graph.add_edge(START, 'execute_approved_scope')
    graph.add_conditional_edges('execute_approved_scope',
                                lambda state: END if state['interrupted'] else 'verify_and_audit',
                                [END, 'verify_and_audit'])
    graph.add_edge('verify_and_audit', END)
    graph.compile().invoke({'request_id': request_id, 'interrupted': False})
    return engine.get_request(request_id, user)
