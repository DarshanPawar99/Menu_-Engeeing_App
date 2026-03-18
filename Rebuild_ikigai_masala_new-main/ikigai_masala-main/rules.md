"""
Project Rules for Implementing New Features (Codex Guidance)
"""

# Rules for Implementing Features

This document captures the project-level expectations for adding or modifying features, especially **menu rules**.

## 1) When You Add a New Rule

Follow this checklist:

1. **Create a rule class**
   - Add a new file in `src/menu_rules/` (e.g., `color_pairing_menu_rule.py`).
   - Implement `validate_config()` and `apply()` methods.

2. **Register the rule**
   - Add the new rule type in `src/menu_rules/base_menu_rule.py` under `MenuRuleType`.
   - Add the new rule class to `src/menu_rules/menu_rule_loader.py` in `RULE_CLASSES`.
   - Export the rule class from `src/menu_rules/__init__.py`.

3. **Support data requirements**
   - If the rule relies on new fields (columns like `item_color`), update:
     - `src/preprocessor/excel_reader.py` (schema validation)
     - `src/preprocessor/data_cleanser.py` (cleaning + defaults)
     - `src/preprocessor/data_serializer.py` if metadata expectations change

4. **Add tests**
   - Create a **dedicated test file** for the rule, e.g.:
     - `tests/test_<rule_name>.py`
   - Include both positive and negative scenarios.
   - Ensure the test exercises the solver end‑to‑end when possible.

## 2) When Configuration Parameters Change

If a rule’s config changes (added/removed/renamed parameters):

1. **Update tests first**
   - Update all related test fixtures and rule configs.
   - Remove deprecated config keys from tests.

2. **Update rule implementation**
   - Remove deprecated config keys from rule logic.
   - Validate only the current config shape.

3. **Update any documentation**
   - Update example JSON configs in `data/configs/` if they exist.
   - Keep `working.md` or other docs aligned with the new config.

## 3) Test File Expectations

Every new rule **must** have its own test file in `tests/`:

- `tests/test_<rule_name>.py`
- Must include:
  - At least one **positive** test (valid behavior)
  - At least one **negative** test (infeasible or constraint failure)

## 4) Rule Changes Must Be End‑to‑End

When a rule depends on new fields:

- **Schema validation** must accept the field.
- **Cleaner** must standardize it.
- **Solver** must be able to read and enforce it.
- **Tests** must confirm expected behavior.

## 5) Keep Rule Loader Accurate

Menu rules are loaded via `MenuRuleLoader`. If a rule is removed or renamed:

- Remove it from `RULE_CLASSES`.
- Remove related tests.
- Update any configs that reference it.

---

If any of the above changes are made, ensure you run `pytest` and verify all tests pass.
