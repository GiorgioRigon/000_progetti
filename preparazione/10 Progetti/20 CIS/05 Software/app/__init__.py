from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from werkzeug.exceptions import HTTPException

from app.csv_import import ImportResult, import_leads_csv
from app.data_access import (
    ContactCreate,
    ContactRepository,
    Database,
    OrganizationCreate,
    OrganizationRepository,
)
from app.workbot_profiles import load_workbot_profile
from app.wb1_contact_hunter import (
    build_contact_hunter_prompt,
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
    app.logger.info("CIS app initialized", extra={"db_path": str(database.db_path)})

    @app.get("/")
    def home() -> str:
        return render_template("home.html")

    @app.route("/wb0", methods=["GET", "POST"])
    def wb0_target_discovery() -> str:
        project_key = str(app.config["ACTIVE_PROJECT_KEY"])
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
                                organization_type=request.form.get("organization_type", "").strip() or None,
                                sector=request.form.get("sector", "").strip() or None,
                                city=request.form.get("city", "").strip() or None,
                                region=request.form.get("region", "").strip() or None,
                                country=request.form.get("country", "").strip() or None,
                                website=request.form.get("website", "").strip() or None,
                                email=request.form.get("email", "").strip() or None,
                                phone=request.form.get("phone", "").strip() or None,
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
            organizations=organizations.list_all(),
            import_result=import_result,
        )

    @app.route("/organizations/<int:organization_id>", methods=["GET", "POST"])
    def organization_detail(organization_id: int) -> str:
        organization = organizations.get(organization_id)
        if organization is None:
            abort(404)
        organization_contacts = contacts.list_by_organization(organization_id)

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
                            organization_type=request.form.get("organization_type", "").strip() or None,
                            sector=request.form.get("sector", "").strip() or None,
                            city=request.form.get("city", "").strip() or None,
                            region=request.form.get("region", "").strip() or None,
                            country=request.form.get("country", "").strip() or None,
                            website=request.form.get("website", "").strip() or None,
                            email=request.form.get("email", "").strip() or None,
                            phone=request.form.get("phone", "").strip() or None,
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
                research_note = request.form.get("research_note", "").strip()

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
                            campaign_id=organization["campaign_id"],
                            organization_type=organization["organization_type"],
                            sector=organization["sector"],
                            city=organization["city"],
                            region=organization["region"],
                            country=organization["country"],
                            website=website or organization["website"],
                            phone=general_phone or organization["phone"],
                            email=general_email or organization["email"],
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

            return redirect(url_for("organization_detail", organization_id=organization_id))

        organization = organizations.get(organization_id)
        organization_contacts = contacts.list_by_organization(organization_id)
        wb1_profile = load_workbot_profile(
            str(app.config["ACTIVE_PROJECT_KEY"]),
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
        wb1_form_data = {
            "website": str(organization.get("website", "") or ""),
            "general_email": str(organization.get("email", "") or ""),
            "general_phone": str(organization.get("phone", "") or ""),
            "contact_full_name": "",
            "contact_role": "",
            "contact_email": "",
            "contact_phone": "",
            "social_profiles": "\n".join(extract_social_profiles(organization.get("notes"))),
            "research_note": extract_research_note(organization.get("notes")),
        }

        return render_template(
            "organization_detail.html",
            organization=organization,
            contacts=organization_contacts,
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
