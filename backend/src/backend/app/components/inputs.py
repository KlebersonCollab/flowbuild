from typing import Any


class BaseInput:
    input_type: str = "any"

    def __init__(
        self,
        name: str,
        label: str | None = None,
        required: bool = False,
        default: Any = None,
        placeholder: str | None = None,
        is_handle: bool = True,
        description: str | None = None,
    ):
        self.name = name
        self.label = label or name.replace("_", " ").title()
        self.required = required
        self.default = default
        self.placeholder = placeholder
        self.is_handle = is_handle
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.input_type,
            "label": self.label,
            "required": self.required,
            "default": self.default,
            "placeholder": self.placeholder,
            "is_handle": self.is_handle,
            "description": self.description,
        }


class StrInput(BaseInput):
    input_type = "str"


class IntInput(BaseInput):
    input_type = "int"


class FloatInput(BaseInput):
    input_type = "float"


class BoolInput(BaseInput):
    input_type = "bool"

    def __init__(
        self,
        name: str,
        label: str | None = None,
        required: bool = False,
        default: bool = False,
        placeholder: str | None = None,
        is_handle: bool = True,
        description: str | None = None,
    ):
        super().__init__(
            name=name,
            label=label,
            required=required,
            default=default,
            placeholder=placeholder,
            is_handle=is_handle,
            description=description,
        )


class SelectInput(BaseInput):
    input_type = "select"

    def __init__(
        self,
        name: str,
        options: list[str],
        label: str | None = None,
        required: bool = False,
        default: Any = None,
        placeholder: str | None = None,
        is_handle: bool = True,
        description: str | None = None,
    ):
        super().__init__(
            name=name,
            label=label,
            required=required,
            default=default or (options[0] if options else None),
            placeholder=placeholder,
            is_handle=is_handle,
            description=description,
        )
        self.options = options

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["options"] = self.options
        return data


class DictInput(BaseInput):
    input_type = "dict"


class CodeInput(BaseInput):
    input_type = "code"

    def __init__(
        self,
        name: str,
        label: str | None = None,
        language: str = "python",
        required: bool = False,
        default: str = "",
        placeholder: str | None = None,
        is_handle: bool = True,
        description: str | None = None,
    ):
        super().__init__(
            name=name,
            label=label,
            required=required,
            default=default,
            placeholder=placeholder,
            is_handle=is_handle,
            description=description,
        )
        self.language = language

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["language"] = self.language
        return data
