from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.exceptions import HTTPException

from app.csv_import import ImportResult, import_leads_csv
from app.data_access import (
    QuoteCreate,
    QuoteIntakeCreate,
    QuoteIntakeRepository,
    QuoteLineItemCreate,
    QuoteLineItemRepository,
    QuoteRepository,
    QuoteVersionCreate,
    QuoteVersionRepository,
    build_quote_snapshot,
    ContactCreate,
    ContactRepository,
    Database,
    MessageCreate,
    MessageRepository,
    OrganizationCreate,
    OrganizationRepository,
    OutreachActionCreate,
    OutreachActionRepository,
    RelationshipMemoryCreate,
    RelationshipMemoryRepository,
)
from app.followup_planner import (
    build_followup_note,
    extract_followup_data,
    merge_followup_notes,
    suggest_followup,
)
from app.lead_qualification import (
    build_qualification_note,
    extract_qualification_data,
    merge_qualification_notes,
)
from app.outreach_drafter import (
    DEFAULT_TEMPLATE_NAME,
    build_outreach_draft,
    list_outreach_templates,
    suggest_outreach_template,
)
from app.strategy_builder import (
    build_strategy_note,
    extract_strategy_data,
    merge_strategy_notes,
    suggest_strategy,
)
from app.quotations import (
    build_intake_initial_data,
    build_suggested_line_items,
    extract_intake_submission,
    list_intake_schemas,
    load_intake_schema,
    load_price_list,
    load_quotation_config,
    quote_config_paths,
    resolve_default_intake_schema_key,
)
from app.project_registry import list_projects
from app.workbot_profiles import load_workbot_profile
from app.wb1_contact_hunter import (
    build_research_note,
    build_contact_hunter_prompt,
    extract_research_metadata,
    extract_research_note,
    extract_social_profiles,
    merge_wb1_notes,
    parse_multiline_field as parse_wb1_multiline_field,
)
from app.wb0_target_discovery import (
    DEFAULT_PROJECT_KEY,
    build_discovery_run,
    build_prompt_preview,
    delete_discovery_run,
    list_discovery_runs,
    load_discovery_run,
    load_latest_run,
    load_project_sources,
    mark_candidate_imported,
    reset_latest_run,
    save_discovery_run,
    update_candidate_review,
    update_discovery_run,
)


def create_app(
    db_path: Path | str | None = None,
    projects_root: Path | str | None = None,
    active_project_key: str = DEFAULT_PROJECT_KEY,
) -> Flask:
    base_dir = Path(__file__).resolve().parent.parent
    template_dir = base_dir / "templates"
    static_dir = base_dir / "static"
    configured_projects_root = Path(projects_root) if projects_root is not None else base_dir / "projects"
    app = Flask(__name__, template_folder=str(template_dir))
    app.static_folder = str(static_dir)
    app.config["SECRET_KEY"] = "cis-local-dev"
    app.config["PROJECTS_ROOT"] = str(configured_projects_root)
    app.config["ACTIVE_PROJECT_KEY"] = active_project_key
    _configure_logging(app)
    database = Database(db_path) if db_path is not None else Database()
    organizations = OrganizationRepository(database)
    contacts = ContactRepository(database)
    outreach_actions = OutreachActionRepository(database)
    messages = MessageRepository(database)
    relationship_memory = RelationshipMemoryRepository(database)
    quote_intakes = QuoteIntakeRepository(database)
    quotes = QuoteRepository(database)
    quote_line_items = QuoteLineItemRepository(database)
    quote_versions = QuoteVersionRepository(database)
    app.logger.info("CIS app initialized", extra={"db_path": str(database.db_path)})

    def get_active_project_key() -> str:
        available_projects = list_projects(app.config["PROJECTS_ROOT"])
        available_keys = {project["key"] for project in available_projects}
        session_project_key = str(session.get("active_project_key", "") or "")
        if session_project_key and session_project_key in available_keys:
            return session_project_key
        configured_project_key = str(app.config["ACTIVE_PROJECT_KEY"])
        if configured_project_key in available_keys:
            return configured_project_key
        if available_projects:
            return available_projects[0]["key"]
        return configured_project_key

    @app.context_processor
    def inject_project_navigation() -> dict[str, object]:
        available_projects = list_projects(app.config["PROJECTS_ROOT"])
        return {
            "available_projects": available_projects,
            "active_project_key": get_active_project_key(),
        }

    @app.get("/")
    def home() -> str:
        return render_template("home.html")

    @app.post("/active-project")
    def set_active_project() -> str:
        requested_project_key = request.form.get("project_key", "").strip()
        available_projects = list_projects(app.config["PROJECTS_ROOT"])
        available_keys = {project["key"] for project in available_projects}

        if requested_project_key not in available_keys:
            flash("Il progetto selezionato non e disponibile.", "error")
            return redirect(request.referrer or url_for("home"))

        session["active_project_key"] = requested_project_key
        flash(f"Progetto attivo aggiornato: {requested_project_key}.", "success")
        return redirect(request.referrer or url_for("home"))

    @app.route("/wb0", methods=["GET", "POST"])
    def wb0_target_discovery() -> str:
        project_key = get_active_project_key()
        available_sources = load_project_sources(project_key, app.config["PROJECTS_ROOT"])
        wb0_profile = load_workbot_profile(project_key, "wb0", app.config["PROJECTS_ROOT"])
        selected_run_file = request.args.get("run_file", "").strip()
        latest_run = load_latest_run(project_key, app.config["PROJECTS_ROOT"])
        selected_run = (
            load_discovery_run(project_key, app.config["PROJECTS_ROOT"], selected_run_file)
            if selected_run_file
            else None
        )
        form_data = {
            "research_goal": "",
            "project_context": "",
            "territory_target": "",
            "target_types": "",
            "selected_sources": [],
            "research_prompt": "",
            "prompt_variants": "",
            "inclusion_criteria": "",
            "exclusion_criteria": "",
            "raw_candidates": "",
            "run_file": selected_run_file,
        }

        if request.method == "POST":
            form_type = request.form.get("form_type", "save_run")
            selected_run_file = request.form.get("run_file", "").strip()
            form_data = {
                "research_goal": request.form.get("research_goal", ""),
                "project_context": request.form.get("project_context", ""),
                "territory_target": request.form.get("territory_target", ""),
                "target_types": request.form.get("target_types", ""),
                "selected_sources": request.form.getlist("selected_sources"),
                "research_prompt": request.form.get("research_prompt", ""),
                "prompt_variants": request.form.get("prompt_variants", ""),
                "inclusion_criteria": request.form.get("inclusion_criteria", ""),
                "exclusion_criteria": request.form.get("exclusion_criteria", ""),
                "raw_candidates": request.form.get("raw_candidates", ""),
                "run_file": selected_run_file,
            }
            if form_type == "delete_run":
                if not selected_run_file:
                    flash("Seleziona un run WB0 da eliminare.", "error")
                elif delete_discovery_run(project_key, app.config["PROJECTS_ROOT"], selected_run_file):
                    app.logger.info(
                        "WB0 discovery run deleted",
                        extra={"project_key": project_key, "run_file": selected_run_file},
                    )
                    flash("Run WB0 eliminato correttamente.", "success")
                    return redirect(url_for("wb0_target_discovery"))
                else:
                    flash("Il run WB0 selezionato non e disponibile.", "error")
            elif form_type == "reset_latest":
                if reset_latest_run(project_key, app.config["PROJECTS_ROOT"]):
                    app.logger.info("WB0 latest reset", extra={"project_key": project_key})
                    flash("latest.json e stato resettato.", "success")
                else:
                    flash("Nessun latest.json da resettare.", "warning")
                return redirect(url_for("wb0_target_discovery"))
            elif form_type == "save_candidate_review":
                candidate_index_raw = request.form.get("candidate_index", "").strip()
                if not selected_run_file:
                    flash("Seleziona un run WB0 da aggiornare.", "error")
                elif not candidate_index_raw.isdigit():
                    flash("Candidate non valida.", "error")
                else:
                    try:
                        update_candidate_review(
                            project_key=project_key,
                            projects_root=app.config["PROJECTS_ROOT"],
                            run_filename=selected_run_file,
                            candidate_index=int(candidate_index_raw),
                            review_status=request.form.get("review_status", ""),
                            fit_label=request.form.get("fit_label", ""),
                            website_confirmed=request.form.get("website_confirmed", ""),
                            qualification_notes=request.form.get("qualification_notes", ""),
                            final_decision=request.form.get("final_decision", ""),
                        )
                    except Exception:
                        app.logger.exception("WB0 failed to update candidate review")
                        flash("Non e stato possibile aggiornare la candidate.", "error")
                    else:
                        app.logger.info(
                            "WB0 candidate review updated",
                            extra={"project_key": project_key, "run_file": selected_run_file},
                        )
                        flash("Candidate aggiornata correttamente.", "success")
                        return redirect(url_for("wb0_target_discovery", run_file=selected_run_file))
            elif form_type == "import_candidate":
                candidate_index_raw = request.form.get("candidate_index", "").strip()
                if not selected_run_file:
                    flash("Seleziona un run WB0 da cui importare.", "error")
                elif not candidate_index_raw.isdigit():
                    flash("Candidate non valida.", "error")
                else:
                    candidate_index = int(candidate_index_raw)
                    active_run_for_import = load_discovery_run(
                        project_key,
                        app.config["PROJECTS_ROOT"],
                        selected_run_file,
                    )
                    if active_run_for_import is None:
                        flash("Il run WB0 selezionato non e disponibile.", "error")
                    else:
                        candidates = active_run_for_import.get("candidates", [])
                        if candidate_index < 0 or candidate_index >= len(candidates):
                            flash("Candidate non valida.", "error")
                        else:
                            candidate = candidates[candidate_index]
                            if candidate.get("imported_organization_id"):
                                flash("Questa candidate e gia stata importata nel CIS.", "warning")
                            else:
                                try:
                                    organization_id = organizations.create(
                                        OrganizationCreate(
                                            name=str(candidate.get("name", "")).strip(),
                                            project_key=project_key,
                                            organization_type=_clean_form_value(candidate.get("organization_type")),
                                            city=_clean_form_value(candidate.get("city")),
                                            region=_clean_form_value(candidate.get("region")),
                                            country=_clean_form_value(candidate.get("country")),
                                            website=_clean_form_value(candidate.get("website")),
                                            source="wb0_import",
                                            notes=_build_import_notes(candidate),
                                        )
                                    )
                                    mark_candidate_imported(
                                        project_key=project_key,
                                        projects_root=app.config["PROJECTS_ROOT"],
                                        run_filename=selected_run_file,
                                        candidate_index=candidate_index,
                                        organization_id=organization_id,
                                    )
                                except Exception:
                                    app.logger.exception("WB0 failed to import candidate")
                                    flash("Non e stato possibile importare la candidate nel CIS.", "error")
                                else:
                                    app.logger.info(
                                        "WB0 candidate imported",
                                        extra={
                                            "project_key": project_key,
                                            "run_file": selected_run_file,
                                            "organization_id": organization_id,
                                        },
                                    )
                                    flash("Candidate importata nel CIS come organization.", "success")
                                    return redirect(url_for("organization_detail", organization_id=organization_id))
            else:
                try:
                    discovery_run = build_discovery_run(
                        research_goal=form_data["research_goal"],
                        project_context=form_data["project_context"],
                        territory_target=form_data["territory_target"],
                        target_types_text=form_data["target_types"],
                        selected_sources=form_data["selected_sources"],
                        research_prompt=form_data["research_prompt"],
                        prompt_variants_text=form_data["prompt_variants"],
                        inclusion_criteria_text=form_data["inclusion_criteria"],
                        exclusion_criteria_text=form_data["exclusion_criteria"],
                        raw_candidates=form_data["raw_candidates"],
                        project_key=project_key,
                    )
                    if selected_run_file:
                        existing_run = load_discovery_run(
                            project_key,
                            app.config["PROJECTS_ROOT"],
                            selected_run_file,
                        )
                        if existing_run is None:
                            raise ValueError("Il run WB0 da modificare non e disponibile.")
                        discovery_run.created_at = str(existing_run.get("created_at", discovery_run.created_at))
                        update_discovery_run(
                            discovery_run,
                            app.config["PROJECTS_ROOT"],
                            selected_run_file,
                        )
                        target_run_file = selected_run_file
                    else:
                        saved_path = save_discovery_run(discovery_run, app.config["PROJECTS_ROOT"])
                        target_run_file = saved_path.name
                except ValueError as error:
                    app.logger.warning("WB0 validation error", extra={"message_text": str(error)})
                    flash(str(error), "error")
                except Exception:
                    app.logger.exception("WB0 failed to save discovery run")
                    flash("Non e stato possibile salvare il risultato WB0.", "error")
                else:
                    app.logger.info(
                        "WB0 discovery run saved",
                        extra={
                            "project_key": project_key,
                            "research_goal": discovery_run.research_goal,
                            "candidate_count": discovery_run.candidate_count,
                            "run_file": selected_run_file or "new",
                        },
                    )
                    flash(
                        (
                            f"Run WB0 aggiornato correttamente con {discovery_run.candidate_count} "
                            "candidate organizations."
                            if selected_run_file
                            else f"WB0 salvato correttamente con {discovery_run.candidate_count} candidate organizations."
                        ),
                        "success",
                    )
                    return redirect(url_for("wb0_target_discovery", run_file=target_run_file))

            latest_run = latest_run or {
                "project_key": project_key,
                "research_goal": "",
                "project_context": "",
                "territory_target": "",
                "target_types": [],
                "selected_sources": [],
                "research_prompt": "",
                "prompt_variants": [],
                "inclusion_criteria": [],
                "exclusion_criteria": [],
                "created_at": "",
                "candidate_count": 0,
                "candidates": [],
            }
        else:
            active_run = selected_run or latest_run
            if active_run:
                form_data = {
                    "research_goal": str(active_run.get("research_goal", "")),
                    "project_context": str(active_run.get("project_context", "")),
                    "territory_target": str(active_run.get("territory_target", "")),
                    "target_types": "\n".join(active_run.get("target_types", [])),
                    "selected_sources": list(active_run.get("selected_sources", [])),
                    "research_prompt": str(active_run.get("research_prompt", "")),
                    "prompt_variants": "\n".join(active_run.get("prompt_variants", [])),
                    "inclusion_criteria": "\n".join(active_run.get("inclusion_criteria", [])),
                    "exclusion_criteria": "\n".join(active_run.get("exclusion_criteria", [])),
                    "raw_candidates": "\n".join(
                        _candidate_to_line(candidate) for candidate in active_run.get("candidates", [])
                    ),
                    "run_file": selected_run_file,
                }
            latest_run = latest_run or {
                "project_key": project_key,
                "research_goal": "",
                "project_context": "",
                "territory_target": "",
                "target_types": [],
                "selected_sources": [],
                "research_prompt": "",
                "prompt_variants": [],
                "inclusion_criteria": [],
                "exclusion_criteria": [],
                "created_at": "",
                "candidate_count": 0,
                "candidates": [],
            }

        latest_output_path = (
            Path(app.config["PROJECTS_ROOT"]) / project_key / "wb0_target_discovery" / "latest.json"
        )
        saved_runs = list_discovery_runs(project_key, app.config["PROJECTS_ROOT"])
        active_run = selected_run or latest_run
        prompt_preview = build_prompt_preview(
            form_data["research_goal"],
            form_data["project_context"],
            form_data["territory_target"],
            form_data["target_types"],
            form_data["selected_sources"],
            form_data["research_prompt"],
            form_data["inclusion_criteria"],
            form_data["exclusion_criteria"],
            profile=wb0_profile,
        )
        return render_template(
            "wb0_target_discovery.html",
            project_key=project_key,
            active_run=active_run,
            wb0_profile=wb0_profile,
            form_data=form_data,
            available_sources=available_sources,
            prompt_preview=prompt_preview,
            saved_runs=saved_runs,
            selected_run_file=selected_run_file,
            latest_output_path=latest_output_path if latest_output_path.exists() else None,
        )

    @app.route("/organizations", methods=["GET", "POST"])
    def organizations_list() -> str:
        import_result = ImportResult()

        if request.method == "POST":
            form_type = request.form.get("form_type")

            if form_type == "manual":
                name = request.form.get("name", "").strip()
                if name:
                    try:
                        organization_id = organizations.create(
                            OrganizationCreate(
                                name=name,
                                project_key=get_active_project_key(),
                                organization_type=request.form.get("organization_type", "").strip() or None,
                                sector=request.form.get("sector", "").strip() or None,
                                city=request.form.get("city", "").strip() or None,
                                region=request.form.get("region", "").strip() or None,
                                country=request.form.get("country", "").strip() or None,
                                website=request.form.get("website", "").strip() or None,
                                email=request.form.get("email", "").strip() or None,
                                phone=request.form.get("phone", "").strip() or None,
                                employee_count=_parse_optional_nonnegative_int(
                                    request.form.get("employee_count", "")
                                ),
                                notes=request.form.get("notes", "").strip() or None,
                            )
                        )
                    except Exception:
                        app.logger.exception(
                            "Failed to create organization",
                            extra={"organization_name": name},
                        )
                        flash("Non e stato possibile salvare la organization. Controlla i dati e riprova.", "error")
                    else:
                        app.logger.info(
                            "Organization created",
                            extra={"organization_id": organization_id, "organization_name": name},
                        )
                        flash("Organization salvata correttamente.", "success")
                        return redirect(url_for("organization_detail", organization_id=organization_id))

                import_result.errors.append("Il nome della organization e obbligatorio.")

            elif form_type == "csv_import":
                uploaded_file = request.files.get("csv_file")
                if uploaded_file is None or uploaded_file.filename == "":
                    import_result.errors.append("Seleziona un file CSV da importare.")
                else:
                    try:
                        csv_text = uploaded_file.read().decode("utf-8-sig")
                    except UnicodeDecodeError:
                        app.logger.warning(
                            "CSV import rejected: invalid encoding",
                            extra={"csv_filename": uploaded_file.filename},
                        )
                        import_result.errors.append(
                            "Il file non e in formato UTF-8 leggibile."
                        )
                    else:
                        try:
                            import_result = import_leads_csv(
                                csv_text=csv_text,
                                organizations=organizations,
                                contacts=contacts,
                                project_key=get_active_project_key(),
                            )
                        except Exception:
                            app.logger.exception(
                                "CSV import failed",
                                extra={"csv_filename": uploaded_file.filename},
                            )
                            import_result.errors.append(
                                "Si e verificato un errore durante l'import CSV."
                            )
                            flash("Import CSV non completato. Controlla il file e riprova.", "error")
                        else:
                            app.logger.info(
                                "CSV import completed",
                                extra={
                                    "csv_filename": uploaded_file.filename,
                                    "imported_organizations": import_result.imported_organizations,
                                    "imported_contacts": import_result.imported_contacts,
                                    "errors_count": len(import_result.errors),
                                },
                            )
                            if import_result.errors:
                                flash("Import completato con alcuni errori da controllare.", "warning")
                            else:
                                flash("Import CSV completato correttamente.", "success")

        return render_template(
            "organizations.html",
            organizations=organizations.list_by_project(get_active_project_key()),
            import_result=import_result,
        )

    @app.get("/organizations/table")
    def organizations_table() -> str:
        active_project_key = get_active_project_key()
        organizations_for_project = organizations.list_by_project(active_project_key)
        search_query = request.args.get("q", "").strip()
        normalized_search_query = search_query.casefold()
        table_rows = []

        for organization in organizations_for_project:
            qualification_data = extract_qualification_data(organization.get("notes"))
            if normalized_search_query:
                searchable_parts = [
                    str(organization.get("name") or ""),
                    str(organization.get("organization_type") or ""),
                    str(organization.get("city") or ""),
                    str(organization.get("country") or ""),
                    str(organization.get("email") or ""),
                    str(organization.get("phone") or ""),
                    str(qualification_data.get("fit_label") or ""),
                    str(qualification_data.get("priority_level") or ""),
                    str(qualification_data.get("opportunity_type") or ""),
                    str(qualification_data.get("next_step") or ""),
                ]
                searchable_text = " ".join(searchable_parts).casefold()
                if normalized_search_query not in searchable_text:
                    continue
            table_rows.append(
                {
                    "organization": organization,
                    "qualification": qualification_data,
                }
            )

        return render_template(
            "organizations_table.html",
            table_rows=table_rows,
            search_query=search_query,
            total_organizations=len(organizations_for_project),
        )

    @app.route("/quotes", methods=["GET", "POST"])
    def quotes_list() -> str:
        active_project_key = get_active_project_key()
        project_organizations = organizations.list_by_project(active_project_key)
        organization_id_filter_raw = request.args.get("organization_id", "").strip()
        selected_organization_id = (
            int(organization_id_filter_raw) if organization_id_filter_raw.isdigit() else None
        )

        if request.method == "POST":
            form_type = request.form.get("form_type", "create_quote")
            if form_type == "create_quote":
                organization_id_raw = request.form.get("organization_id", "").strip()
                title = request.form.get("title", "").strip()
                if not organization_id_raw.isdigit():
                    abort(400, description="Seleziona una organization valida per il preventivo.")
                if not title:
                    abort(400, description="Il titolo del preventivo e obbligatorio.")

                organization_id = int(organization_id_raw)
                organization = organizations.get(organization_id)
                if organization is None or organization.get("project_key") != active_project_key:
                    abort(404)

                intake_data = {
                    "requested_by": request.form.get("requested_by", "").strip(),
                    "scope_summary": request.form.get("scope_summary", "").strip(),
                    "budget_notes": request.form.get("budget_notes", "").strip(),
                    "timing_notes": request.form.get("timing_notes", "").strip(),
                }
                intake_id = quote_intakes.create(
                    QuoteIntakeCreate(
                        project_key=active_project_key,
                        organization_id=organization_id,
                        title=title,
                        status="ready_for_quote",
                        intake_schema_key=request.form.get("intake_schema_key", "").strip() or None,
                        intake_data=intake_data,
                        summary=request.form.get("scope_summary", "").strip() or None,
                    )
                )
                quote_id = quotes.create(
                    QuoteCreate(
                        project_key=active_project_key,
                        organization_id=organization_id,
                        quote_intake_id=intake_id,
                        title=title,
                        quote_number=_build_quote_number(active_project_key),
                        status="draft",
                        currency=request.form.get("currency", "").strip() or "EUR",
                        valid_until=request.form.get("valid_until", "").strip() or None,
                        version_label="v1",
                        assumptions=request.form.get("assumptions", "").strip() or None,
                        internal_notes=request.form.get("internal_notes", "").strip() or None,
                        client_notes=request.form.get("client_notes", "").strip() or None,
                    )
                )
                quote = quotes.get(quote_id)
                intake = quote_intakes.get(intake_id)
                quote_versions.create(
                    QuoteVersionCreate(
                        quote_id=quote_id,
                        version_label="v1",
                        snapshot=build_quote_snapshot(quote or {}, intake, []),
                    )
                )
                flash("Preventivo creato correttamente.", "success")
                return redirect(url_for("quote_detail", quote_id=quote_id))

        project_quotes = quotes.list_by_project(active_project_key)
        if selected_organization_id is not None:
            project_quotes = [
                quote for quote in project_quotes if int(quote["organization_id"]) == selected_organization_id
            ]

        quotation_config = load_quotation_config(active_project_key, app.config["PROJECTS_ROOT"])
        default_currency = quotation_config.get("default_currency", "EUR")

        return render_template(
            "quotes.html",
            quotes=project_quotes,
            organizations=project_organizations,
            selected_organization_id=selected_organization_id,
            intake_schemas=list_intake_schemas(active_project_key, app.config["PROJECTS_ROOT"]),
            quotation_config=quotation_config,
            quotation_paths=quote_config_paths(active_project_key, app.config["PROJECTS_ROOT"]),
            default_currency=default_currency,
        )

    @app.post("/organizations/<int:organization_id>/quotes/new")
    def create_quote_from_organization(organization_id: int) -> str:
        organization = organizations.get(organization_id)
        if organization is None:
            abort(404)

        active_project_key = get_active_project_key()
        if organization.get("project_key") != active_project_key:
            abort(404)

        intake_schema_key = resolve_default_intake_schema_key(
            active_project_key,
            app.config["PROJECTS_ROOT"],
        )
        organization_name = str(organization.get("name") or "Organization").strip()
        quote_title = f"Preventivo {organization_name}"
        intake_data = {
            "organization_name": organization_name,
        }
        intake_id = quote_intakes.create(
            QuoteIntakeCreate(
                project_key=active_project_key,
                organization_id=organization_id,
                title=quote_title,
                status="draft",
                intake_schema_key=intake_schema_key,
                intake_data=intake_data,
            )
        )
        quote_id = quotes.create(
            QuoteCreate(
                project_key=active_project_key,
                organization_id=organization_id,
                quote_intake_id=intake_id,
                title=quote_title,
                quote_number=_build_quote_number(active_project_key),
                status="draft",
                currency=load_quotation_config(
                    active_project_key,
                    app.config["PROJECTS_ROOT"],
                ).get("default_currency", "EUR"),
                version_label="v1",
            )
        )
        quote = quotes.get(quote_id)
        intake = quote_intakes.get(intake_id)
        quote_versions.create(
            QuoteVersionCreate(
                quote_id=quote_id,
                version_label="v1",
                snapshot=build_quote_snapshot(quote or {}, intake, []),
            )
        )
        flash("Preventivo creato. Completa ora la scheda dati preventivo.", "success")
        return redirect(f"{url_for('quote_detail', quote_id=quote_id)}#scheda-dati")

    @app.route("/quotes/<int:quote_id>", methods=["GET", "POST"])
    def quote_detail(quote_id: int) -> str:
        quote = quotes.get(quote_id)
        if quote is None:
            abort(404)
        if quote.get("project_key") != get_active_project_key():
            abort(404)
        organization = organizations.get(int(quote["organization_id"])) if quote else None
        intake = (
            quote_intakes.get(int(quote["quote_intake_id"]))
            if quote and quote.get("quote_intake_id")
            else None
        )
        intake_schema_key = str((intake or {}).get("intake_schema_key") or "").strip()
        intake_schema = (
            load_intake_schema(
                str(quote.get("project_key") or get_active_project_key()),
                app.config["PROJECTS_ROOT"],
                intake_schema_key,
            )
            if intake_schema_key
            else {"key": "", "title": "", "sections": []}
        )
        intake_form_data = build_intake_initial_data(
            intake_schema,
            organization,
            (intake or {}).get("intake_data"),
        )

        if request.method == "POST":
            form_type = request.form.get("form_type", "line_item")
            if form_type == "intake":
                if intake is None:
                    abort(404)
                intake_payload, intake_errors = extract_intake_submission(intake_schema, request.form)
                if intake_errors:
                    for error_message in intake_errors:
                        flash(error_message, "error")
                    intake_form_data = intake_payload
                else:
                    intake_status = request.form.get("intake_status", "").strip() or str(intake.get("status") or "draft")
                    intake_summary = request.form.get("intake_summary", "").strip() or None
                    quote_intakes.update(
                        int(intake["id"]),
                        status=intake_status,
                        intake_schema_key=intake_schema_key or None,
                        intake_data=intake_payload,
                        summary=intake_summary,
                    )
                    refreshed_quote = quotes.get(quote_id)
                    refreshed_intake = quote_intakes.get(int(intake["id"]))
                    quote_versions.create(
                        QuoteVersionCreate(
                            quote_id=quote_id,
                            version_label=str((refreshed_quote or {}).get("version_label") or "v1"),
                            snapshot=build_quote_snapshot(
                                refreshed_quote or {},
                                refreshed_intake,
                                quote_line_items.list_by_quote(quote_id),
                            ),
                        )
                    )
                    flash("Scheda preventivo aggiornata correttamente.", "success")
                    return redirect(url_for("quote_detail", quote_id=quote_id))
            elif form_type == "generate_from_intake":
                if intake is None:
                    abort(404)
                suggested_line_items = build_suggested_line_items(
                    str(quote.get("project_key") or get_active_project_key()),
                    app.config["PROJECTS_ROOT"],
                    intake.get("intake_data"),
                )
                existing_line_items = quote_line_items.list_by_quote(quote_id)
                existing_codes = {
                    str(item.get("code") or "").strip()
                    for item in existing_line_items
                    if str(item.get("code") or "").strip()
                }
                next_sort_order = len(existing_line_items)
                created_count = 0
                for suggested_item in suggested_line_items:
                    if str(suggested_item.get("code") or "") in existing_codes:
                        continue
                    quote_line_items.create(
                        QuoteLineItemCreate(
                            quote_id=quote_id,
                            line_type=str(suggested_item.get("line_type") or "custom"),
                            code=str(suggested_item.get("code") or "").strip() or None,
                            title=str(suggested_item.get("title") or "Voce da listino"),
                            description=str(suggested_item.get("description") or "").strip() or None,
                            quantity=float(suggested_item.get("quantity") or 1),
                            unit=str(suggested_item.get("unit") or "").strip() or None,
                            unit_price=float(suggested_item.get("unit_price") or 0),
                            sort_order=next_sort_order,
                            pricing_source=str(suggested_item.get("pricing_source") or "rule_based"),
                        )
                    )
                    next_sort_order += 1
                    created_count += 1
                _refresh_quote_totals(
                    quote_id=quote_id,
                    quotes=quotes,
                    quote_line_items=quote_line_items,
                )
                updated_quote = quotes.get(quote_id)
                updated_intake = quote_intakes.get(int(intake["id"]))
                quote_versions.create(
                    QuoteVersionCreate(
                        quote_id=quote_id,
                        version_label=str((updated_quote or {}).get("version_label") or "v1"),
                        snapshot=build_quote_snapshot(
                            updated_quote or {},
                            updated_intake,
                            quote_line_items.list_by_quote(quote_id),
                        ),
                    )
                )
                if created_count == 0:
                    flash("Nessuna nuova riga suggerita dal listino oppure righe gia presenti.", "warning")
                else:
                    flash(f"Generate {created_count} righe suggerite dal listino.", "success")
                return redirect(url_for("quote_detail", quote_id=quote_id))
            elif form_type == "line_item":
                title = request.form.get("title", "").strip()
                if not title:
                    abort(400, description="Il titolo della riga preventivo e obbligatorio.")
                quantity = _parse_required_positive_float(
                    request.form.get("quantity", ""),
                    "La quantita deve essere un numero positivo.",
                )
                unit_price = _parse_required_nonnegative_float(
                    request.form.get("unit_price", ""),
                    "Il prezzo unitario deve essere un numero non negativo.",
                )
                quote_line_items.create(
                    QuoteLineItemCreate(
                        quote_id=quote_id,
                        line_type=request.form.get("line_type", "").strip() or "custom",
                        code=request.form.get("code", "").strip() or None,
                        title=title,
                        description=request.form.get("description", "").strip() or None,
                        quantity=quantity,
                        unit=request.form.get("unit", "").strip() or None,
                        unit_price=unit_price,
                        sort_order=_parse_optional_nonnegative_int(request.form.get("sort_order", "")) or 0,
                        pricing_source=request.form.get("pricing_source", "").strip() or "manual",
                    )
                )
                _refresh_quote_totals(
                    quote_id=quote_id,
                    quotes=quotes,
                    quote_line_items=quote_line_items,
                )
                updated_quote = quotes.get(quote_id)
                intake = (
                    quote_intakes.get(int(updated_quote["quote_intake_id"]))
                    if updated_quote and updated_quote.get("quote_intake_id")
                    else None
                )
                quote_versions.create(
                    QuoteVersionCreate(
                        quote_id=quote_id,
                        version_label=str(updated_quote.get("version_label") or "v1"),
                        snapshot=build_quote_snapshot(
                            updated_quote or {},
                            intake,
                            quote_line_items.list_by_quote(quote_id),
                        ),
                    )
                )
                flash("Riga preventivo aggiunta correttamente.", "success")
                return redirect(url_for("quote_detail", quote_id=quote_id))

        quote = quotes.get(quote_id)
        intake = (
            quote_intakes.get(int(quote["quote_intake_id"]))
            if quote and quote.get("quote_intake_id")
            else None
        )
        line_items = quote_line_items.list_by_quote(quote_id)
        versions = quote_versions.list_by_quote(quote_id)
        suggested_line_items = build_suggested_line_items(
            str(quote.get("project_key") or get_active_project_key()),
            app.config["PROJECTS_ROOT"],
            (intake or {}).get("intake_data"),
        )
        return render_template(
            "quote_detail.html",
            quote=quote,
            organization=organization,
            intake=intake,
            intake_schema=intake_schema,
            intake_form_data=intake_form_data,
            line_items=line_items,
            suggested_line_items=suggested_line_items,
            versions=versions,
        )

    @app.route("/organizations/<int:organization_id>", methods=["GET", "POST"])
    def organization_detail(organization_id: int) -> str:
        organization = organizations.get(organization_id)
        if organization is None:
            abort(404)
        organization_quotes = quotes.list_by_organization(organization_id)
        organization_contacts = contacts.list_by_organization(organization_id)
        organization_messages = messages.list_by_organization(organization_id)
        organization_relationship_memory = relationship_memory.list_by_organization(organization_id)
        available_outreach_templates = list_outreach_templates(
            str(organization.get("project_key") or get_active_project_key()),
            app.config["PROJECTS_ROOT"],
        )
        suggested_template = suggest_outreach_template(
            available_outreach_templates,
            organization_contacts[0] if organization_contacts else None,
        )
        selected_template_name = _resolve_outreach_template_name(
            request.args.get("template_name", "") or str((suggested_template or {}).get("name") or ""),
            available_outreach_templates,
        )
        selected_template_metadata = _find_outreach_template_metadata(
            selected_template_name,
            available_outreach_templates,
        )
        strategy_data = extract_strategy_data(organization.get("notes"))
        followup_data = extract_followup_data(organization.get("notes"))

        if request.method == "POST":
            form_type = request.form.get("form_type", "organization")

            if form_type == "organization":
                name = request.form.get("name", "").strip()
                if not name:
                    abort(400, description="Il nome della organization e obbligatorio.")

                try:
                    organizations.update(
                        organization_id,
                        OrganizationCreate(
                            name=name,
                            project_key=str(organization.get("project_key", "melodema")),
                            organization_type=request.form.get("organization_type", "").strip() or None,
                            sector=request.form.get("sector", "").strip() or None,
                            city=request.form.get("city", "").strip() or None,
                            region=request.form.get("region", "").strip() or None,
                            country=request.form.get("country", "").strip() or None,
                            website=request.form.get("website", "").strip() or None,
                            email=request.form.get("email", "").strip() or None,
                            phone=request.form.get("phone", "").strip() or None,
                            employee_count=_parse_optional_nonnegative_int(
                                request.form.get("employee_count", "")
                            ),
                            source=request.form.get("source", "").strip() or None,
                            notes=request.form.get("notes", "").strip() or None,
                        ),
                    )
                except Exception:
                    app.logger.exception(
                        "Failed to update organization",
                        extra={"organization_id": organization_id},
                    )
                    flash("Non e stato possibile aggiornare la organization.", "error")
                else:
                    app.logger.info(
                        "Organization updated",
                        extra={"organization_id": organization_id},
                    )
                    flash("Organization aggiornata correttamente.", "success")
            elif form_type == "contact":
                full_name = request.form.get("full_name", "").strip()
                first_name = request.form.get("first_name", "").strip()
                last_name = request.form.get("last_name", "").strip()
                if not any([full_name, first_name, last_name]):
                    abort(400, description="Inserisci almeno un nome per il contatto.")

                try:
                    contact_id = contacts.create(
                        ContactCreate(
                            organization_id=organization_id,
                            first_name=first_name or None,
                            last_name=last_name or None,
                            full_name=full_name or None,
                            role=request.form.get("role", "").strip() or None,
                            email=request.form.get("email", "").strip() or None,
                            phone=request.form.get("phone", "").strip() or None,
                            linkedin_url=request.form.get("linkedin_url", "").strip() or None,
                            notes=request.form.get("notes", "").strip() or None,
                        )
                    )
                except Exception:
                    app.logger.exception(
                        "Failed to create contact",
                        extra={"organization_id": organization_id},
                    )
                    flash("Non e stato possibile aggiungere il contatto.", "error")
                else:
                    app.logger.info(
                        "Contact created",
                        extra={"organization_id": organization_id, "contact_id": contact_id},
                    )
                    flash("Contatto aggiunto correttamente.", "success")
            elif form_type == "edit_contact":
                contact_id_raw = request.form.get("contact_id", "").strip()
                if not contact_id_raw.isdigit():
                    abort(400, description="ID contatto non valido.")

                full_name = request.form.get("full_name", "").strip()
                first_name = request.form.get("first_name", "").strip()
                last_name = request.form.get("last_name", "").strip()
                if not any([full_name, first_name, last_name]):
                    abort(400, description="Inserisci almeno un nome per il contatto.")

                contact_id = int(contact_id_raw)
                existing_contact = contacts.get(contact_id)
                if existing_contact is None or existing_contact["organization_id"] != organization_id:
                    abort(404)

                try:
                    contacts.update(
                        contact_id,
                        ContactCreate(
                            organization_id=organization_id,
                            first_name=first_name or None,
                            last_name=last_name or None,
                            full_name=full_name or None,
                            role=request.form.get("role", "").strip() or None,
                            email=request.form.get("email", "").strip() or None,
                            phone=request.form.get("phone", "").strip() or None,
                            linkedin_url=request.form.get("linkedin_url", "").strip() or None,
                            notes=request.form.get("notes", "").strip() or None,
                        ),
                    )
                except Exception:
                    app.logger.exception(
                        "Failed to update contact",
                        extra={"organization_id": organization_id, "contact_id": contact_id},
                    )
                    flash("Non e stato possibile aggiornare il contatto.", "error")
                else:
                    app.logger.info(
                        "Contact updated",
                        extra={"organization_id": organization_id, "contact_id": contact_id},
                    )
                    flash("Contatto aggiornato correttamente.", "success")
            elif form_type == "wb1_enrichment":
                social_profiles = parse_wb1_multiline_field(request.form.get("social_profiles", ""))
                contact_full_name = request.form.get("contact_full_name", "").strip()
                contact_role = request.form.get("contact_role", "").strip()
                contact_email = request.form.get("contact_email", "").strip()
                contact_phone = request.form.get("contact_phone", "").strip()
                website = request.form.get("website", "").strip()
                general_email = request.form.get("general_email", "").strip()
                general_phone = request.form.get("general_phone", "").strip()
                research_note = build_research_note(
                    research_note=request.form.get("research_note", ""),
                    verification_source=request.form.get("verification_source", ""),
                    contact_level=request.form.get("contact_level", ""),
                    qualification_signals=request.form.get("qualification_signals", ""),
                )

                if not any(
                    [
                        website,
                        general_email,
                        general_phone,
                        contact_full_name,
                        contact_role,
                        contact_email,
                        contact_phone,
                        social_profiles,
                        research_note,
                    ]
                ):
                    flash("Inserisci almeno un dato WB1 da salvare.", "error")
                    return redirect(url_for("organization_detail", organization_id=organization_id))

                try:
                    organizations.update(
                        organization_id,
                        OrganizationCreate(
                            name=str(organization["name"]),
                            project_key=str(organization.get("project_key", "melodema")),
                            campaign_id=organization["campaign_id"],
                            organization_type=organization["organization_type"],
                            sector=organization["sector"],
                            city=organization["city"],
                            region=organization["region"],
                            country=organization["country"],
                            website=website or organization["website"],
                            phone=general_phone or organization["phone"],
                            email=general_email or organization["email"],
                            employee_count=organization["employee_count"],
                            source=organization["source"],
                            notes=merge_wb1_notes(
                                existing_notes=organization["notes"],
                                social_profiles=social_profiles,
                                research_note=research_note,
                            ),
                        ),
                    )

                    if any([contact_full_name, contact_role, contact_email, contact_phone]):
                        contacts.create(
                            ContactCreate(
                                organization_id=organization_id,
                                full_name=contact_full_name or None,
                                role=contact_role or None,
                                email=contact_email or None,
                                phone=contact_phone or None,
                                notes="Contatto aggiunto da WB1 Contact Hunter.",
                            )
                        )
                except Exception:
                    app.logger.exception(
                        "Failed to save WB1 enrichment",
                        extra={"organization_id": organization_id},
                    )
                    flash("Non e stato possibile salvare i dati WB1.", "error")
                else:
                    app.logger.info(
                        "WB1 enrichment saved",
                        extra={"organization_id": organization_id},
                    )
                    flash("WB1 aggiornato correttamente.", "success")
            elif form_type == "lead_qualification":
                qualification_note = build_qualification_note(
                    fit_label=request.form.get("fit_label", ""),
                    opportunity_type=request.form.get("opportunity_type", ""),
                    priority_level=request.form.get("priority_level", ""),
                    qualification_signals=request.form.get("qualification_signals", ""),
                    next_step=request.form.get("next_step", ""),
                    qualification_note=request.form.get("qualification_note", ""),
                )

                if not qualification_note:
                    flash("Inserisci almeno un dato di qualificazione lead.", "error")
                    return redirect(url_for("organization_detail", organization_id=organization_id))

                try:
                    organizations.update(
                        organization_id,
                        OrganizationCreate(
                            name=str(organization["name"]),
                            project_key=str(organization.get("project_key", "melodema")),
                            campaign_id=organization["campaign_id"],
                            organization_type=organization["organization_type"],
                            sector=organization["sector"],
                            city=organization["city"],
                            region=organization["region"],
                            country=organization["country"],
                            website=organization["website"],
                            phone=organization["phone"],
                            email=organization["email"],
                            employee_count=organization["employee_count"],
                            source=organization["source"],
                            notes=merge_qualification_notes(
                                existing_notes=organization["notes"],
                                qualification_note=qualification_note,
                            ),
                        ),
                    )
                except Exception:
                    app.logger.exception(
                        "Failed to save lead qualification",
                        extra={"organization_id": organization_id},
                    )
                    flash("Non e stato possibile salvare la qualificazione lead.", "error")
                else:
                    app.logger.info(
                        "Lead qualification saved",
                        extra={"organization_id": organization_id},
                    )
                    flash("Qualificazione lead aggiornata correttamente.", "success")
            elif form_type == "wb3_strategy":
                strategy_note = build_strategy_note(
                    channel=request.form.get("channel", ""),
                    channel_reason=request.form.get("channel_reason", ""),
                    commercial_angle=request.form.get("commercial_angle", ""),
                    caution_note=request.form.get("caution_note", ""),
                    next_step=request.form.get("next_step", ""),
                )

                if not strategy_note:
                    flash("Inserisci almeno un dato di strategia WB3.", "error")
                    return redirect(url_for("organization_detail", organization_id=organization_id))

                try:
                    organizations.update(
                        organization_id,
                        OrganizationCreate(
                            name=str(organization["name"]),
                            project_key=str(organization.get("project_key", "melodema")),
                            campaign_id=organization["campaign_id"],
                            organization_type=organization["organization_type"],
                            sector=organization["sector"],
                            city=organization["city"],
                            region=organization["region"],
                            country=organization["country"],
                            website=organization["website"],
                            phone=organization["phone"],
                            email=organization["email"],
                            employee_count=organization["employee_count"],
                            source=organization["source"],
                            notes=merge_strategy_notes(
                                existing_notes=organization["notes"],
                                strategy_note=strategy_note,
                            ),
                        ),
                    )
                except Exception:
                    app.logger.exception(
                        "Failed to save WB3 strategy",
                        extra={"organization_id": organization_id},
                    )
                    flash("Non e stato possibile salvare la strategia WB3.", "error")
                else:
                    app.logger.info(
                        "WB3 strategy saved",
                        extra={"organization_id": organization_id},
                    )
                    flash("WB3 aggiornato correttamente.", "success")
            elif form_type == "wb5_followup":
                followup_note = build_followup_note(
                    followup_window=request.form.get("followup_window", ""),
                    channel=request.form.get("channel", ""),
                    micro_script=request.form.get("micro_script", ""),
                    reason=request.form.get("reason", ""),
                    next_status=request.form.get("next_status", ""),
                )

                if not followup_note:
                    flash("Inserisci almeno un dato di follow-up WB5.", "error")
                    return redirect(url_for("organization_detail", organization_id=organization_id))

                try:
                    organizations.update(
                        organization_id,
                        OrganizationCreate(
                            name=str(organization["name"]),
                            project_key=str(organization.get("project_key", "melodema")),
                            campaign_id=organization["campaign_id"],
                            organization_type=organization["organization_type"],
                            sector=organization["sector"],
                            city=organization["city"],
                            region=organization["region"],
                            country=organization["country"],
                            website=organization["website"],
                            phone=organization["phone"],
                            email=organization["email"],
                            employee_count=organization["employee_count"],
                            source=organization["source"],
                            notes=merge_followup_notes(
                                existing_notes=organization["notes"],
                                followup_note=followup_note,
                            ),
                        ),
                    )
                except Exception:
                    app.logger.exception(
                        "Failed to save WB5 follow-up",
                        extra={"organization_id": organization_id},
                    )
                    flash("Non e stato possibile salvare il follow-up WB5.", "error")
                else:
                    app.logger.info(
                        "WB5 follow-up saved",
                        extra={"organization_id": organization_id},
                    )
                    flash("WB5 aggiornato correttamente.", "success")
            elif form_type == "relationship_memory":
                memory_type = request.form.get("memory_type", "").strip()
                content = request.form.get("content", "").strip()
                importance_raw = request.form.get("importance", "").strip()
                source = request.form.get("source", "").strip() or None
                contact_id = _parse_optional_contact_id(
                    request.form.get("contact_id", ""),
                    organization_contacts,
                )

                if not memory_type or not content:
                    flash("Inserisci almeno tipo memoria e contenuto.", "error")
                    return redirect(url_for("organization_detail", organization_id=organization_id))

                try:
                    importance = int(importance_raw) if importance_raw else 1
                except ValueError:
                    abort(400, description="Importanza relationship memory non valida.")

                if importance < 1:
                    abort(400, description="Importanza relationship memory non valida.")

                try:
                    relationship_memory.create(
                        RelationshipMemoryCreate(
                            organization_id=organization_id,
                            contact_id=contact_id,
                            memory_type=memory_type,
                            content=content,
                            importance=importance,
                            source=source,
                        )
                    )
                except Exception:
                    app.logger.exception(
                        "Failed to save relationship memory",
                        extra={"organization_id": organization_id},
                    )
                    flash("Non e stato possibile salvare la relationship memory.", "error")
                else:
                    app.logger.info(
                        "Relationship memory saved",
                        extra={"organization_id": organization_id},
                    )
                    flash("Relationship memory aggiornata correttamente.", "success")
            elif form_type == "outreach_draft":
                selected_contact_id = _parse_optional_contact_id(
                    request.form.get("contact_id", ""),
                    organization_contacts,
                )
                draft_subject = request.form.get("subject", "").strip()
                draft_body = request.form.get("body", "").strip()
                template_name = _resolve_outreach_template_name(
                    request.form.get("template_name", ""),
                    available_outreach_templates,
                )

                if not draft_subject and not draft_body:
                    flash("Genera o compila una bozza outreach prima di salvarla.", "error")
                    return redirect(
                        url_for(
                            "organization_detail",
                            organization_id=organization_id,
                            template_name=template_name,
                        )
                    )

                try:
                    action_id = outreach_actions.create(
                        OutreachActionCreate(
                            campaign_id=organization.get("campaign_id"),
                            organization_id=organization_id,
                            contact_id=selected_contact_id,
                            action_type="draft_outreach",
                            channel="email",
                            status="draft",
                            summary=_build_outreach_summary(draft_subject, organization.get("name")),
                        )
                    )
                    messages.create(
                        MessageCreate(
                            outreach_action_id=action_id,
                            organization_id=organization_id,
                            contact_id=selected_contact_id,
                            direction="outbound",
                            channel="email",
                            subject=draft_subject or None,
                            body=draft_body or None,
                            status="draft",
                        )
                    )
                except Exception:
                    app.logger.exception(
                        "Failed to save outreach draft",
                        extra={"organization_id": organization_id},
                    )
                    flash("Non e stato possibile salvare la bozza outreach.", "error")
                else:
                    app.logger.info(
                        "Outreach draft saved",
                        extra={"organization_id": organization_id, "contact_id": selected_contact_id},
                    )
                    flash("Bozza outreach salvata correttamente.", "success")
            elif form_type == "outreach_regenerate":
                selected_contact_id = _parse_optional_contact_id(
                    request.form.get("contact_id", ""),
                    organization_contacts,
                )
                selected_contact = next(
                    (contact for contact in organization_contacts if int(contact["id"]) == selected_contact_id),
                    None,
                )
                template_name = _resolve_outreach_template_name(
                    request.form.get("template_name", ""),
                    available_outreach_templates,
                )

                organization = organizations.get(organization_id)
                organization_contacts = contacts.list_by_organization(organization_id)
                organization_messages = messages.list_by_organization(organization_id)
                organization_relationship_memory = relationship_memory.list_by_organization(organization_id)
                qualification_data = extract_qualification_data(organization.get("notes"))
                strategy_data = extract_strategy_data(organization.get("notes"))
                followup_data = extract_followup_data(organization.get("notes"))
                wb1_profile = load_workbot_profile(
                    get_active_project_key(),
                    "wb1",
                    app.config["PROJECTS_ROOT"],
                )
                wb1_prompt_preview = build_contact_hunter_prompt(
                    organization_name=str(organization.get("name", "") or ""),
                    organization_type=str(organization.get("organization_type", "") or ""),
                    city=str(organization.get("city", "") or ""),
                    region=str(organization.get("region", "") or ""),
                    country=str(organization.get("country", "") or ""),
                    website=str(organization.get("website", "") or ""),
                    current_email=str(organization.get("email", "") or ""),
                    current_phone=str(organization.get("phone", "") or ""),
                    existing_contacts=organization_contacts,
                    profile=wb1_profile,
                )
                wb1_research_metadata = extract_research_metadata(organization.get("notes"))
                wb1_form_data = {
                    "website": str(organization.get("website", "") or ""),
                    "general_email": str(organization.get("email", "") or ""),
                    "general_phone": str(organization.get("phone", "") or ""),
                    "contact_full_name": "",
                    "contact_role": "",
                    "contact_email": "",
                    "contact_phone": "",
                    "social_profiles": "\n".join(extract_social_profiles(organization.get("notes"))),
                    "research_note": wb1_research_metadata["research_note"],
                    "verification_source": wb1_research_metadata["verification_source"],
                    "contact_level": wb1_research_metadata["contact_level"],
                    "qualification_signals": wb1_research_metadata["qualification_signals"],
                }
                outreach_template_error = ""
                outreach_template_path = ""
                outreach_form_data = {
                    "template_name": template_name,
                    "contact_id": str(selected_contact_id) if selected_contact_id else "",
                    "subject": "",
                    "body": "",
                }
                try:
                    outreach_draft = build_outreach_draft(
                        project_key=str(organization.get("project_key") or get_active_project_key()),
                        projects_root=app.config["PROJECTS_ROOT"],
                        organization=organization,
                        contact=selected_contact,
                        qualification_data=qualification_data,
                        template_name=template_name,
                    )
                except (FileNotFoundError, ValueError) as error:
                    outreach_template_error = str(error)
                else:
                    outreach_template_path = outreach_draft.template_path
                    outreach_form_data["subject"] = outreach_draft.subject
                    outreach_form_data["body"] = outreach_draft.body

                return render_template(
                    "organization_detail.html",
                    organization=organization,
                    organization_quotes=quotes.list_by_organization(organization_id),
                    contacts=organization_contacts,
                    available_outreach_templates=available_outreach_templates,
                    suggested_template=suggested_template,
                    selected_template_metadata=selected_template_metadata,
                    outreach_history=organization_messages,
                    relationship_memory_items=organization_relationship_memory,
                    outreach_form_data=outreach_form_data,
                    outreach_template_error=outreach_template_error,
                    outreach_template_path=outreach_template_path,
                    qualification_data=qualification_data,
                    strategy_data=strategy_data,
                    followup_data=followup_data,
                    wb1_profile=wb1_profile,
                    wb1_prompt_preview=wb1_prompt_preview,
                    wb1_form_data=wb1_form_data,
                    wb1_social_profiles=extract_social_profiles(organization.get("notes")),
                    wb1_research_note=extract_research_note(organization.get("notes")),
                )

            return redirect(
                url_for(
                    "organization_detail",
                    organization_id=organization_id,
                    template_name=template_name if form_type in {"outreach_draft", "outreach_regenerate"} else selected_template_name,
                )
            )

        organization = organizations.get(organization_id)
        organization_contacts = contacts.list_by_organization(organization_id)
        organization_messages = messages.list_by_organization(organization_id)
        organization_relationship_memory = relationship_memory.list_by_organization(organization_id)
        qualification_data = extract_qualification_data(organization.get("notes"))
        strategy_data = extract_strategy_data(organization.get("notes"))
        if not any(strategy_data.values()):
            strategy_data = suggest_strategy(
                organization=organization,
                contacts=organization_contacts,
                qualification_data=qualification_data,
            )
        followup_data = extract_followup_data(organization.get("notes"))
        if not any(followup_data.values()):
            followup_data = suggest_followup(
                organization=organization,
                qualification_data=qualification_data,
                strategy_data=strategy_data,
                outreach_history=organization_messages,
            )
        wb1_profile = load_workbot_profile(
            get_active_project_key(),
            "wb1",
            app.config["PROJECTS_ROOT"],
        )
        wb1_prompt_preview = build_contact_hunter_prompt(
            organization_name=str(organization.get("name", "") or ""),
            organization_type=str(organization.get("organization_type", "") or ""),
            city=str(organization.get("city", "") or ""),
            region=str(organization.get("region", "") or ""),
            country=str(organization.get("country", "") or ""),
            website=str(organization.get("website", "") or ""),
            current_email=str(organization.get("email", "") or ""),
            current_phone=str(organization.get("phone", "") or ""),
            existing_contacts=organization_contacts,
            profile=wb1_profile,
        )
        wb1_research_metadata = extract_research_metadata(organization.get("notes"))
        wb1_form_data = {
            "website": str(organization.get("website", "") or ""),
            "general_email": str(organization.get("email", "") or ""),
            "general_phone": str(organization.get("phone", "") or ""),
            "contact_full_name": "",
            "contact_role": "",
            "contact_email": "",
            "contact_phone": "",
            "social_profiles": "\n".join(extract_social_profiles(organization.get("notes"))),
            "research_note": wb1_research_metadata["research_note"],
            "verification_source": wb1_research_metadata["verification_source"],
            "contact_level": wb1_research_metadata["contact_level"],
            "qualification_signals": wb1_research_metadata["qualification_signals"],
        }
        selected_outreach_contact = organization_contacts[0] if organization_contacts else None
        outreach_template_error = ""
        outreach_template_path = ""
        outreach_form_data = {
            "template_name": selected_template_name,
            "contact_id": str(selected_outreach_contact.get("id")) if selected_outreach_contact else "",
            "subject": "",
            "body": "",
        }
        try:
            outreach_draft = build_outreach_draft(
                project_key=str(organization.get("project_key") or get_active_project_key()),
                projects_root=app.config["PROJECTS_ROOT"],
                organization=organization,
                contact=selected_outreach_contact,
                qualification_data=qualification_data,
                template_name=selected_template_name,
            )
        except (FileNotFoundError, ValueError) as error:
            outreach_template_error = str(error)
        else:
            outreach_template_path = outreach_draft.template_path
            outreach_form_data["subject"] = outreach_draft.subject
            outreach_form_data["body"] = outreach_draft.body

        return render_template(
            "organization_detail.html",
            organization=organization,
            organization_quotes=organization_quotes,
            contacts=organization_contacts,
            available_outreach_templates=available_outreach_templates,
            suggested_template=suggested_template,
            selected_template_metadata=selected_template_metadata,
            outreach_history=organization_messages,
            relationship_memory_items=organization_relationship_memory,
            outreach_form_data=outreach_form_data,
            outreach_template_error=outreach_template_error,
            outreach_template_path=outreach_template_path,
            qualification_data=qualification_data,
            strategy_data=strategy_data,
            followup_data=followup_data,
            wb1_profile=wb1_profile,
            wb1_prompt_preview=wb1_prompt_preview,
            wb1_form_data=wb1_form_data,
            wb1_social_profiles=extract_social_profiles(organization.get("notes")),
            wb1_research_note=extract_research_note(organization.get("notes")),
        )

    @app.errorhandler(400)
    def bad_request(error: HTTPException) -> tuple[str, int]:
        app.logger.warning("Bad request", extra={"path": request.path, "description": error.description})
        return (
            render_template(
                "error.html",
                title="Richiesta non valida",
                message=error.description or "La richiesta non e valida.",
            ),
            400,
        )

    @app.errorhandler(404)
    def not_found(error: HTTPException) -> tuple[str, int]:
        app.logger.warning("Resource not found", extra={"path": request.path})
        return (
            render_template(
                "error.html",
                title="Risorsa non trovata",
                message="La pagina o la risorsa richiesta non e disponibile.",
            ),
            404,
        )

    @app.errorhandler(Exception)
    def internal_error(error: Exception) -> tuple[str, int]:
        if isinstance(error, HTTPException):
            raise error
        app.logger.exception("Unhandled application error", extra={"path": request.path})
        return (
            render_template(
                "error.html",
                title="Errore interno",
                message="Si e verificato un errore inatteso. Controlla i log e riprova.",
            ),
            500,
        )

    return app


def _configure_logging(app: Flask) -> None:
    if app.logger.handlers:
        app.logger.setLevel(logging.INFO)
        return

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)


def _candidate_to_line(candidate: dict) -> str:
    parts = [
        candidate.get("name", ""),
        candidate.get("organization_type", "") or "",
        candidate.get("city", "") or "",
        candidate.get("region", "") or "",
        candidate.get("country", "") or "",
        candidate.get("website", "") or "",
        candidate.get("notes", "") or "",
    ]
    return " | ".join(parts)


def _build_import_notes(candidate: dict) -> str | None:
    notes_parts: list[str] = []
    base_notes = str(candidate.get("notes", "") or "").strip()
    qualification_notes = str(candidate.get("qualification_notes", "") or "").strip()
    fit_label = str(candidate.get("fit_label", "") or "").strip()
    website_confirmed = str(candidate.get("website_confirmed", "") or "").strip()
    final_decision = str(candidate.get("final_decision", "") or "").strip()

    if base_notes:
        notes_parts.append(f"WB0 note: {base_notes}")
    if qualification_notes:
        notes_parts.append(f"WB0 qualificazione: {qualification_notes}")
    if fit_label:
        notes_parts.append(f"WB0 fit: {fit_label}")
    if website_confirmed:
        notes_parts.append(f"WB0 sito confermato: {website_confirmed}")
    if final_decision:
        notes_parts.append(f"WB0 decisione: {final_decision}")

    return "\n".join(notes_parts) if notes_parts else None


def _clean_form_value(value: object) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _parse_optional_nonnegative_int(value: str) -> int | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    if not cleaned.isdigit():
        abort(400, description="Il numero dipendenti deve essere un intero non negativo.")
    return int(cleaned)


def _parse_required_positive_float(value: str, error_message: str) -> float:
    try:
        parsed = float(value.strip())
    except ValueError:
        abort(400, description=error_message)
    if parsed <= 0:
        abort(400, description=error_message)
    return parsed


def _parse_required_nonnegative_float(value: str, error_message: str) -> float:
    try:
        parsed = float(value.strip())
    except ValueError:
        abort(400, description=error_message)
    if parsed < 0:
        abort(400, description=error_message)
    return parsed


def _parse_optional_contact_id(contact_id_raw: str, organization_contacts: list[dict[str, object]]) -> int | None:
    cleaned = contact_id_raw.strip()
    if not cleaned:
        return None
    if not cleaned.isdigit():
        abort(400, description="ID contatto non valido per la bozza outreach.")

    contact_id = int(cleaned)
    valid_contact_ids = {int(contact["id"]) for contact in organization_contacts}
    if contact_id not in valid_contact_ids:
        abort(404)
    return contact_id


def _build_outreach_summary(subject: str, organization_name: object) -> str:
    cleaned_subject = subject.strip()
    if cleaned_subject:
        return cleaned_subject[:200]
    return f"Bozza outreach per {organization_name}"


def _resolve_outreach_template_name(
    requested_template_name: str,
    available_templates: list[dict[str, str]],
) -> str:
    available_names = [template["name"] for template in available_templates]
    cleaned = requested_template_name.strip()
    if cleaned and cleaned in available_names:
        return cleaned
    if DEFAULT_TEMPLATE_NAME in available_names:
        return DEFAULT_TEMPLATE_NAME
    if available_names:
        return available_names[0]
    return DEFAULT_TEMPLATE_NAME


def _find_outreach_template_metadata(
    template_name: str,
    available_templates: list[dict[str, object]],
) -> dict[str, object]:
    for template in available_templates:
        if template.get("name") == template_name:
            return template
    return {"name": template_name, "label": template_name, "description": "", "tags": []}


def _build_quote_number(project_key: str) -> str:
    return f"{project_key.upper()}-DRAFT"


def _refresh_quote_totals(
    quote_id: int,
    quotes: QuoteRepository,
    quote_line_items: QuoteLineItemRepository,
) -> None:
    quote = quotes.get(quote_id)
    if quote is None:
        return

    line_items = quote_line_items.list_by_quote(quote_id)
    subtotal_amount = sum(float(item.get("line_total") or 0) for item in line_items)
    discount_amount = float(quote.get("discount_amount") or 0)
    total_amount = subtotal_amount - discount_amount
    quotes.update_amounts(
        quote_id=quote_id,
        subtotal_amount=subtotal_amount,
        discount_amount=discount_amount,
        total_amount=total_amount,
    )
