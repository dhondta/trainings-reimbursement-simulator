""" UI copy for every supported language, keyed by language code (see config.LANGUAGE_OPTIONS) and then string id."""

STRINGS = {
    "fr": {
        "language_label": "Langue :",
        "app_title": "Simulateur de remboursement des formations - Loi du 31/07/13, Art. 179",
        "load_label": "Charger un jeu de formations :",
        "preset_placeholder": "Charger un preset…",
        "browse_label": "Importer un CSV",
        "export_label": "Exporter en CSV",
        "export_pdf_label": "Exporter en PDF",
        "upload_error": "Impossible de charger le fichier : {error}",
        "auth_required": "Vous devez être connecté(e) pour charger un fichier.",
        "upload_too_large": "le fichier dépasse la taille maximale de {max_kb} Ko",
        "upload_too_many": "le fichier contient plus de {max} formations",
        "upload_limit_reached": "vous avez atteint la limite de {max} fichiers importés",
        "pdf_rate_limited": "Veuillez patienter {seconds} s avant d'exporter un nouveau PDF.",
        "too_many_courses": "Seules les {max} premières formations sont prises en compte (limite de {max} lignes).",
        "add_row": "Ajouter une ligne",
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
        "explanation_cap_none": "Aucune période n'a encore atteint sa limite de validité de {years} ans "
                                "(Art. 179, §5).",
        "explanation_cap_some": (
            "{n_capped} période(s) ont atteint leur limite de validité de {years} ans et ont vu leur solde restant "
            "remis, en application de l'Art. 179 §5 : {amount} €."
        ),
        "explanation_cap_custom": (
            "Hors loi : la limite de validité d'une période de rendement est fixée à {years} ans au lieu des "
            "{law_years} ans prévus par l'Art. 179, §5."
        ),
        "explanation_min_rate": (
            "Hors loi : un taux de rendement minimal de {rate} €/mois (montant de base, indexé chaque mois comme le "
            "seuil, soit {rate_now} €/mois ce mois-ci, avec l'indice {index} applicable depuis le {index_since}) est "
            "appliqué, ce qui raccourcit la période de rendement (et "
            "accélère la dégression) de {n_shortened} formation(s) moins coûteuse(s)."
        ),
        "explanation_max_rate": (
            "Hors loi : un taux de rendement maximal de {rate} €/mois (montant de base, indexé chaque mois comme le "
            "seuil, soit {rate_now} €/mois ce mois-ci, avec l'indice {index} applicable depuis le {index_since}) est "
            "appliqué, ce qui allonge la période de rendement (et "
            "ralentit la dégression) de {n_lengthened} formation(s) plus coûteuse(s)."
        ),
        "explanation_postpone_remainder": (
            "Hors loi : lorsque le dernier mois d'une période de rendement solderait moins de {amount} € (montant de "
            "base, indexé chaque mois comme le seuil, soit {amount_now} € ce mois-ci), ce reliquat est reporté sur le "
            "mois précédent, ce qui termine la période un mois plus tôt."
        ),
        "departure_label": "Date de départ envisagée :",
        "no_valid_courses": "Aucune formation valide.",
        "total_label": "Total à rembourser",
        "period_label": "Période de rendement",
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
        "expired": "Expiré",
        "departure_marker": "Départ",
        "rate_label": "Taux de rendement",
        "rate_detail": "{code} - {month}",
        "month_abbr": ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."],
        "thousands_sep": "\u00a0",
        "rate_pct": "{pct}% du montant restant",
        "rate_none": "Aucune formation n'est prestée ce mois-ci.",
        "err_missing_code": "Ligne {i} : code de formation manquant.",
        "err_invalid_price": "Ligne {i} ({code}) : prix invalide ({exc}).",
        "err_negative_price": "le prix ne peut pas être négatif",
        "err_invalid_date": "Ligne {i} ({code}) : date invalide ({exc}).",
        "report_title": "Plan de remboursement des formations",
        "report_subtitle": "Départ envisagé le {date} - rapport généré le {today}",
        "report_source": "Jeu de formations : {name}",
        "report_summary": "Synthèse",
        "report_rules": "Règles appliquées (Loi du 31/07/13, Art. 179)",
        "report_courses": "Formations et test du seuil",
        "report_details": "Remboursement par formation au {date}",
        "report_charts": "Graphiques",
        "report_explanation": "Application des critères à cette simulation",
        "report_errors": "Lignes ignorées",
        "report_page": "Page {n}",
        "col_window_cost": "Coût cumulé sur 24 mois (€)",
        "col_threshold": "Seuil indexé (€)",
        "col_triggers": "Déclenche",
        "col_rendement_start": "Début du rendement",
        "col_required": "Mois requis",
        "col_served": "Mois prestés",
        "col_months_remaining": "Mois restants",
        "col_reimbursement": "À rembourser (€)",
        "col_status": "Statut",
        "yes": "Oui",
        "no": "Non",
        "not_taken": "Pas encore suivie",
        "total_row": "Total",
    },
    "nl": {
        "language_label": "Taal:",
        "app_title": "Simulator voor terugbetaling van opleidingen - Wet van 31/07/13, Art. 179",
        "load_label": "Een reeks opleidingen laden:",
        "preset_placeholder": "Een preset laden…",
        "browse_label": "CSV importeren",
        "export_label": "Exporteren naar CSV",
        "export_pdf_label": "Exporteren naar PDF",
        "upload_error": "Kan het bestand niet laden: {error}",
        "auth_required": "U moet aangemeld zijn om een bestand te uploaden.",
        "upload_too_large": "het bestand overschrijdt de maximale grootte van {max_kb} kB",
        "upload_too_many": "het bestand bevat meer dan {max} opleidingen",
        "upload_limit_reached": "u hebt de limiet van {max} geïmporteerde bestanden bereikt",
        "pdf_rate_limited": "Wacht {seconds} s voordat u een nieuwe PDF exporteert.",
        "too_many_courses": "Alleen de eerste {max} opleidingen worden in aanmerking genomen (limiet van {max} rijen).",
        "add_row": "Rij toevoegen",
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
        "explanation_cap_none": "Geen enkele periode heeft nog haar geldigheidslimiet van {years} jaar bereikt "
                                "(Art. 179, §5).",
        "explanation_cap_some": (
            "{n_capped} periode(n) hebben hun geldigheidslimiet van {years} jaar bereikt en hun resterend saldo werd "
            "kwijtgescholden, conform Art. 179 §5: {amount} €."
        ),
        "explanation_cap_custom": (
            "Buiten de wet: de geldigheidslimiet van een rendementsperiode is vastgesteld op {years} jaar in plaats "
            "van de {law_years} jaar voorzien door Art. 179, §5."
        ),
        "explanation_min_rate": (
            "Buiten de wet: er geldt een minimaal rendementspercentage van {rate} €/maand (basisbedrag, elke maand "
            "geïndexeerd zoals de drempel, d.w.z. {rate_now} €/maand deze maand, met de index {index} van toepassing "
            "sinds {index_since}), waardoor de rendementsperiode (en "
            "de degressie) van {n_shortened} goedkopere opleiding(en) korter wordt."
        ),
        "explanation_max_rate": (
            "Buiten de wet: er geldt een maximaal rendementspercentage van {rate} €/maand (basisbedrag, elke maand "
            "geïndexeerd zoals de drempel, d.w.z. {rate_now} €/maand deze maand, met de index {index} van toepassing "
            "sinds {index_since}), waardoor de rendementsperiode (en "
            "de degressie) van {n_lengthened} duurdere opleiding(en) langer wordt."
        ),
        "explanation_postpone_remainder": (
            "Buiten de wet: wanneer de laatste maand van een rendementsperiode minder dan {amount} € zou aflossen "
            "(basisbedrag, elke maand geïndexeerd zoals de drempel, d.w.z. {amount_now} € deze maand), wordt dat "
            "restbedrag bij de vorige maand gevoegd, waardoor de periode een maand vroeger eindigt."
        ),
        "departure_label": "Beoogde vertrekdatum:",
        "no_valid_courses": "Geen geldige opleiding.",
        "total_label": "Terug te betalen bedrag",
        "period_label": "Rendementsperiode",
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
        "expired": "Verlopen",
        "departure_marker": "Vertrek",
        "rate_label": "Rendementspercentage",
        "rate_detail": "{code} - {month}",
        "month_abbr": ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"],
        "thousands_sep": ".",
        "rate_pct": "{pct}% van het resterende bedrag",
        "rate_none": "Geen enkele opleiding wordt deze maand gepresteerd.",
        "err_missing_code": "Rij {i}: opleidingscode ontbreekt.",
        "err_invalid_price": "Rij {i} ({code}): ongeldige prijs ({exc}).",
        "err_negative_price": "de prijs mag niet negatief zijn",
        "err_invalid_date": "Rij {i} ({code}): ongeldige datum ({exc}).",
        "report_title": "Terugbetalingsplan van opleidingen",
        "report_subtitle": "Beoogd vertrek op {date} - rapport gegenereerd op {today}",
        "report_source": "Reeks opleidingen: {name}",
        "report_summary": "Overzicht",
        "report_rules": "Toegepaste regels (Wet van 31/07/13, Art. 179)",
        "report_courses": "Opleidingen en drempeltest",
        "report_details": "Terugbetaling per opleiding op {date}",
        "report_charts": "Grafieken",
        "report_explanation": "Toepassing van de criteria op deze simulatie",
        "report_errors": "Genegeerde rijen",
        "report_page": "Pagina {n}",
        "col_window_cost": "Cumulatieve kost over 24 maanden (€)",
        "col_threshold": "Geïndexeerde drempel (€)",
        "col_triggers": "Activeert",
        "col_rendement_start": "Start rendement",
        "col_required": "Vereiste maanden",
        "col_served": "Maanden gepresteerd",
        "col_months_remaining": "Resterende maanden",
        "col_reimbursement": "Terug te betalen (€)",
        "col_status": "Status",
        "yes": "Ja",
        "no": "Nee",
        "not_taken": "Nog niet gevolgd",
        "total_row": "Totaal",
    },
    "en": {
        "language_label": "Language:",
        "app_title": "Training Reimbursement Simulator - Law of 31/07/13 Art. 179",
        "load_label": "Load a set of courses:",
        "preset_placeholder": "Load a preset…",
        "browse_label": "Import CSV",
        "export_label": "Export CSV",
        "export_pdf_label": "Export PDF",
        "upload_error": "Could not load the file: {error}",
        "auth_required": "You must be signed in to upload a file.",
        "upload_too_large": "the file exceeds the maximum size of {max_kb} KB",
        "upload_too_many": "the file contains more than {max} courses",
        "upload_limit_reached": "you have reached the limit of {max} imported files",
        "pdf_rate_limited": "Please wait {seconds} s before exporting another PDF.",
        "too_many_courses": "Only the first {max} courses are taken into account (limit of {max} rows).",
        "add_row": "Add row",
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
        "explanation_cap_none": "No period has yet reached its {years}-year validity limit (Art. 179, §5).",
        "explanation_cap_some": (
            "{n_capped} period(s) have reached their {years}-year validity limit and had their remaining balance "
            "forgiven, per Art. 179 §5: {amount} €."
        ),
        "explanation_cap_custom": (
            "Beyond the law: the validity limit of a rendement period is set to {years} years instead of the "
            "{law_years} years provided by Art. 179, §5."
        ),
        "explanation_min_rate": (
            "Beyond the law: a minimum rendement rate of {rate} €/month (base amount, indexed every month like the "
            "threshold, i.e. {rate_now} €/month this month, with the index value {index} applicable since "
            "{index_since}) is applied, which shortens the rendement period (and "
            "speeds up the degression) of {n_shortened} cheaper course(s)."
        ),
        "explanation_max_rate": (
            "Beyond the law: a maximum rendement rate of {rate} €/month (base amount, indexed every month like the "
            "threshold, i.e. {rate_now} €/month this month, with the index value {index} applicable since "
            "{index_since}) is applied, which lengthens the rendement period (and "
            "slows down the degression) of {n_lengthened} more expensive course(s)."
        ),
        "explanation_postpone_remainder": (
            "Beyond the law: when the last month of a rendement period would pay off less than {amount} € (base "
            "amount, indexed every month like the threshold, i.e. {amount_now} € this month), this remainder is merged "
            "into the previous month, which ends the period one month earlier."
        ),
        "departure_label": "Planned departure date:",
        "no_valid_courses": "No valid course.",
        "total_label": "Total to reimburse",
        "period_label": "Rendement period",
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
        "expired": "Expired",
        "departure_marker": "Departure",
        "rate_label": "Rendement rate",
        "rate_detail": "{code} - {month}",
        "month_abbr": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "thousands_sep": ",",
        "rate_pct": "{pct}% of the remaining amount",
        "rate_none": "No course is being served this month.",
        "err_missing_code": "Row {i}: missing course code.",
        "err_invalid_price": "Row {i} ({code}): invalid price ({exc}).",
        "err_negative_price": "the price cannot be negative",
        "err_invalid_date": "Row {i} ({code}): invalid date ({exc}).",
        "report_title": "Training reimbursement plan",
        "report_subtitle": "Planned departure on {date} - report generated on {today}",
        "report_source": "Course set: {name}",
        "report_summary": "Summary",
        "report_rules": "Rules applied (Law of 31/07/13, Art. 179)",
        "report_courses": "Courses and threshold test",
        "report_details": "Reimbursement per course on {date}",
        "report_charts": "Charts",
        "report_explanation": "How these criteria apply to this simulation",
        "report_errors": "Ignored rows",
        "report_page": "Page {n}",
        "col_window_cost": "24-month cumulative cost (€)",
        "col_threshold": "Indexed threshold (€)",
        "col_triggers": "Triggers",
        "col_rendement_start": "Rendement start",
        "col_required": "Required months",
        "col_served": "Months served",
        "col_months_remaining": "Months remaining",
        "col_reimbursement": "To reimburse (€)",
        "col_status": "Status",
        "yes": "Yes",
        "no": "No",
        "not_taken": "Not yet taken",
        "total_row": "Total",
    },
}

