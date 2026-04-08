Stato
  Ho ricostruito lo stato reale dai file chiave e il punto di ripartenza coincide con quanto hai descritto.

  Il comportamento attuale di WB1 è definito nella UI della scheda organization in 10%20Progetti/20%20CIS/05%20Software/  templates/organization_detail.html:321, nel salvataggio backend in 10%20Progetti/20%20CIS/05%20Software/app/
  __init__.py:631, nella gestione delle note WB1 in 10%20Progetti/20%20CIS/05%20Software/app/wb1_contact_hunter.py:19, e  nel blocco di qualificazione lead in 10%20Progetti/20%20CIS/05%20Software/app/lead_qualification.py:13. I vincoli che
  mi hai chiesto di tenere attivi sono coerenti con 10%20Progetti/20%20CIS/05%20Software/docs/DEVELOPMENT_NOTES.md:35 e
  con il manuale operativo 10%20Progetti/20%20CIS/05%20Software/docs/OPERATIONAL_MANUAL.md:140.

  Nel database reale:

  - Vecomp esiste come organization ethics con sito, email generale e telefono già compilati.
  - Vecomp ha 5 contatti associati già presenti.
  - Vecomp ha una qualificazione lead minima già salvata: fit=alto, priorita=alta, tipo opportunita=da_capire.
  - Vecomp ha un blocco WB1 molto parziale: solo Livello contatto: contatto ponte e Segnali qualificazione: PdR125.
  - FEINAR Srl esiste come organization ethics, ma è ancora ferma sostanzialmente al solo import WB0: niente email,
    niente telefono, nessun contatto, nessun blocco WB1, nessuna qualificazione lead.

  Flusso WB1 pratico
  Il prompt preview non è un dato da salvare: è un brief operativo generato dai dati già presenti della organization,
  dai contatti già associati e dal profilo ethics di WB1 10%20Progetti/20%20CIS/05%20Software/app/
  wb1_contact_hunter.py:19. Dentro ci devono essere:

  - contesto minimo del lead: nome, tipo, territorio, sito/email/telefono già noti
  - ruoli prioritari da cercare
  - fonti da controllare
  - formato risposta atteso per la ricerca assistita

  Fuori dal CIS, per WB1, devi cercare solo 5 cose:

  - sito ufficiale corretto
  - contatto generale verificabile
  - eventuale referente nominativo verificabile
  - ruolo reale del referente
  - uno o più segnali utili alla qualificazione ethics

  Nel form WB1 salvi così 10%20Progetti/20%20CIS/05%20Software/templates/organization_detail.html:354:

  - website, general_email, general_phone: dati della organization
  - contact_full_name, contact_role, contact_email, contact_phone: nuovo contatto associato, se davvero verificato
  - social_profiles: solo social ufficiali
  - verification_source: dove hai verificato
  - contact_level: decision maker, influencer, contatto ponte
  - qualification_signals: leva emersa, es. PdR125, HR, governance
  - research_note: nota breve e concreta su cosa hai verificato

  La differenza tra blocchi è questa:

  - dati organization: anagrafica e canali generali dell’azienda
  - referente: persona associata come contatto
  - note WB1: come hai verificato, quanto è buono il contatto, quali segnali sono emersi
  - qualificazione lead: decisione commerciale sintetica sul lead, separata da WB1 e salvata in un blocco dedicato
    10%20Progetti/20%20CIS/05%20Software/app/lead_qualification.py:42

  Ripartenza
  Su Vecomp, in pratica, risulta già compilato:

  - organization: ok
  - contatti associati: presenti
  - qualificazione minima: presente ma incompleta
  - WB1: presente ma incompleto

  Per considerare Vecomp completata nello Step 6, oggi manca almeno questo:

  - chiarire se uno dei 5 contatti già salvati è davvero il referente migliore oppure no
  - compilare Fonte verifica
  - aggiungere una Note di verifica WB1 vera, non solo metadati
  - salvare eventuali social ufficiali se li hai verificati
  - chiudere la qualificazione lead con tipo opportunita, segnali, prossimo passo, nota

  Quindi per Vecomp ti suggerisco una verifica molto semplice in UI:

  - se non hai un referente certo, lascia i 5 contatti come contatti esplorativi e in WB1 salva contatto ponte
  - compila Fonte verifica con qualcosa di preciso, es. sito ufficiale, pagina contatti, LinkedIn aziendale/profili
    pubblici
  - in Note di verifica WB1 salva una nota breve del tipo: Verificati sito ufficiale, contatti aziendali e segnali
    pubblici su PdR125. Referente nominativo non ancora confermato come owner diretto del tema.
  - nella qualificazione lead porta tipo opportunita da da_capire a cliente solo se vuoi chiuderla come lead cliente già    maturo; altrimenti puoi lasciare da_capire, ma per Step 6 è meno pulito

  Su FEINAR Srl, il passo passo pratico è:

  1. apri la scheda organization
  2. usa il prompt preview come checklist, non come output finale
  3. verifica fuori dal CIS: sito, contatti generali, pagina policy/parità di genere, eventuale team/management,
     LinkedIn aziendale
  4. se trovi solo canale generale, salva comunque email, telefono, fonte verifica, contatto ponte
  5. se trovi un nominativo coerente, aggiungi il contatto dal form WB1
  6. in Segnali qualificazione per partire usa una formula minima come PdR125, HR, partner oppure PdR125, HR, da_capire
  7. chiudi la qualificazione lead con uno di questi esiti:

  - partner se emerge davvero una logica di rete/moltiplicazione
  - cliente se emerge bisogno consulenziale diretto
  - da_capire se vedi entrambi ma non vuoi forzare

  Per chiudere lo Step 6 in modo MVP, la mini-verifica finale dovrebbe essere:

  - ha funzionato: filtro WB0, import pulito, scheda organization per progetto, separazione minima tra WB1 e
    qualificazione lead
  - ha creato attrito: confine poco evidente tra contatti esplorativi, note WB1 e decisione commerciale; Vecomp lo
    mostra bene
  - Step 7 minimo utile: chiarire meglio la routine operativa WB1 e forse rendere più esplicito in UI che WB1 non
    sostituisce la qualificazione lead. Non serve allargare il perimetro MVP.

  Se vuoi, nel prossimo messaggio possiamo fare solo questo, in ordine:

  1. chiusura operativa di Vecomp con i campi esatti da compilare
  2. checklist compilativa di FEINAR Srl pronta da seguire dentro la scheda organization.