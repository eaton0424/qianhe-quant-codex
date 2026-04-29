from dataclasses import dataclass, field


def _normalize_items(items: list[str]) -> list[str]:
    normalized: list[str] = []
    for item in items:
        text = str(item).strip()
        if text and text not in normalized:
            normalized.append(text)
    return normalized


@dataclass(frozen=True)
class StockProfile:
    stock_code: str
    stock_name: str
    industry: str = "TO_VERIFY"
    theme_tags: list[str] = field(default_factory=list)
    facts: list[str] = field(default_factory=list)
    opinions: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    verification_tasks: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "stock_code", str(self.stock_code).strip() or "TO_VERIFY")
        object.__setattr__(self, "stock_name", str(self.stock_name).strip() or "TO_VERIFY")
        object.__setattr__(self, "industry", str(self.industry).strip() or "TO_VERIFY")
        object.__setattr__(self, "theme_tags", _normalize_items(self.theme_tags))
        object.__setattr__(self, "facts", _normalize_items(self.facts))
        object.__setattr__(self, "opinions", _normalize_items(self.opinions))
        object.__setattr__(self, "assumptions", _normalize_items(self.assumptions))
        object.__setattr__(self, "risks", _normalize_items(self.risks))
        object.__setattr__(self, "verification_tasks", _normalize_items(self.verification_tasks))

    def as_dict(self) -> dict:
        return {
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "industry": self.industry,
            "theme_tags": self.theme_tags,
            "facts": self.facts,
            "opinions": self.opinions,
            "assumptions": self.assumptions,
            "risks": self.risks,
            "verification_tasks": self.verification_tasks,
        }
