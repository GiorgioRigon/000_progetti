from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app  # noqa: E402
from app.wb0_target_discovery import (  # noqa: E402
    build_discovery_run,
    build_prompt_preview,
    delete_discovery_run,
    load_project_sources,
    reset_latest_run,
    save_discovery_run,
)


class Wb0TargetDiscoveryTests(unittest.TestCase):
    def test_build_and_save_discovery_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            projects_root = Path(temp_dir) / "projects"
            run = build_discovery_run(
                research_goal="Trovare enti che programmano concerti corali o musica sacra.",
                project_context="Melodema, coro con repertorio cameristico e sacro.",
                territory_target="Lombardia, Veneto, Emilia-Romagna",
                target_types_text="comuni\ndiocesi\nfestival",
                selected_sources=["festival_websites", "municipality_event_pages"],
                research_prompt="Cerca enti che ospitano o programmano musica corale nel territorio indicato.",
                prompt_variants_text="festival corale lombardia\nmusica sacra diocesi veneto",
                inclusion_criteria_text="programmazione musicale pubblica\ncoerenza con repertorio corale",
                exclusion_criteria_text="eventi interni non pubblici",
                raw_candidates=(
                    "Festival Corale Padovano | festival | Padova | Veneto | Italia | https://example.org | "
                    "Rassegna da verificare manualmente\n"
                    "Diocesi di Bergamo | diocesi | Bergamo | Lombardia | Italia | https://example.com | "
                    "Verificare calendario musica sacra"
                ),
            )

            saved_path = save_discovery_run(run, projects_root)
            latest_path = projects_root / "melodema" / "wb0_target_discovery" / "latest.json"

            self.assertTrue(saved_path.exists())
            self.assertTrue(latest_path.exists())

            payload = json.loads(latest_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["research_goal"], "Trovare enti che programmano concerti corali o musica sacra.")
            self.assertEqual(payload["territory_target"], "Lombardia, Veneto, Emilia-Romagna")
            self.assertEqual(payload["target_types"], ["comuni", "diocesi", "festival"])
            self.assertEqual(payload["prompt_variants"][0], "festival corale lombardia")
            self.assertEqual(payload["inclusion_criteria"][0], "programmazione musicale pubblica")
            self.assertEqual(payload["candidate_count"], 2)

    def test_wb0_page_saves_latest_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.sqlite3"
            projects_root = Path(temp_dir) / "projects"
            schema_sql = (BASE_DIR / "data" / "schema.sql").read_text(encoding="utf-8")

            with sqlite3.connect(db_path) as connection:
                connection.executescript(schema_sql)
                connection.commit()

            app = create_app(db_path=db_path, projects_root=projects_root)
            app.config["TESTING"] = True
            client = app.test_client()

            response = client.post(
                "/wb0",
                data={
                    "research_goal": "Trovare enti per concerti corali.",
                    "project_context": "Melodema, coro con repertorio sacro e cameristico.",
                    "territory_target": "Lombardia e Veneto",
                    "target_types": "comuni\ndiocesi\nistituzioni culturali",
                    "selected_sources": ["festival_websites", "municipality_event_pages"],
                    "research_prompt": "Cerca enti pubblici o culturali che ospitano rassegne corali.",
                    "prompt_variants": "rassegne corali lombardia\nmusica sacra veneto enti culturali",
                    "inclusion_criteria": "programmazione musicale pubblica\nente attivo nel territorio",
                    "exclusion_criteria": "eventi scolastici interni",
                    "raw_candidates": (
                        "Associazione Corale Vicentina | associazione | Vicenza | Veneto | Italia | "
                        "https://vicentina.example | Buon fit territoriale\n"
                        "Festival di Musica Sacra Milano | festival | Milano | Lombardia | Italia | "
                        "https://milano.example | Da verificare programmazione"
                    ),
                },
                follow_redirects=True,
            )

            page = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("WB0 salvato correttamente con 2 candidate organizations.", page)
            self.assertIn("Trovare enti per concerti corali.", page)
            self.assertIn("Melodema, coro con repertorio sacro e cameristico.", page)
            self.assertIn("rassegne corali lombardia", page)

            latest_path = projects_root / "melodema" / "wb0_target_discovery" / "latest.json"
            payload = json.loads(latest_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["target_types"], ["comuni", "diocesi", "istituzioni culturali"])
            self.assertEqual(payload["prompt_variants"][1], "musica sacra veneto enti culturali")
            self.assertEqual(payload["candidates"][1]["name"], "Festival di Musica Sacra Milano")

    def test_wb0_page_updates_existing_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.sqlite3"
            projects_root = Path(temp_dir) / "projects"
            schema_sql = (BASE_DIR / "data" / "schema.sql").read_text(encoding="utf-8")

            with sqlite3.connect(db_path) as connection:
                connection.executescript(schema_sql)
                connection.commit()

            initial_run = build_discovery_run(
                research_goal="Trovare festival corali.",
                project_context="Melodema, coro da camera.",
                territory_target="Veneto",
                target_types_text="festival",
                selected_sources=["festival_websites"],
                research_prompt="Cerca festival con programmazione corale in Veneto.",
                prompt_variants_text="festival corale veneto",
                inclusion_criteria_text="programmazione corale",
                exclusion_criteria_text="festival non musicali",
                raw_candidates="Festival Corale Padovano | festival | Padova | Veneto | Italia | https://example.org | Prima nota",
            )
            run_path = save_discovery_run(initial_run, projects_root)

            app = create_app(db_path=db_path, projects_root=projects_root)
            app.config["TESTING"] = True
            client = app.test_client()

            response = client.post(
                "/wb0",
                data={
                    "form_type": "save_run",
                    "run_file": run_path.name,
                    "research_goal": "Trovare festival e teatri adatti al coro.",
                    "project_context": "Melodema, coro con repertorio sacro e cameristico.",
                    "territory_target": "Veneto e Lombardia",
                    "target_types": "festival\nteatri",
                    "selected_sources": ["festival_websites", "cultural_directories"],
                    "research_prompt": "Cerca festival e teatri con programmazione corale o sacra.",
                    "prompt_variants": "festival corale veneto\nteatro musica sacra lombardia",
                    "inclusion_criteria": "programmazione musicale pubblica\ncoerenza artistica",
                    "exclusion_criteria": "spazi senza programmazione stabile",
                    "raw_candidates": (
                        "Festival Corale Padovano | festival | Padova | Veneto | Italia | https://example.org | Nota aggiornata\n"
                        "Teatro Nuove Voci | teatro | Brescia | Lombardia | Italia | https://example.com | Seconda candidate"
                    ),
                },
                follow_redirects=True,
            )

            page = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Run WB0 aggiornato correttamente con 2 candidate organizations.", page)

            payload = json.loads(run_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["research_goal"], "Trovare festival e teatri adatti al coro.")
            self.assertEqual(payload["target_types"], ["festival", "teatri"])
            self.assertEqual(payload["prompt_variants"][1], "teatro musica sacra lombardia")
            self.assertEqual(payload["candidate_count"], 2)

    def test_wb0_can_delete_run_and_reset_latest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            projects_root = Path(temp_dir) / "projects"
            run = build_discovery_run(
                research_goal="Trovare festival corali.",
                project_context="Melodema, coro da camera.",
                territory_target="Italia nord",
                target_types_text="festival",
                selected_sources=["festival_websites"],
                research_prompt="Cerca festival corali nel nord Italia.",
                prompt_variants_text="festival corale nord italia",
                inclusion_criteria_text="programmazione corale",
                exclusion_criteria_text="eventi non musicali",
                raw_candidates="Festival Corale Padovano | festival | Padova | Veneto | Italia | https://example.org | Nota",
            )
            run_path = save_discovery_run(run, projects_root)
            latest_path = projects_root / "melodema" / "wb0_target_discovery" / "latest.json"

            self.assertTrue(delete_discovery_run("melodema", projects_root, run_path.name))
            self.assertFalse(run_path.exists())
            self.assertTrue(latest_path.exists())

            self.assertTrue(reset_latest_run("melodema", projects_root))
            self.assertFalse(latest_path.exists())

    def test_wb0_can_save_candidate_review_and_import_to_cis(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.sqlite3"
            projects_root = Path(temp_dir) / "projects"
            schema_sql = (BASE_DIR / "data" / "schema.sql").read_text(encoding="utf-8")

            with sqlite3.connect(db_path) as connection:
                connection.executescript(schema_sql)
                connection.commit()

            run = build_discovery_run(
                research_goal="Trovare festival corali in Lombardia.",
                project_context="Melodema, coro con repertorio corale e sacro.",
                territory_target="Lombardia",
                target_types_text="festival",
                selected_sources=["festival_websites"],
                research_prompt="Cerca festival corali in Lombardia.",
                prompt_variants_text="festival corale lombardia",
                inclusion_criteria_text="programmazione corale pubblica",
                exclusion_criteria_text="eventi interni",
                raw_candidates="Festival Corale Bergamasco | festival | Bergamo | Lombardia | Italia | https://example.org | Nota iniziale",
            )
            run_path = save_discovery_run(run, projects_root)

            app = create_app(db_path=db_path, projects_root=projects_root)
            app.config["TESTING"] = True
            client = app.test_client()

            review_response = client.post(
                "/wb0",
                data={
                    "form_type": "save_candidate_review",
                    "run_file": run_path.name,
                    "candidate_index": "0",
                    "review_status": "da_importare",
                    "fit_label": "alto",
                    "website_confirmed": "si",
                    "qualification_notes": "Festival coerente con repertorio corale e territorio.",
                    "final_decision": "da_importare",
                },
                follow_redirects=True,
            )

            review_page = review_response.get_data(as_text=True)
            self.assertEqual(review_response.status_code, 200)
            self.assertIn("Candidate aggiornata correttamente.", review_page)

            payload = json.loads(run_path.read_text(encoding="utf-8"))
            candidate = payload["candidates"][0]
            self.assertEqual(candidate["review_status"], "da_importare")
            self.assertEqual(candidate["fit_label"], "alto")

            import_response = client.post(
                "/wb0",
                data={
                    "form_type": "import_candidate",
                    "run_file": run_path.name,
                    "candidate_index": "0",
                },
                follow_redirects=True,
            )

            import_page = import_response.get_data(as_text=True)
            self.assertEqual(import_response.status_code, 200)
            self.assertIn("Festival Corale Bergamasco", import_page)

            with sqlite3.connect(db_path) as connection:
                row = connection.execute(
                    "SELECT id, source, notes FROM organizations WHERE name = ?",
                    ("Festival Corale Bergamasco",),
                ).fetchone()

            self.assertIsNotNone(row)
            self.assertEqual(row[1], "wb0_import")
            self.assertIn("WB0 qualificazione", row[2])

            payload = json.loads(run_path.read_text(encoding="utf-8"))
            candidate = payload["candidates"][0]
            self.assertEqual(candidate["final_decision"], "importata")
            self.assertIsNotNone(candidate["imported_organization_id"])

    def test_load_sources_and_build_prompt_preview(self) -> None:
        sources = load_project_sources("melodema", BASE_DIR / "projects")
        self.assertGreaterEqual(len(sources), 1)
        self.assertEqual(sources[0]["name"], "festival_websites")

        preview = build_prompt_preview(
            research_goal="Trovare enti per concerti corali.",
            project_context="Melodema, coro da camera.",
            territory_target="Veneto",
            target_types_text="diocesi\ncomuni",
            selected_sources=["festival_websites", "cultural_directories"],
            research_prompt="Cerca enti che ospitano musica corale o sacra.",
            inclusion_criteria_text="programmazione musicale pubblica\ncoerenza artistica",
            exclusion_criteria_text="eventi interni",
        )
        self.assertIn("Obiettivo ricerca: Trovare enti per concerti corali.", preview)
        self.assertIn("Tipi di target: diocesi, comuni", preview)
        self.assertIn("- programmazione musicale pubblica", preview)


if __name__ == "__main__":
    unittest.main()
