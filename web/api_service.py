import os
import sys
from pathlib import Path
from tokenize import TokenError

import fastapi
from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.calculator import Calculator
from core.logger import make_logger
from core.session_storage import JSONStorage, StateManager
from web.pyd_models import Expression, GetVariablesOutput, State, FullState, read_state


console_logging = os.environ.get("CONSOLE_LOGGING", "yes")
file_logging = os.environ.get("FILE_LOGGING", "yes")
log_console = (console_logging != "no")
log_file = (file_logging != "no")

conf_path = os.environ.get("CONF_PATH", "")

logger = make_logger(name="web", console=log_console, file=log_file)
calc = Calculator(logger=logger)
storage = JSONStorage(logger=logger, json_path=conf_path)
state_manager = StateManager(storage)

state_manager.load_state(calc)

app = FastAPI()

@app.on_event("shutdown")
def shutdown_event():
    state_manager.save_state(calc)

@app.get("/calc/get_state")
def get_state(full: bool) -> FullState:
    state = read_state(calc, state_model=FullState)
    if full:
        state.explanations = calc.explanations
        state.help_text = calc.help_text
    return state


@app.get("/calc/evaluate")
def evaluate() -> Expression:
    sec = calc.evaluate()
    return Expression(expr=str(sec))

@app.get("/calc/current_values")
def current_values() -> Expression:
    subs_string = calc.current_values()
    return Expression(expr=subs_string)

@app.get("/calc/get_variables")
def get_variables(include_unset: bool) -> GetVariablesOutput:
    current, lines = calc.get_variables(include_unset=include_unset)
    return GetVariablesOutput(current=current, lines=lines)

@app.put("/calc/put_state")
def put_state(data: FullState) -> State:
    try:
        calc.set_expr(data.expr)
        calc.set_se(data.se) # May throw esception
        calc.set_sec(data.sec)
        for k, v in data.values.items():
            calc.set_value(k, v) # May throw esception
        for k, v in data.options.items():
            calc.set_option(k, v)
    except (SyntaxError, TokenError) as exc:
        calc.logger.error("TokenError: %s", exc)
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={"Error": "Синтактическая ошибка"}
        )

    return read_state(calc)

@app.post("/calc/set_new_expr")
def set_new_expr(data: Expression) -> State:

    try:
        error = calc.set_new_expr(data.expr)
    except (SyntaxError, TokenError) as exc:
        calc.logger.error("TokenError: %s", exc)
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={"Error": "Синтактическая ошибка"}
        )
    
    if error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={"Error": error}
        )
    
    return read_state(calc)

@app.post("/calc/save_state")
def save_state(session_id: int) -> None:
    state_manager.save_state(calc, session_id=session_id)

@app.delete("/calc/delete_all_values")
def delete_all_values() -> State:
    calc.delete_all_values()
    
    return read_state(calc)

@app.delete("/calc/delete_value")
def delete_value(var: str) -> State:
    calc.delete_value(var)
    
    return read_state(calc)

@app.delete("/calc/clear_all")
def clear_all() -> State:
    calc.clear_all()
    return read_state(calc)

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run("api_service:app", reload=True)
