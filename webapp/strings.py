""" UI copy for every supported language, keyed by language code (see config.LANGUAGE_OPTIONS) and then string id."""

STRINGS = {
    "fr": {
        "language_label": "Langue :",
        "app_title": "Simulateur de remboursement des formations - Loi du 31/07/13, Art. 179",
        "load_label": "Charger un jeu de formations :",
        "preset_placeholder": "Charger un preset…",
        "browse_label": "Parcourir…",
        "upload_error": "Impossible de charger le fichier : {error}",
        "auth_required": "Vous devez être connecté(e) pour charger un fichier.",
        "add_row": "Ajouter une ligne",
        "move_up_label": "▲ Monter",
        "move_down_label": "▼ Descendre",
        "move_no_selection": "Sélectionnez d'abord une ligne (bouton radio à gauche) pour la déplacer.",
        "col_course": "Formation",
        "col_price": "Prix (€)",
        "col_end_date": "Date de fin (jj/mm/aaaa)",
        "law_criteria": [
            "Une clause de formation est déclenchée dès que le coût cumulé des formations suivies sur une "
            "fenêtre glissante de 24 mois dépasse un seuil indexé (base de 5 000 €, indexée depuis 2013).",
            "Une fois déclenchée, le travailleur doit 24 mois de « rendement » (service) après cette formation ; "
            "partir avant la fin de cette période implique de rembourser un montant dégressif "
            "(prix × mois restants / 24).",
            "Lorsque les périodes de rendement de plusieurs formations se chevauchent, seule la plus récente "
            "compte comme du service chaque mois - les plus anciennes restent suspendues jusqu'à ce qu'elle "
            "soit totalement prestée.",
            "Selon le §5, cette obligation s'éteint totalement après 15 ans depuis le début de la période, "
            "quel que soit le solde restant.",
        ],
        "explanation_title": "Application des critères à cette simulation",
        "explanation_threshold": (
            "{n_triggering} formation(s) sur {n_total} dépassent le seuil indexé de coût cumulé sur leur "
            "fenêtre glissante de 24 mois et déclenchent l'obligation : {codes}."
        ),
        "explanation_rendement": (
            "Chaque formation déclenchante requiert 24 mois de rendement ; le remboursement vaut "
            "prix × mois restants / 24. Au {date}, {n_owing} formation(s) présentent encore un solde, pour un "
            "total de {total} €."
        ),
        "explanation_priority": (
            "Les périodes de rendement se chevauchant, seule la plus récente compte comme prestée chaque mois. "
            "Au {date}, {n_active} période(s) sont activement prestées et {n_suspended} sont suspendues "
            "derrière une formation plus récente."
        ),
        "explanation_cap_none": "Aucune période n'a encore atteint sa limite de validité de 15 ans (Art. 179, §5).",
        "explanation_cap_some": (
            "{n_capped} période(s) ont atteint leur limite de validité de 15 ans et ont vu leur solde restant "
            "remis, en application de l'Art. 179 §5 : {amount} €."
        ),
        "departure_label": "Date de départ envisagée :",
        "no_valid_courses": "Aucune formation valide.",
        "total_label": "Total à rembourser (au {date})",
        "final_date_label": "Date de fin du rendement",
        "final_date_none": "Aucune formation ne déclenche l'obligation.",
        "bar_title_default": "Montant dégressif à rembourser par formation",
        "bar_title": "Montant dégressif à rembourser par formation (au {date})",
        "bar_title_none": "Montant dégressif à rembourser par formation (aucune formation ne déclenche l'obligation)",
        "timeline_title_default": "Périodes de rendement (24 mois)",
        "timeline_title": "Périodes de rendement (24 mois de service requis après chaque formation déclenchante)",
        "xaxis_course": "Formation",
        "yaxis_amount": "Montant à rembourser (€)",
        "xaxis_date": "Date",
        "yaxis_course": "Formation",
        "served": "Presté",
        "suspended": "Suspendu",
        "remaining": "Restant",
        "departure_marker": "Départ",
        "rate_label": "Taux de rendement (mois suivant)",
        "rate_detail": "{code} - {month}",
        "rate_pct": "{pct}% du montant restant",
        "rate_none": "Aucune formation n'est prestée le mois suivant.",
        "err_missing_code": "Ligne {i} : code de formation manquant.",
        "err_invalid_price": "Ligne {i} ({code}) : prix invalide ({exc}).",
        "err_invalid_date": "Ligne {i} ({code}) : date invalide ({exc}).",
    },
    "nl": {
        "language_label": "Taal:",
        "app_title": "Simulator voor terugbetaling van opleidingen - Wet van 31/07/13, Art. 179",
        "load_label": "Een reeks opleidingen laden:",
        "preset_placeholder": "Een preset laden…",
        "browse_label": "Bladeren…",
        "upload_error": "Kan het bestand niet laden: {error}",
        "auth_required": "U moet aangemeld zijn om een bestand te uploaden.",
        "add_row": "Rij toevoegen",
        "move_up_label": "▲ Omhoog",
        "move_down_label": "▼ Omlaag",
        "move_no_selection": "Selecteer eerst een rij (keuzerondje links) om te verplaatsen.",
        "col_course": "Opleiding",
        "col_price": "Prijs (€)",
        "col_end_date": "Einddatum (dd/mm/jjjj)",
        "law_criteria": [
            "Een opleidingsbeding wordt geactiveerd zodra de cumulatieve kost van opleidingen binnen een "
            "glijdend venster van 24 maanden een geïndexeerde drempel overschrijdt (basis van € 5.000, "
            "geïndexeerd sinds 2013).",
            "Eenmaal geactiveerd, is de werknemer 24 maanden \"rendement\" (dienst) verschuldigd na die "
            "opleiding; vertrekken voordat die periode voltooid is, houdt in dat een degressief bedrag moet "
            "worden terugbetaald (prijs × resterende maanden / 24).",
            "Wanneer de rendementsperiodes van meerdere opleidingen elkaar overlappen, telt enkel de meest "
            "recente als dienst per maand - de oudere blijven geschorst tot ze volledig is gepresteerd.",
            "Volgens §5 vervalt deze verplichting volledig na 15 jaar vanaf de start van de periode, ongeacht "
            "het resterende saldo.",
        ],
        "explanation_title": "Toepassing van de criteria op deze simulatie",
        "explanation_threshold": (
            "{n_triggering} van de {n_total} opleiding(en) overschrijden de geïndexeerde drempel van "
            "cumulatieve kost binnen hun glijdend venster van 24 maanden en activeren de verplichting: {codes}."
        ),
        "explanation_rendement": (
            "Elke activerende opleiding vereist 24 maanden rendement; de terugbetaling is "
            "prijs × resterende maanden / 24. Op {date} hebben {n_owing} opleiding(en) nog een saldo, voor een "
            "totaal van {total} €."
        ),
        "explanation_priority": (
            "Omdat de rendementsperiodes elkaar overlappen, telt enkel de meest recente als gepresteerd per "
            "maand. Op {date} worden {n_active} periode(n) actief gepresteerd en zijn {n_suspended} geschorst "
            "achter een recentere opleiding."
        ),
        "explanation_cap_none": "Geen enkele periode heeft nog haar geldigheidslimiet van 15 jaar bereikt (Art. 179, §5).",
        "explanation_cap_some": (
            "{n_capped} periode(n) hebben hun geldigheidslimiet van 15 jaar bereikt en hun resterend saldo werd "
            "kwijtgescholden, conform Art. 179 §5: {amount} €."
        ),
        "departure_label": "Beoogde vertrekdatum:",
        "no_valid_courses": "Geen geldige opleiding.",
        "total_label": "Terug te betalen bedrag (op {date})",
        "final_date_label": "Einddatum van het rendement",
        "final_date_none": "Geen enkele opleiding activeert de verplichting.",
        "bar_title_default": "Degressief terug te betalen bedrag per opleiding",
        "bar_title": "Degressief terug te betalen bedrag per opleiding (op {date})",
        "bar_title_none": "Degressief terug te betalen bedrag per opleiding (geen enkele opleiding activeert de verplichting)",
        "timeline_title_default": "Rendementsperiodes (24 maanden)",
        "timeline_title": "Rendementsperiodes (24 maanden dienst vereist na elke activerende opleiding)",
        "xaxis_course": "Opleiding",
        "yaxis_amount": "Terug te betalen bedrag (€)",
        "xaxis_date": "Datum",
        "yaxis_course": "Opleiding",
        "served": "Gepresteerd",
        "suspended": "Geschorst",
        "remaining": "Resterend",
        "departure_marker": "Vertrek",
        "rate_label": "Rendementspercentage (volgende maand)",
        "rate_detail": "{code} - {month}",
        "rate_pct": "{pct}% van het resterende bedrag",
        "rate_none": "Geen enkele opleiding wordt de volgende maand gepresteerd.",
        "err_missing_code": "Rij {i}: opleidingscode ontbreekt.",
        "err_invalid_price": "Rij {i} ({code}): ongeldige prijs ({exc}).",
        "err_invalid_date": "Rij {i} ({code}): ongeldige datum ({exc}).",
    },
    "en": {
        "language_label": "Language:",
        "app_title": "Training Reimbursement Simulator - Law of 31/07/13 Art. 179",
        "load_label": "Load a set of courses:",
        "preset_placeholder": "Load a preset…",
        "browse_label": "Browse…",
        "upload_error": "Could not load the file: {error}",
        "auth_required": "You must be signed in to upload a file.",
        "add_row": "Add row",
        "move_up_label": "▲ Move up",
        "move_down_label": "▼ Move down",
        "move_no_selection": "Select a row first (radio button on the left) to move it.",
        "col_course": "Course",
        "col_price": "Price (€)",
        "col_end_date": "End date (dd/mm/yyyy)",
        "law_criteria": [
            "A training clause is triggered whenever the cumulative cost of trainings completed within a "
            "rolling 24-month window exceeds an indexed threshold (€5,000 base, indexed since 2013).",
            "Once triggered, the employee owes 24 months of \"rendement\" (service) after that training; "
            "leaving before completing it means reimbursing a degressively reduced amount "
            "(price × months still owed / 24).",
            "When several trainings' rendement periods overlap, only the most recent one counts as service "
            "each month - older ones stay suspended until it is fully served.",
            "Per §5, this obligation lapses entirely after 15 years from the start of the period, whatever "
            "remains unserved.",
        ],
        "explanation_title": "How these criteria apply to this simulation",
        "explanation_threshold": (
            "{n_triggering} of {n_total} course(s) exceed the indexed cumulative-cost threshold within their "
            "trailing 24-month window and trigger the obligation: {codes}."
        ),
        "explanation_rendement": (
            "Each triggering course requires 24 months of rendement; reimbursement equals "
            "price × months remaining / 24. As of {date}, {n_owing} course(s) still carry a balance, "
            "totalling {total} €."
        ),
        "explanation_priority": (
            "Because rendement periods overlap, only the most recently triggered course accrues service each "
            "month. As of {date}, {n_active} period(s) are actively accruing service and {n_suspended} are "
            "suspended behind a more recent one."
        ),
        "explanation_cap_none": "No period has yet reached its 15-year validity limit (Art. 179, §5).",
        "explanation_cap_some": (
            "{n_capped} period(s) have reached their 15-year validity limit and had their remaining balance "
            "forgiven, per Art. 179 §5: {amount} €."
        ),
        "departure_label": "Planned departure date:",
        "no_valid_courses": "No valid course.",
        "total_label": "Total to reimburse (on {date})",
        "final_date_label": "Final rendement end date",
        "final_date_none": "No course triggers the obligation.",
        "bar_title_default": "Degressive amount to reimburse per course",
        "bar_title": "Degressive amount to reimburse per course (on {date})",
        "bar_title_none": "Degressive amount to reimburse per course (no course triggers the obligation)",
        "timeline_title_default": "Rendement periods (24 months)",
        "timeline_title": "Rendement periods (24 months of service required after each triggering course)",
        "xaxis_course": "Course",
        "yaxis_amount": "Amount to reimburse (€)",
        "xaxis_date": "Date",
        "yaxis_course": "Course",
        "served": "Served",
        "suspended": "Suspended",
        "remaining": "Remaining",
        "departure_marker": "Departure",
        "rate_label": "Rendement rate (next month)",
        "rate_detail": "{code} - {month}",
        "rate_pct": "{pct}% of the remaining amount",
        "rate_none": "No course is being served next month.",
        "err_missing_code": "Row {i}: missing course code.",
        "err_invalid_price": "Row {i} ({code}): invalid price ({exc}).",
        "err_invalid_date": "Row {i} ({code}): invalid date ({exc}).",
    },
}

