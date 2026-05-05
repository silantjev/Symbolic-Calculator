from typing import Annotated
import secrets
import sys
from pathlib import Path
from tokenize import TokenError

from fastapi import FastAPI, Form, Response, Cookie
from fastapi.responses import HTMLResponse

FILEDIR = Path(__file__).resolve().parent
ROOT = FILEDIR.parent
sys.path.insert(0, str(ROOT))

from web_app.app_utils import HtmlGenetator, Sessions

html_gen = HtmlGenetator(
        template_path=FILEDIR / 'template.html',
        error_template_path=FILEDIR / 'error.html',
        info_template_path=FILEDIR / 'info.html',
    )
sess = Sessions()
app = FastAPI()

@app.on_event("shutdown")
def shutdown_event():
    sess.save()

@app.get("/symcalc", response_class=HTMLResponse)
def start(response: Response):
    uu_id = sess.UUID_THRESHOLD + secrets.randbits(32)
    calc = sess.get_calc(uu_id)
    response.set_cookie(key="session_uuid", value=uu_id, httponly=True)
    return html_gen.get_html(calc)

css_path = FILEDIR / "template.css"
assert css_path.is_file()
css_content = css_path.read_text(encoding="utf-8")

@app.get("/template.css")
async def get_css():
    return Response(content=css_content, media_type="text/css")

def _set_new_expression(calc, expr):
    try:
        error = calc.set_new_expr(expr)
    except (SyntaxError, TokenError) as exc:
        calc.logger.error("TokenError: %s", exc)
        return html_gen.show_error(expr=expr, error=f"Синтаксическая ошибка: {exc}")
    
    if error:
        calc.logger.error("Error: %s", error)
        return html_gen.show_error(expr=expr, error=error)

    calc.sec = calc.evaluate()

    return html_gen.get_html(calc)


@app.post("/symcalc/set_new_expr", response_class=HTMLResponse)
def set_new_expr(expr: str = Form(...), session_uuid: Annotated[int, Cookie()] = 0):
    calc = sess.get_calc(session_uuid)
    calc.expr = expr
    return _set_new_expression(calc, expr)

@app.post("/symcalc/process_se", response_class=HTMLResponse)
def precess_se(
        se: str = Form(...),
        action: str = Form(...),
        session_uuid: Annotated[int, Cookie()] = 0,
    ):
    calc = sess.get_calc(session_uuid)
    match action:
        case "evaluate":
            return _set_new_expression(calc, se)
        case "se_up": #Перебросить se -> expr
            calc.se = se
            calc.expr = calc.get_nice()
            return html_gen.get_html(calc)
        case _:
            raise ValueError(f"Wrong action '{action}'")


@app.post("/symcalc/up", response_class=HTMLResponse)
def up(sec: str = Form(...), session_uuid: Annotated[int, Cookie()] = 0):
    calc = sess.get_calc(session_uuid)
    #Перебросить sec -> se
    calc.sec = sec
    calc.se = sec

    return html_gen.get_html(calc)

@app.post("/symcalc/clear_all", response_class=HTMLResponse)
def clear_all(session_uuid: Annotated[int, Cookie()] = 0):
    calc = sess.get_calc(session_uuid)
    calc.clear_all()
    return html_gen.get_html(calc)

@app.get('/symcalc/info', response_class=HTMLResponse)
def show_info_text(session_uuid: Annotated[int, Cookie()] = 0):
    calc = sess.get_calc(session_uuid)
    return html_gen.show_info(calc)

@app.get("/symcalc/{uu_id}", response_class=HTMLResponse)
def start_with_uu_id(uu_id: int, response: Response):
    calc = sess.get_calc(uu_id)
    response.set_cookie(key="session_uuid", value=uu_id, httponly=True)
    return html_gen.get_html(calc)


"""
@app.get("/symcalc/current_values")
def current_values() -> Expression:
    subs_string = calc.current_values()
    return Expression(expr=subs_string)

@app.get("/symcalc/get_variables")
def get_variables(include_unset: bool) -> GetVariablesOutput:
    current, lines = calc.get_variables(include_unset=include_unset)
    return GetVariablesOutput(current=current, lines=lines)

@app.put("/symcalc/put_state")
def put_state(data: FullState) -> State:
    try:
        calc.set_expr(data.expr)
        calc.set_se(data.se) # May throw exception
        calc.set_sec(data.sec)
        for k, v in data.values.items():
            calc.set_value(k, v) # May throw exception
        for k, v in data.options.items():
            calc.set_option(k, v)
    except (SyntaxError, TokenError) as exc:
        calc.logger.error("TokenError: %s", exc)
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={"Error": "Синтаксическая ошибка"}
        )

    return read_state(calc)

@app.post("/symcalc/save_state")
def save_state(session_id: int):
    state_manager.save_state(calc, session_id=session_id)
    return JSONResponse(content={"status": "ok"}, status_code=200)

@app.delete("/symcalc/delete_all_values")
def delete_all_values() -> State:
    calc.delete_all_values()
    
    return read_state(calc)

@app.delete("/symcalc/delete_value")
def delete_value(var: str) -> State:
    calc.delete_value(var)
    
    return read_state(calc)

"""


if __name__ == "__main__":
    import uvicorn 
    uvicorn.run("web_application:app", reload=True)
