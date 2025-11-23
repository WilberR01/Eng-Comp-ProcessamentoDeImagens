import math
from models.analysis import AnalysisResult
from models.report import ResultItem, ConsolidatedReport


def test_analysis_result_to_dict():
    ar = AnalysisResult(detalhe="ok", metrics={"score": 0.9876}, extra={"foo": "bar"})
    d = ar.to_dict()
    assert d["detalhe"] == "ok"
    assert math.isclose(d["metrics"]["score"], 0.9876)
    assert d["extra"]["foo"] == "bar"


def test_result_item_serialization_and_consolidation():
    ar = AnalysisResult(detalhe="done", metrics={"n": 5})
    item = ResultItem(module="mod1", status="OK", dados=ar, time_taken=0.12345)
    d = item.to_dict()
    assert d["status"] == "OK"
    assert d["dados"]["detalhe"] == "done"
    # time_taken rounded to 3 decimals
    assert d["time_taken"] == round(0.12345, 3)

    cr = ConsolidatedReport()
    cr.add(item)
    assert "mod1" in cr.to_dict()
