from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AnalysisResult:

    detalhe: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = field(default_factory=dict)
    extra: Optional[Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        if self.detalhe is not None:
            out["detalhe"] = self.detalhe
        if self.metrics:
            out["metrics"] = self.metrics
        if self.extra:
            out["extra"] = self.extra
        return out
