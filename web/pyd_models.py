from typing import Optional, Dict, Set, List
from pydantic import BaseModel

class Expression(BaseModel):
    expr: str


class GetVariablesOutput(BaseModel):
    current : Set[str]
    lines : List[str]

class State(BaseModel):
    nice: str
    expr: str
    se: str
    sec: str
    values: Dict[str, str]
    options: Dict[str, int]


class FullState(State):
    explanations: Optional[Dict[str, str]] = None
    help_text: Optional[str] = None


def read_state(calc, state_model=State):
    state = state_model(
                nice=calc.get_nice(),
                expr=calc.expr,
                se=str(calc.se),
                sec=str(calc.sec),
                values={k : str(v) for k, v in calc.values.items()},
                options=calc.options,
            )

    return state
