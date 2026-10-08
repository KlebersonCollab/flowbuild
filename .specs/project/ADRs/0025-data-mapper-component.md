# ADR 0025: Declarative Data Mapper Component for Record Transformation

## Status
Accepted

## Date
2026-10-07

## Context
In automation workflows, data received from external webhooks, databases, or third-party APIs rarely matches the schema expected by downstream services. Developers often need to rename fields, restructure nested objects, pick specific properties, or reshape entire arrays of records.

Currently, users must resort to writing custom Python code in `PythonScriptComponent` or complex expressions in `JsonTransformComponent` for routine field mapping and renaming tasks.

A dedicated `DataMapperComponent` provides a declarative, visual way to reshape records and collections using dot-notation path extraction (`data.user.id`), field renaming, optional unmapped field passthrough, and item list handling.

## Decision
1. **Component Design (`DataMapperComponent`)**:
   - Class name: `DataMapperComponent`
   - Display name: `"Data Mapper"`
   - Category: `"Transform"`
   - Description: `"Transforms, renames, and restructures objects or collections using declarative field mappings."`
   - Icon: `"arrow-right-left"`
2. **Inputs**:
   - `input_data` (`DictInput` / `BaseInput`, required=True, default={}): Source object or array of objects to transform.
   - `mapping` (`DictInput`, required=True, default={}): Dictionary where keys are destination field names and values are source dot-notation paths (e.g. `{"id": "user.id", "email": "contact.email"}`).
   - `items_path` (`StrInput`, default=""): Optional dot-notation path to extract a nested list of items before mapping (e.g., `"items"` or `"data.users"`).
   - `pass_unmapped` (`BoolInput`, default=False): If True, preserves source fields not explicitly overridden in `mapping`.
   - `mode` (`SelectInput`, options=`["auto", "single", "array"]`, default=`"auto"`): Processing mode. `"auto"` detects whether data is a single record or collection.
3. **Outputs**:
   - `output_data` (`Output`, type="any"): The mapped dictionary or list of mapped dictionaries.
   - `mapped_count` (`Output`, type="int"): Total number of records successfully transformed.
4. **Execution Semantics & Resilience**:
   - Path resolution supports dot notation (`a.b.c`) and numerical array indexing (`items.0.name`).
   - If a source path does not exist, `None` (or fallback) is assigned without throwing an unhandled exception.
   - When `items_path` is specified, the component traverses into the nested collection, transforms each item, and outputs the resulting list.
   - Fully deterministic and pure execution.
5. **Frontend Canvas & Palette Integration**:
   - Map `mapper` in `ComponentPalette.vue` and `CustomNode.vue` to `ArrowRightLeft` icon with Emerald Transform styling (`text-emerald-400 bg-emerald-500/10 border-emerald-500/30`).

## Consequences
- **Positive**: Declarative, visual data mapping without writing custom Python code.
- **Completeness**: Solves common schema mismatch problems between APIs, databases, and notification services.
- **Safety**: Safe traversal with null-safety and 0 unhandled exceptions on missing fields.
- **Backwards Compatibility**: 100% additive; no breaking changes.
