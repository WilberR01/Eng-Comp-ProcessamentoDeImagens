from typing import Any, Dict
from gerenciador import MotorDeAnalise
from services.error_handler import format_exception


def run_analysis(caminho_imagem: str) -> Dict[str, Any]:
    engine = MotorDeAnalise()
    try:
        report = engine.executar_pipeline(caminho_imagem)
        return {"success": True, "report": report}
    except Exception as e:
        err = format_exception(e)
        return {"success": False, "error": err}
