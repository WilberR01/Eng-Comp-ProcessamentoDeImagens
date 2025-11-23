import os
import time
from gerenciador import MotorDeAnalise, AnalisadorBase
from models.analysis import AnalysisResult


class SuccessAnalyzer(AnalisadorBase):
    @property
    def nome_modulo(self):
        return "SuccessAnalyzer"

    def processar(self, caminho_imagem: str) -> AnalysisResult:
        # Simula processamento rápido
        return AnalysisResult(detalhe="ok", metrics={"value": 1})


class FailAnalyzer(AnalisadorBase):
    @property
    def nome_modulo(self):
        return "FailAnalyzer"

    def processar(self, caminho_imagem: str) -> AnalysisResult:
        raise RuntimeError("simulated failure")


class TestMotor(MotorDeAnalise):
    def _descobrir_analisadores(self):
        # Instead of scanning subclasses in the environment, inject our test analyzers
        self.analisadores = [SuccessAnalyzer(), FailAnalyzer()]


def test_motor_runs_and_reports_ok_and_error(tmp_path):
    # Create a dummy file path (motor tolerates missing files)
    dummy = tmp_path / "img.jpg"
    dummy.write_text("x")

    m = TestMotor()
    report = m.executar_pipeline(str(dummy))

    assert isinstance(report, dict)
    assert "SuccessAnalyzer" in report
    assert "FailAnalyzer" in report
    assert report["SuccessAnalyzer"]["status"] == "OK"
    assert report["FailAnalyzer"]["status"] == "ERRO"
    assert "simulated failure" in report["FailAnalyzer"]["msg"]
