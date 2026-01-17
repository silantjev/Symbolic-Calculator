import re
import os
import sys
from pathlib import Path
from tokenize import TokenError

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

FILEDIR = Path(__file__).resolve().parent
ROOT = FILEDIR.parent
sys.path.insert(0, str(ROOT))

from core.calculator import Calculator
from core.logger import make_logger
from core.session_storage import JSONStorage, StateManager


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

class HtmlGenetator:
    def __init__(self, template_path, error_template_path, info_template_path):
        assert template_path.is_file(), f'File {template_path} not found'
        assert error_template_path.is_file(), f'File {error_template_path} not found'
        assert info_template_path.is_file(), f'File {error_template_path} not found'
        with open(template_path, 'r', encoding='utf8') as f:
            self.template = f.read()
        with open(error_template_path, 'r', encoding='utf8') as f:
            self.error_template = f.read()
        with open(info_template_path, 'r', encoding='utf8') as f:
            self.info_template = f.read()
        self.url_reg_expr = re.compile(r'(https?://[\w\-./]+)')

    def get_html(self, calc):
        return self.template.format(
                expr=calc.expr,
                se=calc.get_nice(),
                sec=str(calc.sec),
            )

    def show_error(self, expr, error):
        return self.error_template.format(
                expr=expr,
                error=error,
            )

    def show_info(self, calc):
        html_text = self.info_template.format(text=calc.get_help_text())
        return re.sub(self.url_reg_expr, r'<a href="\1">\1</a>', html_text)

html_gen = HtmlGenetator(
        template_path=FILEDIR / 'template.html',
        error_template_path=FILEDIR / 'error.html',
        info_template_path=FILEDIR / 'info.html',
    )
app = FastAPI()

@app.on_event("shutdown")
def shutdown_event():
    state_manager.save_state(calc)

@app.get("/symcalc", response_class=HTMLResponse)
def start():
    return html_gen.get_html(calc)

def _set_new_expression(expr):
    try:
        error = calc.set_new_expr(expr)
    except (SyntaxError, TokenError) as exc:
        calc.logger.error("TokenError: %s", exc)
        return html_gen.show_error(expr=expr, error=f"Синтактическая ошибка: {exc}")
    
    if error:
        calc.logger.error("Error: %s", error)
        return html_gen.show_error(expr=expr, error=error)

    calc.sec = calc.evaluate()

    return html_gen.get_html(calc)


@app.post("/symcalc/set_new_expr", response_class=HTMLResponse)
def set_new_expr(expr: str = Form(...)):
    calc.expr = expr
    return _set_new_expression(expr)

@app.post("/symcalc/process_se", response_class=HTMLResponse)
def precess_se(
        se: str = Form(...),
        action: str = Form(...),
    ):
    if action == "evaluate":
        return _set_new_expression(se)
    #Перебросить se -> expr
    calc.se = se
    calc.expr = calc.get_nice()
    return html_gen.get_html(calc)


@app.post("/symcalc/up", response_class=HTMLResponse)
def up(sec: str = Form(...)):
    #Перебросить sec -> se
    calc.sec = sec
    calc.se = sec

    return html_gen.get_html(calc)

@app.post("/symcalc/clear_all", response_class=HTMLResponse)
def clear_all():
    calc.clear_all()
    return html_gen.get_html(calc)

@app.get('/symcalc/info', response_class=HTMLResponse)
def show_info_text():
    return html_gen.show_info(calc)

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
