from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app  # noqa: E402
from app.data_access import Database, OrganizationCreate, OrganizationRepository  # noqa: E402
from app.wb0_target_discovery import build_discovery_run, save_discovery_run  # noqa: E402


class AgentRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.db_path = self.base_path / "test.sqlite3"
        self.projects_root = self.base_path / "projects"
        self._init_schema()
        self._init_projects_root()
        self.app = create_app(
            db_path=self.db_path,
            projects_root=self.projects_root,
            active_project_key="melodema",
        )
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_can_create_wb0_agent_run_and_import_candidate(self) -> None:
        discovery_run = build_discovery_run(
            research_goal="Trovare enti che programmano concerti corali.",
            project_context="Melodema, coro con repertorio sacro e cameristico.",
            territory_target="Veneto",
            target_types_text="festival\ncomuni",
            selected_sources=["festival_websites"],
            research_prompt="Cerca enti che programmano musica corale.",
            prompt_variants_text="festival corale veneto",
            inclusion_criteria_text="programmazione musicale pubblica",
            exclusion_criteria_text="eventi interni",
            raw_candidates=(
                "Festival Corale Vicentino | festival | Vicenza | Veneto | Italia | https://festival.example | Fit territoriale forte\n"
                "Comune di Schio | comune | Schio | Veneto | Italia | https://schio.example | Programmazione culturale da verificare"
            ),
            project_key="melodema",
        )
        run_path = save_discovery_run(discovery_run, self.projects_root)

        response = self.client.post(
            "/agents",
            data={
                "form_type": "create_wb0_run",
                "source_run_file": run_path.name,
            },
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Run agente WB0 creato correttamente.", page)
        self.assertIn("Festival Corale Vicentino", page)

        with sqlite3.connect(self.db_path) as connection:
            run_id = connection.execute("SELECT id FROM agent_runs WHERE agent_key = 'wb0'").fetchone()[0]
            task_id = connection.execute(
                "SELECT id FROM agent_tasks WHERE run_id = ? ORDER BY sort_order ASC, id ASC LIMIT 1",
                (run_id,),
            ).fetchone()[0]

        review_response = self.client.post(
            f"/agent-runs/{run_id}",
            data={
                "form_type": "task_review",
                "task_id": str(task_id),
                "status": "approved",
                "review_notes": "Candidate valida per approfondimento commerciale.",
            },
            follow_redirects=True,
        )
        review_page = review_response.get_data(as_text=True)
        self.assertEqual(review_response.status_code, 200)
        self.assertIn("Task agente aggiornato correttamente.", review_page)

        import_response = self.client.post(
            f"/agent-runs/{run_id}",
            data={
                "form_type": "import_wb0_task",
                "task_id": str(task_id),
                "review_notes": "Importata nel CIS 1.0 dal runtime 2.0.",
            },
            follow_redirects=True,
        )
        import_page = import_response.get_data(as_text=True)
        self.assertEqual(import_response.status_code, 200)
        self.assertIn("Task WB0 importato nel CIS correttamente.", import_page)
        self.assertIn("Festival Corale Vicentino", import_page)

    def test_can_create_wb1_agent_batch(self) -> None:
        organizations = OrganizationRepository(Database(self.db_path))
        organizations.create(
            OrganizationCreate(
                name="Comune di Vicenza",
                project_key="melodema",
                city="Vicenza",
            )
        )
        organizations.create(
            OrganizationCreate(
                name="Festival Voci Alpine",
                project_key="melodema",
                city="Trento",
                email="info@vocialpine.example",
            )
        )

        response = self.client.post(
            "/agents",
            data={
                "form_type": "create_wb1_run",
                "filter_mode": "without_contacts_first",
                "batch_size": "2",
            },
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Run agente WB1 creato correttamente.", page)
        self.assertIn("Comune di Vicenza", page)
        self.assertIn("Festival Voci Alpine", page)

    def test_wb1_task_can_save_structured_enrichment_and_sync_organization(self) -> None:
        organizations = OrganizationRepository(Database(self.db_path))
        organization_id = organizations.create(
            OrganizationCreate(
                name="Delta Tech S.p.A.",
                project_key="melodema",
                city="Vicenza",
            )
        )

        response = self.client.post(
            "/agents",
            data={
                "form_type": "create_wb1_run",
                "filter_mode": "alphabetical",
                "batch_size": "1",
            },
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Run agente WB1 creato correttamente.", page)

        with sqlite3.connect(self.db_path) as connection:
            run_id = connection.execute(
                "SELECT id FROM agent_runs WHERE agent_key = 'wb1' ORDER BY id DESC LIMIT 1"
            ).fetchone()[0]
            task_id = connection.execute(
                "SELECT id FROM agent_tasks WHERE run_id = ? AND organization_id = ?",
                (run_id, organization_id),
            ).fetchone()[0]

        review_response = self.client.post(
            f"/agent-runs/{run_id}",
            data={
                "form_type": "task_review",
                "task_id": str(task_id),
                "status": "approved",
                "website": "https://www.delta.example",
                "general_email": "info@delta.example",
                "general_phone": "+39 0444 123456",
                "contact_full_name": "Laura Bianchi",
                "contact_role": "HR Manager",
                "contact_email": "laura.bianchi@delta.example",
                "contact_phone": "+39 333 1234567",
                "social_profiles": "linkedin | https://linkedin.example/delta",
                "verification_source": "sito ufficiale e pagina team",
                "contact_level": "decision maker",
                "qualification_signals": "HR, governance, formazione",
                "research_note": "Lead interessante con referente verificabile.",
                "fit_label": "alto",
                "priority_level": "alta",
                "opportunity_type": "cliente",
                "next_step": "Passare a WB3",
                "qualification_note": "Buon fit commerciale e organizzativo.",
                "review_notes": "Task WB1 completato con dati strutturati.",
            },
            follow_redirects=True,
        )
        review_page = review_response.get_data(as_text=True)
        self.assertEqual(review_response.status_code, 200)
        self.assertIn("Task agente aggiornato correttamente.", review_page)
        self.assertIn("Laura Bianchi", review_page)

        with sqlite3.connect(self.db_path) as connection:
            org_row = connection.execute(
                "SELECT website, email, phone, notes FROM organizations WHERE id = ?",
                (organization_id,),
            ).fetchone()
            contact_row = connection.execute(
                "SELECT full_name, role, email, phone FROM contacts WHERE organization_id = ?",
                (organization_id,),
            ).fetchone()
            task_row = connection.execute(
                "SELECT status, result_payload_json FROM agent_tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

        self.assertEqual(org_row[0], "https://www.delta.example")
        self.assertEqual(org_row[1], "info@delta.example")
        self.assertEqual(org_row[2], "+39 0444 123456")
        self.assertIn("[WB1 note]", org_row[3])
        self.assertIn("[Lead qualification]", org_row[3])
        self.assertEqual(contact_row[0], "Laura Bianchi")
        self.assertEqual(contact_row[1], "HR Manager")
        self.assertEqual(contact_row[2], "laura.bianchi@delta.example")
        self.assertEqual(task_row[0], "approved")
        self.assertIn('"fit_label": "alto"', task_row[1])

    def test_can_create_wb2_agent_batch(self) -> None:
        organizations = OrganizationRepository(Database(self.db_path))
        organizations.create(
            OrganizationCreate(
                name="Omega Systems S.r.l.",
                project_key="melodema",
                city="Verona",
            )
        )

        response = self.client.post(
            "/agents",
            data={
                "form_type": "create_wb2_run",
                "filter_mode": "without_contacts_first",
                "batch_size": "1",
            },
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Run agente WB2 creato correttamente.", page)
        self.assertIn("Omega Systems S.r.l.", page)

    def test_can_create_wb1_single_lead_run(self) -> None:
        organizations = OrganizationRepository(Database(self.db_path))
        first_id = organizations.create(
            OrganizationCreate(
                name="Lead Uno S.r.l.",
                project_key="melodema",
                city="Vicenza",
            )
        )
        organizations.create(
            OrganizationCreate(
                name="Lead Due S.r.l.",
                project_key="melodema",
                city="Padova",
            )
        )

        response = self.client.post(
            "/agents",
            data={
                "form_type": "create_wb1_single_run",
                "organization_id": str(first_id),
            },
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Run agente WB1 sul singolo lead creato correttamente.", page)
        self.assertIn("Lead Uno S.r.l.", page)

        with sqlite3.connect(self.db_path) as connection:
            run_id = connection.execute(
                "SELECT id FROM agent_runs WHERE agent_key = 'wb1' ORDER BY id DESC LIMIT 1"
            ).fetchone()[0]
            tasks = connection.execute(
                "SELECT title, organization_id FROM agent_tasks WHERE run_id = ? ORDER BY id",
                (run_id,),
            ).fetchall()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0][0], "Lead Uno S.r.l.")
        self.assertEqual(tasks[0][1], first_id)

    def test_agents_dashboard_shows_full_single_lead_lists_beyond_preview_limit(self) -> None:
        organizations = OrganizationRepository(Database(self.db_path))
        for index in range(1, 14):
            organizations.create(
                OrganizationCreate(
                    name=f"Lead {index:02d} S.r.l.",
                    project_key="melodema",
                    city="Vicenza",
                )
            )

        response = self.client.get("/agents")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Lead 13 S.r.l.", page)
        self.assertIn('id="wb1_single_organization"', page)
        self.assertIn('id="wb2_single_organization"', page)

    def test_can_create_wb2_single_lead_run(self) -> None:
        organizations = OrganizationRepository(Database(self.db_path))
        first_id = organizations.create(
            OrganizationCreate(
                name="Lead Tre S.p.A.",
                project_key="melodema",
                city="Verona",
            )
        )
        organizations.create(
            OrganizationCreate(
                name="Lead Quattro S.p.A.",
                project_key="melodema",
                city="Trento",
            )
        )

        response = self.client.post(
            "/agents",
            data={
                "form_type": "create_wb2_single_run",
                "organization_id": str(first_id),
            },
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Run agente WB2 sul singolo lead creato correttamente.", page)
        self.assertIn("Lead Tre S.p.A.", page)

        with sqlite3.connect(self.db_path) as connection:
            run_id = connection.execute(
                "SELECT id FROM agent_runs WHERE agent_key = 'wb2' ORDER BY id DESC LIMIT 1"
            ).fetchone()[0]
            tasks = connection.execute(
                "SELECT title, organization_id FROM agent_tasks WHERE run_id = ? ORDER BY id",
                (run_id,),
            ).fetchall()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0][0], "Lead Tre S.p.A.")
        self.assertEqual(tasks[0][1], first_id)

    def test_wb2_task_can_save_structured_contact_enrichment(self) -> None:
        organizations = OrganizationRepository(Database(self.db_path))
        organization_id = organizations.create(
            OrganizationCreate(
                name="Sigma Energy S.p.A.",
                project_key="melodema",
                city="Padova",
            )
        )

        response = self.client.post(
            "/agents",
            data={
                "form_type": "create_wb2_run",
                "filter_mode": "alphabetical",
                "batch_size": "1",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        with sqlite3.connect(self.db_path) as connection:
            run_id = connection.execute(
                "SELECT id FROM agent_runs WHERE agent_key = 'wb2' ORDER BY id DESC LIMIT 1"
            ).fetchone()[0]
            task_id = connection.execute(
                "SELECT id FROM agent_tasks WHERE run_id = ? AND organization_id = ?",
                (run_id, organization_id),
            ).fetchone()[0]

        review_response = self.client.post(
            f"/agent-runs/{run_id}",
            data={
                "form_type": "task_review",
                "task_id": str(task_id),
                "status": "approved",
                "website": "https://www.sigma.example",
                "employee_count": "240",
                "general_email": "info@sigma.example",
                "general_phone": "+39 049 555123",
                "contact_full_name": "Marco Verdi",
                "contact_role": "Operations Director",
                "contact_email": "marco.verdi@sigma.example",
                "contact_phone": "+39 335 1234567",
                "social_profiles": "linkedin | https://linkedin.example/sigma",
                "verification_source": "sito ufficiale e profilo societario",
                "contact_level": "decision maker",
                "org_signals": "gruppo industriale, operations, crescita",
                "research_note": "Contatto coerente e dimensione aziendale confermata.",
                "review_notes": "Task WB2 completato con contatto e dettagli org.",
            },
            follow_redirects=True,
        )
        review_page = review_response.get_data(as_text=True)
        self.assertEqual(review_response.status_code, 200)
        self.assertIn("Task agente aggiornato correttamente.", review_page)
        self.assertIn("Marco Verdi", review_page)

        with sqlite3.connect(self.db_path) as connection:
            org_row = connection.execute(
                "SELECT website, email, phone, employee_count, notes FROM organizations WHERE id = ?",
                (organization_id,),
            ).fetchone()
            contact_row = connection.execute(
                "SELECT full_name, role, email, phone, notes FROM contacts WHERE organization_id = ?",
                (organization_id,),
            ).fetchone()
            task_row = connection.execute(
                "SELECT status, result_payload_json FROM agent_tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

        self.assertEqual(org_row[0], "https://www.sigma.example")
        self.assertEqual(org_row[1], "info@sigma.example")
        self.assertEqual(org_row[2], "+39 049 555123")
        self.assertEqual(org_row[3], 240)
        self.assertIn("[WB2 note]", org_row[4])
        self.assertIn("Numero dipendenti: 240", org_row[4])
        self.assertEqual(contact_row[0], "Marco Verdi")
        self.assertEqual(contact_row[1], "Operations Director")
        self.assertEqual(contact_row[2], "marco.verdi@sigma.example")
        self.assertEqual(contact_row[4], "Contatto aggiunto da WB2 runtime 2.0.")
        self.assertEqual(task_row[0], "approved")
        self.assertIn('"employee_count": "240"', task_row[1])

    def test_can_create_wb0_mission_run_from_brief(self) -> None:
        response = self.client.post(
            "/agents",
            data={
                "form_type": "create_wb0_mission_run",
                "research_goal": "Trovare festival e comuni che programmano musica corale.",
                "project_context": "Melodema, coro con repertorio sacro e cameristico.",
                "territory_target": "Veneto",
                "target_types": "festival\ncomuni",
                "selected_sources": ["festival_websites", "municipality_event_pages"],
                "research_prompt": "Cerca enti che ospitano rassegne corali o musica sacra.",
                "prompt_variants": "festival corale veneto\ncomuni musica sacra veneto",
                "inclusion_criteria": "programmazione musicale pubblica\ncoerenza con repertorio corale",
                "exclusion_criteria": "eventi interni",
            },
            follow_redirects=True,
        )
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Missione agente WB0 creata correttamente.", page)
        self.assertIn("wb0_search_slice", page)
        self.assertIn("Cerca enti che ospitano rassegne corali o musica sacra.", page)

    def test_wb0_mission_can_collect_structured_candidates_and_import_one(self) -> None:
        create_response = self.client.post(
            "/agents",
            data={
                "form_type": "create_wb0_mission_run",
                "research_goal": "Trovare aziende che hanno partecipato a workshop PdR125.",
                "project_context": "Ethics supporta aziende su PdR125 e parita di genere.",
                "territory_target": "Italia",
                "target_types": "aziende",
                "selected_sources": ["company_websites", "cultural_directories"],
                "research_prompt": "Cerca aziende che hanno partecipato a workshop o webinar su PdR125.",
                "prompt_variants": "azienda workshop PdR125",
                "inclusion_criteria": "evidenza pubblica verificabile\nnome azienda chiaramente identificabile",
                "exclusion_criteria": "nomi non verificabili",
            },
            follow_redirects=True,
        )
        create_page = create_response.get_data(as_text=True)
        self.assertEqual(create_response.status_code, 200)
        self.assertIn("Missione agente WB0 creata correttamente.", create_page)

        with sqlite3.connect(self.db_path) as connection:
            run_id = connection.execute(
                "SELECT id FROM agent_runs WHERE source_type = 'wb0_search_mission' ORDER BY id DESC LIMIT 1"
            ).fetchone()[0]
            task_id = connection.execute(
                "SELECT id FROM agent_tasks WHERE run_id = ? ORDER BY sort_order ASC, id ASC LIMIT 1",
                (run_id,),
            ).fetchone()[0]

        collect_response = self.client.post(
            f"/agent-runs/{run_id}",
            data={
                "form_type": "task_review",
                "task_id": str(task_id),
                "status": "approved",
                "raw_candidates_text": (
                    "Alpha Consulting Srl | azienda | Milano | Lombardia | Italia | https://alpha.example | "
                    "Partecipazione citata in workshop sulla certificazione\n"
                    "Beta Industrie Spa | azienda | Verona | Veneto | Italia | https://beta.example | "
                    "Webinar su PdR125 con partecipazione aziendale"
                ),
                "review_notes": "Primi nominativi raccolti da query esterna.",
            },
            follow_redirects=True,
        )
        collect_page = collect_response.get_data(as_text=True)
        self.assertEqual(collect_response.status_code, 200)
        self.assertIn("Task agente aggiornato correttamente.", collect_page)
        self.assertIn("Alpha Consulting Srl", collect_page)
        self.assertIn("Importa nel CIS", collect_page)

        import_response = self.client.post(
            f"/agent-runs/{run_id}",
            data={
                "form_type": "import_wb0_mission_candidate",
                "task_id": str(task_id),
                "candidate_index": "0",
                "review_notes": "Importata dopo raccolta strutturata missione WB0.",
            },
            follow_redirects=True,
        )
        import_page = import_response.get_data(as_text=True)
        self.assertEqual(import_response.status_code, 200)
        self.assertIn("Candidate della missione WB0 importata nel CIS correttamente.", import_page)
        self.assertIn("Alpha Consulting Srl", import_page)

        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT source, project_key FROM organizations WHERE name = ?",
                ("Alpha Consulting Srl",),
            ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "cis20_wb0_mission_import")
        self.assertEqual(row[1], "melodema")

    def test_wb0_mission_candidate_link_is_normalized_for_display(self) -> None:
        create_response = self.client.post(
            "/agents",
            data={
                "form_type": "create_wb0_mission_run",
                "research_goal": "Trovare aziende partecipanti a workshop PdR125.",
                "project_context": "Ethics supporta aziende su PdR125.",
                "territory_target": "Italia",
                "target_types": "aziende",
                "selected_sources": ["company_websites"],
                "research_prompt": "Cerca aziende che hanno partecipato a workshop su PdR125.",
                "prompt_variants": "azienda workshop PdR125",
                "inclusion_criteria": "evidenza pubblica verificabile",
                "exclusion_criteria": "nomi non verificabili",
            },
            follow_redirects=True,
        )
        self.assertEqual(create_response.status_code, 200)

        with sqlite3.connect(self.db_path) as connection:
            run_id = connection.execute(
                "SELECT id FROM agent_runs WHERE source_type = 'wb0_search_mission' ORDER BY id DESC LIMIT 1"
            ).fetchone()[0]
            task_id = connection.execute(
                "SELECT id FROM agent_tasks WHERE run_id = ? ORDER BY sort_order ASC, id ASC LIMIT 1",
                (run_id,),
            ).fetchone()[0]

        collect_response = self.client.post(
            f"/agent-runs/{run_id}",
            data={
                "form_type": "task_review",
                "task_id": str(task_id),
                "status": "approved",
                "raw_candidates_text": "Gamma Srl | azienda | Milano | Lombardia | Italia | www.gamma.example | Workshop PdR125",
                "review_notes": "Test link senza schema.",
            },
            follow_redirects=True,
        )
        page = collect_response.get_data(as_text=True)
        self.assertEqual(collect_response.status_code, 200)
        self.assertIn('href="https://www.gamma.example"', page)

    def _init_schema(self) -> None:
        schema_sql = (BASE_DIR / "data" / "schema.sql").read_text(encoding="utf-8")
        with sqlite3.connect(self.db_path) as connection:
            connection.executescript(schema_sql)
            connection.commit()

    def _init_projects_root(self) -> None:
        melodema_dir = self.projects_root / "melodema"
        ethics_dir = self.projects_root / "ethics"
        melodema_dir.mkdir(parents=True, exist_ok=True)
        ethics_dir.mkdir(parents=True, exist_ok=True)
        (melodema_dir / "project_config.yaml").write_text(
            "project:\n  key: melodema\n  name: Melodema Outreach Engine\n",
            encoding="utf-8",
        )
        (ethics_dir / "project_config.yaml").write_text(
            "project:\n  key: ethics\n  name: Ethics Outreach Engine\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
