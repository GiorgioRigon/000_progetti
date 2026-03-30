# Prompt Ripresa Step 6

```text
Sto riprendendo il progetto CIS esattamente da questo punto.

Prima di fare qualunque modifica:
1. leggi i file esistenti rilevanti
2. usa anche docs/DEVELOPMENT_NOTES.md come memoria operativa del progetto
3. ricostruisci in modo sintetico lo stato attuale
4. confermami da quale punto preciso ripartiamo

Leggi in questo ordine:
- 10 Progetti/20 CIS/04 Roadmap/05 Roadmap 2 settimane profili WB.md
- 10 Progetti/20 CIS/05 Software/docs/DEVELOPMENT_NOTES.md
- 10 Progetti/20 CIS/05 Software/docs/OPERATIONAL_MANUAL.md
- 10 Progetti/20 CIS/05 Software/app/__init__.py
- 10 Progetti/20 CIS/05 Software/app/data_access.py
- 10 Progetti/20 CIS/05 Software/app/csv_import.py
- 10 Progetti/20 CIS/05 Software/app/project_registry.py
- 10 Progetti/20 CIS/05 Software/app/workbot_profiles.py
- 10 Progetti/20 CIS/05 Software/app/wb0_target_discovery.py
- 10 Progetti/20 CIS/05 Software/app/wb1_contact_hunter.py
- 10 Progetti/20 CIS/05 Software/app/lead_qualification.py
- 10 Progetti/20 CIS/05 Software/projects/melodema/project_config.yaml
- 10 Progetti/20 CIS/05 Software/projects/melodema/workbot_profiles.json
- 10 Progetti/20 CIS/05 Software/projects/ethics/project_config.yaml
- 10 Progetti/20 CIS/05 Software/projects/ethics/workbot_profiles.json
- 10 Progetti/20 CIS/05 Software/templates/base.html
- 10 Progetti/20 CIS/05 Software/templates/home.html
- 10 Progetti/20 CIS/05 Software/templates/organizations.html
- 10 Progetti/20 CIS/05 Software/templates/organizations_table.html
- 10 Progetti/20 CIS/05 Software/templates/organization_detail.html
- 10 Progetti/20 CIS/05 Software/templates/wb0_target_discovery.html
- 10 Progetti/20 CIS/05 Software/static/style.css
- 10 Progetti/20 CIS/05 Software/tests/test_data_access.py
- 10 Progetti/20 CIS/05 Software/tests/test_manual_flow.py
- 10 Progetti/20 CIS/05 Software/tests/test_wb0_target_discovery.py
- 10 Progetti/20 CIS/05 Software/tests/test_wb1_contact_hunter.py
- 10 Progetti/20 CIS/05 Software/tests/test_workbot_profiles.py
- 10 Progetti/20 CIS/05 Software/tests/test_project_registry.py
- 10 Progetti/20 CIS/05 Software/tests/test_lead_qualification.py

Vincoli da rispettare:
- non cambiare il perimetro MVP senza dirlo esplicitamente
- mantieni approccio semplice e leggibile
- database unico CIS
- human in the loop sempre attivo
- usa docs/DEVELOPMENT_NOTES.md come memoria operativa del progetto
- se aggiungi decisioni o idee rilevanti, salvale anche li

Contesto attuale da ricordare:
- esiste ora un selettore del progetto attivo in UI
- i progetti attivi di riferimento sono almeno melodema ed ethics
- il progetto consulenza_certificazione è stato rinominato in ethics
- WB0 e WB1 leggono profili operativi per progetto
- WB1 è stato rifinito con prompt/input più guidati
- WB0 è stato rifinito con prompt preview e review più guidati
- esiste una qualificazione lead minima comune, salvata nelle note organization
- organizations ora ha project_key e la lista Organizations è filtrata per progetto attivo
- le organization esistenti vanno considerate appartenenti a melodema
- esiste una Organizations Table separata, semplice e leggibile
- la home è più stretta, le pagine operative sono più larghe, la tabella è la più larga
- il prossimo step della roadmap è lo Step 6: prova operativa reale sul progetto ethics

Dopo la lettura:
1. riassumi lo stato attuale in modo breve
2. dimmi se confermi che ripartiamo dallo Step 6
3. proponi un piano operativo molto concreto per lo Step 6 su ethics
4. attendi il mio via prima di modificare
```
