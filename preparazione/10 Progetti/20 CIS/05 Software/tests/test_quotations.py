from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
QUOTATIONS_PATH = BASE_DIR / "app" / "quotations.py"
SPEC = importlib.util.spec_from_file_location("cis_quotations", QUOTATIONS_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load quotations module from {QUOTATIONS_PATH}")
QUOTATIONS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = QUOTATIONS
SPEC.loader.exec_module(QUOTATIONS)

build_suggested_line_items = QUOTATIONS.build_suggested_line_items
build_intake_initial_data = QUOTATIONS.build_intake_initial_data
extract_intake_submission = QUOTATIONS.extract_intake_submission
list_intake_schemas = QUOTATIONS.list_intake_schemas
load_intake_schema = QUOTATIONS.load_intake_schema
load_price_list = QUOTATIONS.load_price_list


class QuotationsSchemaTests(unittest.TestCase):
    def test_can_load_ethics_schema_with_sections_and_fields(self) -> None:
        schema = load_intake_schema("ethics", BASE_DIR / "projects", "pdr125_edocs")

        self.assertEqual(schema["title"], "Preventivo PdR125 E-Docs E-KPI")
        self.assertGreaterEqual(len(schema["sections"]), 5)
        first_section = schema["sections"][0]
        self.assertEqual(first_section["key"], "anagrafica")
        self.assertGreaterEqual(len(first_section["fields"]), 3)

    def test_extract_submission_validates_required_fields(self) -> None:
        schema = {
            "sections": [
                {
                    "key": "base",
                    "label": "Base",
                    "fields": [
                        {"key": "organization_name", "label": "Nome organizzazione", "required": True},
                        {"key": "legal_form", "label": "Forma giuridica", "required": False},
                    ],
                }
            ]
        }

        payload, errors = extract_intake_submission(schema, {"organization_name": "", "legal_form": "SRL"})

        self.assertEqual(payload["legal_form"], "SRL")
        self.assertEqual(len(errors), 1)
        self.assertIn("Nome organizzazione", errors[0])

    def test_build_initial_data_prefills_from_organization(self) -> None:
        schema = {
            "sections": [
                {
                    "key": "base",
                    "label": "Base",
                    "fields": [
                        {"key": "organization_name", "label": "Nome organizzazione"},
                        {"key": "website", "label": "Sito web"},
                    ],
                }
            ]
        }
        organization = {"name": "Cliente Test", "website": "https://example.org"}

        initial_data = build_intake_initial_data(schema, organization, {})

        self.assertEqual(initial_data["organization_name"], "Cliente Test")
        self.assertEqual(initial_data["website"], "https://example.org")

    def test_list_intake_schemas_reads_project_directory(self) -> None:
        schemas = list_intake_schemas("melodema", BASE_DIR / "projects")
        schema_keys = {schema["key"] for schema in schemas}

        self.assertIn("evento_coro", schema_keys)

    def test_can_load_ethics_price_list(self) -> None:
        price_list = load_price_list("ethics", BASE_DIR / "projects")

        self.assertGreaterEqual(len(price_list), 3)
        self.assertEqual(price_list[0]["code"], "ETH-CONS")

    def test_ethics_intake_generates_suggested_line_items(self) -> None:
        intake_data = {
            "pdr125_objective": "rinnovo",
            "edocs_interest": "si",
            "ekpi_interest": "da valutare",
            "requested_services": "serve anche formazione utenti e caricamento documenti iniziale",
        }

        line_items = build_suggested_line_items("ethics", BASE_DIR / "projects", intake_data)
        line_item_codes = {item["code"] for item in line_items}
        line_items_by_code = {item["code"]: item for item in line_items}

        self.assertIn("ETH-CONS", line_item_codes)
        self.assertIn("ETH-EDOCS", line_item_codes)
        self.assertIn("ETH-KPI", line_item_codes)
        self.assertIn("ETH-TRAIN", line_item_codes)
        self.assertIn("ETH-UPLOAD", line_item_codes)
        self.assertEqual(line_items_by_code["ETH-CONS"]["quantity"], 3.0)
        self.assertEqual(line_items_by_code["ETH-EDOCS"]["unit_price"], 850.0)


if __name__ == "__main__":
    unittest.main()
