 Facciamo un test operativo reale su ethics senza cambiare il perimetro MVP. L’obiettivo è validare il flusso completo:

  progetto attivo ethics -> WB0 -> review -> import -> WB1 -> qualificazione lead -> prossimo passo

  Partiamo con un test piccolo ma reale:

  - 1 run WB0
  - 5 candidate
  - 2 o 3 import nel CIS
  - WB1 su 2 lead
  - qualificazione minima salvata su tutti i lead importati

  Passo 1

  Apri il CIS e imposta ethics come progetto attivo dal selettore in alto.

  Quando l’hai fatto, verifica due cose:

  - in Home o Organizations vedi Progetto attivo: ethics
  - la lista Organizations, se già contiene dati, mostra solo lead del progetto ethics

  Se è tutto ok, passiamo al WB0.

  Passo 2

  Apri WB0 e compila un run molto focalizzato. Ti consiglio questo primo scenario:

  - obiettivo: trovare aziende italiane con segnali pubblici utili per consulenza PdR125
  - territorio: Italia
  - target types:

  aziende
  gruppi aziendali
  PMI strutturate

  - fonti: seleziona solo quelle più adatte che trovi disponibili
  - criterio pratico: non cercare “chiunque parli di ESG”, ma realtà con segnali abbastanza concreti

  Puoi usare questo testo iniziale nei campi.

  Obiettivo ricerca

  Trovare aziende italiane realisticamente qualificabili e contattabili per servizi di consulenza su PdR125, parita di genere e temi collegati a HR, ESG, governance e compliance.

  Contesto progetto

  Ethics offre consulenza su PdR125 e percorsi collegati a parita di genere, HR, ESG, governance e compliance. Cerchiamo lead con segnali pubblici concreti e verificabili, maturita organizzativa sufficiente e possibile bisogno
  consulenziale reale.

  Territorio target

  Italia

  Tipi di target

  aziende
  gruppi aziendali
  PMI strutturate

  Criteri di inclusione

  presenza di contenuti pubblici su parita di genere, diversity, ESG, CSR o compliance
  presenza di funzioni HR, people, ESG, governance o compliance chiaramente visibili
  sito ufficiale chiaro con elementi verificabili
  maturita organizzativa compatibile con un percorso consulenziale

  Criteri di esclusione

  sito povero o non verificabile
  segnali troppo generici e non operativi
  organizzazione troppo piccola o destrutturata
  nessun referente plausibile o nessuna funzione coerente individuabile

  Per Prompt di ricerca, tienilo diretto. Usa questo:

  Cerca aziende italiane con segnali pubblici concreti di interesse o maturita su parita di genere, PdR125, ESG, diversity, HR o governance. Restituisci solo organizzazioni con sito ufficiale verificabile e una breve evidenza del
  possibile fit consulenziale.

  Passo 3

  Ora devi popolare Candidate organizations con 5 righe, una per lead. Formato:

  nome | tipo | citta | regione | paese | sito | nota fit o evidenza

  Esempio fittizio del formato:

  Azienda Alfa | azienda | Milano | Lombardia | Italia | https://www.aziendaalfa.it | Pagina ESG e policy DEI pubbliche, funzione HR visibile

  Regola per questo test:

  - inserisci solo 5 candidate
  - tutte con sito ufficiale
  - tutte con una nota molto concreta, non vaga