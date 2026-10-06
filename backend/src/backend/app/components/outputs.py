from typing import Any


class Output:
    def __init__(
        self,
        name: str,
        label: str | None = None,
        type: str = "any",
        method: str = "execute",
        description: str | None = None,
    ):
        self.name = name
        self.label = label or name.replace("_", " ").title()
        self.type = type
        self.method = method
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "type": self.type,
            "method": self.method,
            "description": self.description,
        }
