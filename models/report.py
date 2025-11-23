from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .analysis import AnalysisResult


@dataclass
class ResultItem:
    module: str
    status: str  # e.g. 'OK' ou 'ERRO'
    dados: Optional[AnalysisResult] = None
    msg: Optional[str] = None
    time_taken: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"status": self.status}
        if self.dados is not None:
            try:
                out["dados"] = self.dados.to_dict()
            except Exception:
                out["dados"] = self.dados
        if self.msg is not None:
            out["msg"] = self.msg
        if self.time_taken is not None:
            out["time_taken"] = round(self.time_taken, 3)
        return out


@dataclass
class ConsolidatedReport:
    items: Dict[str, ResultItem] = field(default_factory=dict)

    def add(self, item: ResultItem) -> None:
        self.items[item.module] = item

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        return {k: v.to_dict() for k, v in self.items.items()}

    def __iter__(self):
        return iter(self.items.items())
