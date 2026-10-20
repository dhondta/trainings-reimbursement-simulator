""" UI copy for every supported language, keyed by language code (see config.LANGUAGE_OPTIONS) and then string id."""

STRINGS = {
    "fr": {
        "language_label": "Langue :",
        "app_title": "Simulateur de remboursement des formations",
        "app_subtitle": "Art. 179 de la loi du 28/02/2007, tel que remplacé par la loi du 31/07/2013",
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
        "col_bundle": "Groupe (facultatif)",
        "col_start_date": "Début de non-activité (jj/mm/aaaa)",
        "law_criteria": [
            "Une formation suivie aux frais de la Défense déclenche une période de rendement dès que le coût "
            "cumulé des formations sur une fenêtre glissante de 24 mois dépasse un seuil indexé (base de "
            "5 000 €, liée à l'indice-pivot 138,01).",
            "Le militaire doit alors 24 mois de « rendement » (service) après cette formation ; quitter les "
            "Forces armées avant la fin de cette période implique de rembourser un montant dégressif "
            "(prix × mois restants / 24).",
            "Lorsque les périodes de rendement de plusieurs formations se chevauchent, seule la plus récente "
            "compte comme du service chaque mois - les plus anciennes restent suspendues jusqu'à ce qu'elle "
            "soit totalement prestée.",
            "Selon le §5, les périodes de rendement de plusieurs formations sont cumulées, et la période totale "
            "de rendement ne peut excéder 15 ans : au-delà, le solde restant est remis (compté par groupe de "
            "périodes cumulées ou par période de rendement, selon le choix).",
            "Selon le §6, la période de rendement en cours est suspendue tant que le militaire est en "
            "non-activité (une ligne avec une date de début et sans prix).",
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
        "explanation_cap_none": (
            "Aucun solde n'est remis en application de la limite de {years} ans des périodes de rendement "
            "cumulées (Art. 179, §5)."
        ),
        "explanation_cap_some": (
            "En application de la limite de {years} ans des périodes de rendement cumulées (Art. 179, §5), "
            "{amount} € sont remis sur {n_capped} période(s)."
        ),
        "explanation_cap_custom": (
            "Hors loi : la période totale de rendement cumulée est limitée à {years} ans au lieu des {law_years} "
            "ans prévus par l'Art. 179, §5."
        ),
        "explanation_mode_bunch": (
            "Selon le choix, la limite de {years} ans est comptée par groupe de périodes de rendement cumulées, "
            "prestées l'une après l'autre sans interruption : {bunch} mois sont prestés dans le groupe en cours "
            "au {date}{reached}."
        ),
        "explanation_mode_period": (
            "Selon le choix, la limite de {years} ans est comptée par période de rendement, à partir de son début "
            "(suspensions comprises, hors non-activité) : {n_reached} période(s) l'ont atteinte au {date}{next}."
        ),
        "explanation_mode_reached": " - les {years} ans ont été atteints le {when}",
        "explanation_mode_will_reach": " - les {years} ans seront atteints le {when}",
        "explanation_mode_next": " - la suivante, {code}, l'atteindra le {when}",
        "explanation_mode_compare": (
            "Selon l'autre lecture ({other}), {total} € seraient dus au {date}, au lieu de {current} €."
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
        "explanation_inactivity": (
            "{months} mois de non-activité ({labels}) suspendent la période de rendement en cours (§6) - un mois "
            "touché, même en partie, n'est pas presté."
        ),
        "inactivity_default": "Non-activité",
        "departure_label": "Date de départ envisagée :",
        "full_schedule_switch": "Calendrier complet, sans la limite de {years} ans (Art. 179, §5)",
        "unbundled_switch": "Comparer avec les formations non groupées",
        "theme_toggle": "Mode nuit",
        "tour_toggle": "Visite guidée",
        "tour": {
            "next": "Suivant", "prev": "Précédent", "done": "Terminer", "progress": "{{current}} sur {{total}}",
            "hint": "Cliquez ici pour une visite guidée",
            "steps": {
                "rules": ["Les règles",
                          "Voici les critères de l'Art. 179 appliqués par le simulateur : quand une formation "
                          "déclenche une période de rendement, combien de temps elle dure, et ce qui est dû en partant"
                          " avant son terme."],
                "preset": ["Charger un preset",
                           "Choisissez un ensemble de formations dans la liste : les exemples fournis, et les fichiers"
                           " CSV que vous avez importés."],
                "import": ["Importer un CSV",
                           "Chargez votre propre liste de formations depuis un fichier CSV (Course, Price, End Date, "
                           "et facultativement Bundle et Start Date). Il est conservé dans votre dossier privé pour "
                           "vos prochaines sessions."],
                "export": ["Exporter en CSV",
                           "Téléchargez le tableau tel qu'il est, dans le même format CSV, pour le modifier ailleurs "
                           "ou le réimporter plus tard."],
                "pdf": ["Exporter en PDF",
                        "Téléchargez le plan de remboursement à la date de départ choisie : chiffres clés, test du "
                        "seuil, montant dû par formation, les deux graphiques et l'explication."],
                "add_row": ["Ajouter une ligne",
                            "Ajoutez une formation au bas du tableau, puis complétez son code, son prix et sa date de "
                            "fin (une ligne avec une date de début et sans prix est une période de non-activité). "
                            "Chaque ligne peut être supprimée avec × ; le tableau reste trié par date de fin."],
                "slider_start": ["Date de départ envisagée",
                                 "Déplacez le curseur pour choisir quand vous quitteriez les Forces armées. Au début "
                                 "de la première période de rendement ({date}), seules les formations déjà suivies "
                                 "sont dues, encore en entier : {total}."],
                "slider_middle": ["À mi-parcours",
                                  "Plus tard ({date}), une partie du rendement a été prestée, et le montant dû a "
                                  "diminué : {total}."],
                "slider_end": ["Entièrement soldé",
                               "Au bout du curseur ({date}), chaque période de rendement est prestée ou remise : "
                               "{total}."],
                "cap_bunch": ["La limite de {years} ans, par groupe",
                              "Au-delà de {years} ans de périodes de rendement cumulées, le reste est remis (Art. 179,"
                              " §5). Comptée par groupe de périodes qui se suivent sans interruption, le total au "
                              "{date} est de {total}."],
                "cap_period": ["La limite de {years} ans, par période",
                               "Comptée plutôt par période de rendement, chaque période est limitée séparément : le "
                               "total au {date} devient {total}."],
                "bar": ["Montant par formation",
                        "Le montant dégressif encore dû par formation à la date de départ : en rouge s'il est encore "
                        "dû, en gris clair s'il est remis, en vert une fois entièrement presté."],
                "figures": ["Chiffres clés",
                            "La période de rendement complète, le total à rembourser à la date de départ, et le "
                            "rendement presté ce mois-ci, par la formation en cours de prestation."],
                "timeline": ["Périodes de rendement",
                             "La période de rendement de chaque formation, mois par mois : prestée (vert), suspendue "
                             "derrière une formation plus récente (gris), et restant à prester après la date de départ"
                             " (rouge)."],
                "full_schedule": ["Calendrier complet",
                                  "Ce commutateur montre les périodes telles qu'elles auraient été sans la limite de "
                                  "{years} ans : les mois remis apparaissent en gris clair, avec le montant remis."],
                "unbundled": ["Formations non groupées",
                              "Ce commutateur compare les formations groupées aux mêmes formations prises séparément :"
                              " les lignes foncées montrent les périodes de rendement qu'elles auraient eues, pleines "
                              "quand elles sont prestées, pointillées quand elles sont suspendues."],
                "unbundled_none": ["Formations non groupées",
                                   "Ce commutateur compare les formations groupées aux mêmes formations prises "
                                   "séparément. Il est disponible dès que le tableau contient un groupe (la colonne "
                                   "facultative Bundle)."],
                "explanation": ["Explication",
                                "Enfin, comment les règles s'appliquent à cette simulation, avec ses propres chiffres "
                                "à la date de départ. Vous pouvez relancer cette visite à tout moment avec le bouton ?"
                                " en haut de la page."],
            },
        },
        "unbundled_legend": "Formations non groupées (total : {amount} €)",
        "unbundled_none": "ne déclenche pas l'obligation seule",
        "unbundled_owed": "{amount} € à rembourser au {date}",
        "cap_mode_label": "Limite de {years} ans (Art. 179, §5) :",
        "cap_mode_options": {"bunch": "par groupe de périodes cumulées", "period": "par période de rendement"},
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
        "expired": "Remis",
        "lapsed": "Suspendu, remis",
        "inactive": "Non-activité",
        "departure_marker": "Départ",
        "rate_label": "Taux de rendement",
        "rate_detail": "{code} - {month}",
        "month_abbr": ["janv.",
                       "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."],
        "thousands_sep": "\u00a0",
        "rate_pct": "{pct}% du montant restant",
        "rate_none": "Aucune formation n'est prestée ce mois-ci.",
        "err_missing_code": "Ligne {i} : code de formation manquant.",
        "err_invalid_price": "Ligne {i} ({code}) : prix invalide ({exc}).",
        "err_negative_price": "le prix ne peut pas être négatif",
        "err_invalid_date": "Ligne {i} ({code}) : date invalide ({exc}).",
        "err_bundle_name": "Groupe(s) portant le nom d'une formation hors du groupe, ignoré(s) : {names}.",
        "err_inactivity_fields": "Ligne {i} ({code}) : une période de non-activité n'a ni prix ni groupe.",
        "err_inactivity_dates": "Ligne {i} ({code}) : une période de non-activité ne peut finir avant de commencer.",
        "report_title": "Plan de remboursement des formations",
        "report_subtitle": "Départ envisagé le {date} - rapport généré le {today}",
        "report_source": "Jeu de formations : {name}",
        "report_summary": "Synthèse",
        "report_rules": (
            "Règles appliquées (Art. 179 de la loi du 28/02/2007, "
            "tel que remplacé par la loi du 31/07/2013)"
        ),
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
        "app_title": "Simulator voor terugbetaling van opleidingen",
        "app_subtitle": "Art. 179 van de wet van 28/02/2007, zoals vervangen door de wet van 31/07/2013",
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
        "col_bundle": "Bundel (optioneel)",
        "col_start_date": "Begin non-activiteit (dd/mm/jjjj)",
        "law_criteria": [
            "Een opleiding gevolgd op kosten van Defensie activeert een rendementsperiode zodra de "
            "gecumuleerde kost van opleidingen binnen een glijdend venster van 24 maanden een geïndexeerde "
            "drempel overschrijdt (basis van € 5.000, gekoppeld aan de spilindex 138,01).",
            "De militair is dan 24 maanden \"rendement\" (dienst) verschuldigd na die opleiding; de "
            "Krijgsmacht verlaten voordat die periode voltooid is, houdt in dat een degressief bedrag moet "
            "worden terugbetaald (prijs × resterende maanden / 24).",
            "Wanneer de rendementsperiodes van meerdere opleidingen elkaar overlappen, telt enkel de meest "
            "recente als dienst per maand - de oudere blijven geschorst tot ze volledig is gepresteerd.",
            "Volgens §5 worden de rendementsperiodes van meerdere opleidingen gecumuleerd, en mag de totale "
            "rendementsperiode 15 jaar niet overschrijden: daarna wordt het resterende saldo kwijtgescholden "
            "(geteld per groep van gecumuleerde periodes of per rendementsperiode, volgens de keuze).",
            "Volgens §6 wordt de lopende rendementsperiode geschorst zolang de militair in non-activiteit "
            "is (een rij met een begindatum en zonder prijs).",
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
        "explanation_cap_none": (
            "Er wordt geen saldo kwijtgescholden met toepassing van de limiet van {years} jaar van de "
            "gecumuleerde rendementsperiodes (Art. 179, §5)."
        ),
        "explanation_cap_some": (
            "Met toepassing van de limiet van {years} jaar van de gecumuleerde rendementsperiodes (Art. 179, §5) "
            "wordt {amount} € kwijtgescholden op {n_capped} periode(n)."
        ),
        "explanation_cap_custom": (
            "Buiten de wet: de gecumuleerde totale rendementsperiode is beperkt tot {years} jaar in plaats van de "
            "{law_years} jaar voorzien door Art. 179, §5."
        ),
        "explanation_mode_bunch": (
            "Volgens de keuze wordt de limiet van {years} jaar geteld per groep van gecumuleerde "
            "rendementsperiodes, zonder onderbreking na elkaar gepresteerd: op {date} zijn {bunch} maand(en) "
            "gepresteerd in de lopende groep{reached}."
        ),
        "explanation_mode_period": (
            "Volgens de keuze wordt de limiet van {years} jaar geteld per rendementsperiode, vanaf haar begin "
            "(schorsingen inbegrepen, non-activiteit niet): op {date} hebben {n_reached} periode(s) ze "
            "bereikt{next}."
        ),
        "explanation_mode_reached": " - de {years} jaar werden bereikt op {when}",
        "explanation_mode_will_reach": " - de {years} jaar worden bereikt op {when}",
        "explanation_mode_next": " - de volgende, {code}, bereikt ze op {when}",
        "explanation_mode_compare": (
            "Volgens de andere lezing ({other}) zou op {date} {total} € verschuldigd zijn, in plaats van "
            "{current} €."
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
        "explanation_inactivity": (
            "{months} maand(en) non-activiteit ({labels}) schorsen de lopende rendementsperiode (§6) - een "
            "maand die, zelfs gedeeltelijk, geraakt wordt, wordt niet gepresteerd."
        ),
        "inactivity_default": "Non-activiteit",
        "departure_label": "Beoogde vertrekdatum:",
        "full_schedule_switch": "Volledige planning, zonder de limiet van {years} jaar (Art. 179, §5)",
        "unbundled_switch": "Vergelijken met de niet-gebundelde opleidingen",
        "theme_toggle": "Nachtmodus",
        "tour_toggle": "Rondleiding",
        "tour": {
            "next": "Volgende", "prev": "Vorige", "done": "Klaar", "progress": "{{current}} van {{total}}",
            "hint": "Klik hier voor een rondleiding",
            "steps": {
                "rules": ["De regels",
                          "Dit zijn de criteria van Art. 179 die de simulator toepast: wanneer een opleiding een "
                          "rendementsperiode activeert, hoe lang die duurt, en wat verschuldigd is bij vertrek voor "
                          "het einde ervan."],
                "preset": ["Een preset laden",
                           "Kies een reeks opleidingen uit de lijst: de meegeleverde voorbeelden, en de CSV-bestanden "
                           "die u hebt geïmporteerd."],
                "import": ["CSV importeren",
                           "Laad uw eigen lijst van opleidingen uit een CSV-bestand (Course, Price, End Date, en "
                           "optioneel Bundle en Start Date). Het wordt in uw privémap bewaard voor uw volgende "
                           "sessies."],
                "export": ["Exporteren naar CSV",
                           "Download de tabel zoals ze nu is, in hetzelfde CSV-formaat, om ze elders te bewerken of "
                           "later opnieuw te importeren."],
                "pdf": ["Exporteren naar PDF",
                        "Download het terugbetalingsplan voor de gekozen vertrekdatum: kerncijfers, drempeltest, "
                        "verschuldigd bedrag per opleiding, beide grafieken en de uitleg."],
                "add_row": ["Rij toevoegen",
                            "Voeg een opleiding toe onderaan de tabel en vul dan haar code, prijs en einddatum in (een"
                            " rij met een begindatum en zonder prijs is een periode van non-activiteit). Elke rij kan "
                            "met × verwijderd worden; de tabel blijft gesorteerd op einddatum."],
                "slider_start": ["Beoogde vertrekdatum",
                                 "Verschuif de schuifregelaar om te kiezen wanneer u de Krijgsmacht zou verlaten. Bij "
                                 "het begin van de eerste rendementsperiode ({date}) zijn enkel de reeds gevolgde "
                                 "opleidingen verschuldigd, nog volledig: {total}."],
                "slider_middle": ["Halverwege",
                                  "Later ({date}) is een deel van het rendement gepresteerd, en is het verschuldigde "
                                  "bedrag gedaald: {total}."],
                "slider_end": ["Volledig afgehandeld",
                               "Aan het einde van de schuifregelaar ({date}) is elke rendementsperiode gepresteerd of "
                               "kwijtgescholden: {total}."],
                "cap_bunch": ["De limiet van {years} jaar, per groep",
                              "Na {years} jaar gecumuleerde rendementsperiodes wordt de rest kwijtgescholden (Art. "
                              "179, §5). Geteld per groep van periodes die elkaar zonder onderbreking opvolgen, is het"
                              " totaal op {date} {total}."],
                "cap_period": ["De limiet van {years} jaar, per periode",
                               "Geteld per rendementsperiode wordt elke periode afzonderlijk beperkt: het totaal op "
                               "{date} wordt {total}."],
                "bar": ["Bedrag per opleiding",
                        "Het degressieve bedrag dat per opleiding nog verschuldigd is op de vertrekdatum: rood als het"
                        " nog verschuldigd is, lichtgrijs als het kwijtgescholden is, groen zodra het volledig "
                        "gepresteerd is."],
                "figures": ["Kerncijfers",
                            "De volledige rendementsperiode, het terug te betalen totaal op de vertrekdatum, en het "
                            "rendement dat deze maand gepresteerd wordt, door de opleiding die op dat moment "
                            "gepresteerd wordt."],
                "timeline": ["Rendementsperiodes",
                             "De rendementsperiode van elke opleiding, maand per maand: gepresteerd (groen), geschorst"
                             " achter een recentere opleiding (grijs), en nog te presteren na de vertrekdatum (rood)."],
                "full_schedule": ["Volledige planning",
                                  "Deze schakelaar toont de periodes zoals ze zouden zijn geweest zonder de limiet van"
                                  " {years} jaar: de kwijtgescholden maanden verschijnen in lichtgrijs, met het "
                                  "kwijtgescholden bedrag."],
                "unbundled": ["Niet-gebundelde opleidingen",
                              "Deze schakelaar vergelijkt gebundelde opleidingen met dezelfde opleidingen "
                              "afzonderlijk: de donkere lijnen tonen de rendementsperiodes die ze zouden hebben gehad,"
                              " doorlopend wanneer gepresteerd, gestippeld wanneer geschorst."],
                "unbundled_none": ["Niet-gebundelde opleidingen",
                                   "Deze schakelaar vergelijkt gebundelde opleidingen met dezelfde opleidingen "
                                   "afzonderlijk. Hij is beschikbaar zodra de tabel een bundel bevat (de optionele "
                                   "kolom Bundle)."],
                "explanation": ["Uitleg",
                                "Tot slot, hoe de regels op deze simulatie van toepassing zijn, met haar eigen cijfers"
                                " op de vertrekdatum. U kunt deze rondleiding altijd opnieuw starten met de knop ? "
                                "bovenaan de pagina."],
            },
        },
        "unbundled_legend": "Niet-gebundelde opleidingen (totaal: {amount} €)",
        "unbundled_none": "activeert de verplichting niet op zich",
        "unbundled_owed": "{amount} € terug te betalen op {date}",
        "cap_mode_label": "Limiet van {years} jaar (Art. 179, §5):",
        "cap_mode_options": {"bunch": "per groep van gecumuleerde periodes", "period": "per rendementsperiode"},
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
        "expired": "Kwijtgescholden",
        "lapsed": "Geschorst, kwijtgescholden",
        "inactive": "Non-activiteit",
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
        "err_bundle_name": "Bundel(s) met de naam van een opleiding buiten de bundel, genegeerd: {names}.",
        "err_inactivity_fields": "Rij {i} ({code}): een periode van non-activiteit heeft geen prijs noch bundel.",
        "err_inactivity_dates": "Rij {i} ({code}): een periode van non-activiteit kan niet eindigen voor ze begint.",
        "report_title": "Terugbetalingsplan van opleidingen",
        "report_subtitle": "Beoogd vertrek op {date} - rapport gegenereerd op {today}",
        "report_source": "Reeks opleidingen: {name}",
        "report_summary": "Overzicht",
        "report_rules": (
            "Toegepaste regels (Art. 179 van de wet van 28/02/2007, "
            "zoals vervangen door de wet van 31/07/2013)"
        ),
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
        "app_title": "Training Reimbursement Simulator",
        "app_subtitle": "Art. 179 of the law of 28/02/2007, as replaced by the law of 31/07/2013",
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
        "col_bundle": "Bundle (optional)",
        "col_start_date": "Non-activity start (dd/mm/yyyy)",
        "law_criteria": [
            "A training followed at the expense of Defence triggers a rendement period whenever the cumulative "
            "cost of trainings within a rolling 24-month window exceeds an indexed threshold (€5,000 base, "
            "linked to the pivot index 138.01).",
            "The military member then owes 24 months of \"rendement\" (service) after that training; leaving "
            "the Armed Forces before completing it means reimbursing a degressively reduced amount "
            "(price × months still owed / 24).",
            "When several trainings' rendement periods overlap, only the most recent one counts as service "
            "each month - older ones stay suspended until it is fully served.",
            "Per §5, the rendement periods of several trainings are cumulated, and the total rendement period "
            "cannot exceed 15 years: beyond, the remaining balance is forgiven (counted per bunch of cumulated "
            "periods or per rendement period, as selected).",
            "Per §6, the rendement period in progress is suspended while the military member is in "
            "non-activity (a row with a start date and no price).",
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
        "explanation_cap_none": (
            "No balance is forgiven under the {years}-year limit of the cumulated rendement periods (Art. 179, "
            "§5)."
        ),
        "explanation_cap_some": (
            "Under the {years}-year limit of the cumulated rendement periods (Art. 179, §5), {amount} € is "
            "forgiven on {n_capped} period(s)."
        ),
        "explanation_cap_custom": (
            "Beyond the law: the cumulated total rendement period is limited to {years} years instead of the "
            "{law_years} years provided by Art. 179, §5."
        ),
        "explanation_mode_bunch": (
            "As selected, the {years}-year limit is counted per bunch of cumulated rendement periods, served one "
            "after the other without interruption: {bunch} month(s) are served in the current bunch as of "
            "{date}{reached}."
        ),
        "explanation_mode_period": (
            "As selected, the {years}-year limit is counted per rendement period, from its start (suspensions "
            "included, non-activity excluded): {n_reached} period(s) reached it as of {date}{next}."
        ),
        "explanation_mode_reached": " - the {years} years were reached on {when}",
        "explanation_mode_will_reach": " - the {years} years will be reached on {when}",
        "explanation_mode_next": " - the next one, {code}, will reach it on {when}",
        "explanation_mode_compare": (
            "With the other reading ({other}), {total} € would be owed as of {date}, instead of {current} €."
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
        "explanation_inactivity": (
            "{months} month(s) of non-activity ({labels}) suspend the rendement period in progress (§6) - a "
            "month touched, even partly, is not served."
        ),
        "inactivity_default": "Non-activity",
        "departure_label": "Planned departure date:",
        "full_schedule_switch": "Full schedule, without the {years}-year limit (Art. 179, §5)",
        "unbundled_switch": "Compare with the courses not bundled",
        "theme_toggle": "Night mode",
        "tour_toggle": "Guided tour",
        "tour": {
            "next": "Next", "prev": "Previous", "done": "Done", "progress": "{{current}} of {{total}}",
            "hint": "Click here for a guided tour",
            "steps": {
                "rules": ["The rules",
                          "These are the criteria of Art. 179 that the simulator applies: when a course triggers a "
                          "rendement period, how long it lasts, and what is owed when leaving before its end."],
                "preset": ["Load a preset",
                           "Pick a set of courses from the list: the examples provided, and the CSV files you "
                           "imported."],
                "import": ["Import a CSV",
                           "Load your own course list from a CSV file (Course, Price, End Date, and optionally Bundle "
                           "and Start Date). It is kept in your private folder for your next sessions."],
                "export": ["Export to CSV",
                           "Download the table as it is, in the same CSV format, to edit it elsewhere or import it "
                           "again later."],
                "pdf": ["Export to PDF",
                        "Download the reimbursement plan for the selected departure date: key figures, threshold test,"
                        " amount owed per course, both charts and the explanation."],
                "add_row": ["Add a row",
                            "Add a course at the bottom of the table, then fill in its code, price and end date (a row"
                            " with a start date and no price is a period of non-activity). Any row can be deleted with"
                            " ×; the table stays sorted by end date."],
                "slider_start": ["Planned departure date",
                                 "Move the slider to choose when you would leave the Armed Forces. At the start of the"
                                 " first rendement period ({date}), only the courses already followed are owed, still "
                                 "in full: {total}."],
                "slider_middle": ["Halfway",
                                  "Later on ({date}), part of the rendement has been served, and the amount owed has "
                                  "decreased: {total}."],
                "slider_end": ["Fully resolved",
                               "At the end of the slider ({date}), every rendement period is served or forgiven: "
                               "{total}."],
                "cap_bunch": ["The {years}-year limit, per bunch",
                              "Beyond {years} years of cumulated rendement periods, the rest is forgiven (Art. 179, "
                              "§5). Counted per bunch of periods following each other without interruption, the total "
                              "on {date} is {total}."],
                "cap_period": ["The {years}-year limit, per period",
                               "Counted per rendement period instead, each period is limited on its own: the total on "
                               "{date} becomes {total}."],
                "bar": ["Amount per course",
                        "The degressive amount still owed per course at the departure date: red if still owed, light "
                        "grey if forgiven, green once fully served."],
                "figures": ["Key figures",
                            "The whole rendement period, the total to reimburse at the departure date, and the "
                            "rendement served this month, by the course being served."],
                "timeline": ["Rendement periods",
                             "Each course's rendement period, month by month: served (green), suspended behind a more "
                             "recent course (grey), and still to serve after the departure date (red)."],
                "full_schedule": ["Full schedule",
                                  "This switch shows the periods as they would have been without the {years}-year "
                                  "limit: the months forgiven appear in light grey, with the amount forgiven."],
                "unbundled": ["Courses not bundled",
                              "This switch compares the bundled courses with the same courses taken separately: the "
                              "dark lines show the rendement periods they would have had, solid when served, dotted "
                              "when suspended."],
                "unbundled_none": ["Courses not bundled",
                                   "This switch compares the bundled courses with the same courses taken separately. "
                                   "It is available once the table has a bundle (the optional Bundle column)."],
                "explanation": ["Explanation",
                                "Finally, how the rules apply to this simulation, with its own figures at the "
                                "departure date. You can replay this tour anytime with the ? button at the top of the "
                                "page."],
            },
        },
        "unbundled_legend": "Courses not bundled (total: {amount} €)",
        "unbundled_none": "does not trigger the obligation on its own",
        "unbundled_owed": "{amount} € to reimburse on {date}",
        "cap_mode_label": "{years}-year limit (Art. 179, §5):",
        "cap_mode_options": {"bunch": "per bunch of cumulated periods", "period": "per rendement period"},
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
        "expired": "Forgiven",
        "lapsed": "Suspended, forgiven",
        "inactive": "Non-activity",
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
        "err_bundle_name": "Bundle(s) named like a course outside of them, ignored: {names}.",
        "err_inactivity_fields": "Row {i} ({code}): a period of non-activity has no price nor bundle.",
        "err_inactivity_dates": "Row {i} ({code}): a period of non-activity cannot end before it starts.",
        "report_title": "Training reimbursement plan",
        "report_subtitle": "Planned departure on {date} - report generated on {today}",
        "report_source": "Course set: {name}",
        "report_summary": "Summary",
        "report_rules": "Rules applied (Art. 179 of the law of 28/02/2007, as replaced by the law of 31/07/2013)",
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

