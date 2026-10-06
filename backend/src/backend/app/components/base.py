import inspect
from typing import Any, ClassVar

from backend.app.components.inputs import BaseInput
from backend.app.components.outputs import Output


class BaseComponent:
    name: ClassVar[str] = ""
    display_name: ClassVar[str] = ""
    category: ClassVar[str] = "General"
    description: ClassVar[str] = ""
    icon: ClassVar[str] = "box"

    inputs: ClassVar[list[BaseInput]] = []
    outputs: ClassVar[list[Output]] = []

    def __init__(self, inputs: dict[str, Any] | None = None):
        self._raw_inputs = inputs or {}

    @classmethod
    def get_name(cls) -> str:
        return cls.name or cls.__name__

    @classmethod
    def get_display_name(cls) -> str:
        return cls.display_name or cls.get_name().replace("Component", "")

    def get_inputs(self) -> dict[str, Any]:
        """Resolves inputs by merging defined defaults with runtime values."""
        resolved = {}
        for inp in self.inputs:
            if inp.name in self._raw_inputs:
                resolved[inp.name] = self._raw_inputs[inp.name]
            else:
                resolved[inp.name] = inp.default
        return resolved

    @classmethod
    def get_schema(cls) -> dict[str, Any]:
        """Serializes component definition to JSON schema dictionary."""
        return {
            "name": cls.get_name(),
            "displayName": cls.get_display_name(),
            "category": cls.category,
            "description": cls.description,
            "icon": cls.icon,
            "inputs": [inp.to_dict() for inp in cls.inputs],
            "outputs": [out.to_dict() for out in cls.outputs],
        }

    async def execute(self, method_name: str | None = None) -> Any:
        """Executes designated output method or default execute."""
        target_name = method_name
        if not target_name:
            if self.outputs:
                target_name = self.outputs[0].method
            else:
                target_name = "run"

        method = getattr(self, target_name, None)
        if not method:
            raise AttributeError(
                f"Component '{self.get_name()}' does not implement method '{target_name}'"
            )

        if inspect.iscoroutinefunction(method):
            return await method()
        return method()
