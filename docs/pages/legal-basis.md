# Legal basis

This page lists the texts that the simulator implements, their history, and the questions they leave open. Its
quotations are unofficial English translations of the French texts: only the French, Dutch and German versions are
official.

> **Not legal advice** - The texts below were read as published on [Justel](https://www.ejustice.just.fgov.be/) (the
> consolidated legislation database of the Belgian Official Journal). Check them, and the practice of Defence, before
> relying on the simulator for anything official.

## Texts in force

| Text | What it provides | In the simulator |
|---|---|---|
| [Law of 28/02/2007](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2007022835) on the status of military personnel, Art. 178/3 to 184/1, as replaced and inserted by the [law of 31/07/2013](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2013073104) | Rendement periods and reimbursement of training costs | Everything below |
| Art. 179, §1, 5° | A rendement period starts after "any other training, if it was followed at the expense of Defence and if the cumulated cost over a period of two years exceeds the minimum fixed by the King, which may not be lower than 5,000 euros" | [Threshold](law.md#threshold) |
| Art. 179, §3 | "For the trainings referred to in §1, 5°, the rendement period is two years." | [Rendement period](law.md#rendement-period) |
| Art. 179, §4 | Counted in whole months, starting on the first day of the month following the end of the training | [Rendement period](law.md#rendement-period) |
| Art. 179, §5 | "A training followed during a rendement period which implies an additional rendement period suspends the rendement period in progress. The rendement periods corresponding to various trainings are cumulated. The total rendement period may not exceed fifteen years." | [Priority and suspension](law.md#priority-and-suspension), [Maximum total rendement period](law.md#maximum-total-rendement-period-5) |
| Art. 179, §6 | "The rendement period in progress is suspended for the military member who is in the position 'in non-activity'." | [Non-activity](law.md#non-activity-6) |
| Art. 180, al. 3 (career military members) and Art. 181, al. 4 (auxiliary officers) | Leaving before the end of the "accumulated rendement period", in the cases each of them lists (see [below](#who-is-concerned)), means reimbursing a fraction of the cost: the months still to serve out of 24, over 24 | [Rendement period](law.md#rendement-period) |
| Art. 184/1 | "The amounts set in this law are adapted in accordance with the law of 1 March 1977 […]. The amounts correspond to the pivot index 138.01 (base 1981=100)." | [Indexation table](input-files.md#indexation-table) |
| Art. 189 | Defines the position of non-activity (see [below](#non-activity)) | [Non-activity](law.md#non-activity-6) |
| [Law of 01/03/1977](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=1977030102) on the indexation of public-sector amounts, Art. 2, 4 and 6 | Pivot indexes (each one the previous one × 1.02), coefficient `1.02ⁿ` rounded to 4 decimals, applied from the third month after the smoothed health index reaches the pivot index (Art. 6, 3°, as replaced by the [programme law of 18/07/2025](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2025071806) from 01/07/2025 on; the delay was shorter before, e.g. 01/03/2025 for a pivot index reached in 01/2025) | [Updating the table](input-files.md#updating-the-table) |

## History

| In force on | Text | Change |
|---|---|---|
| 16/04/2000 | **[Law of 16/03/2000](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2000031635)** "on the resignation of certain military members […], the setting of the rendement period and the recovery by the State of part of the costs incurred by the State for the training […]" | The base law: rendement periods for the basic and higher-education trainings, suspension by a new training, "The rendement periods corresponding to various trainings are cumulated, the overall period may not exceed fifteen years", suspension during non-activity |
| - | Constitutional Court, [ruling 134/2000](https://fr.const-court.be/public/f/2000/2000-134f.pdf) and ruling 28/2002 | Request for suspension of the [law of 16/03/2000](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2000031635) rejected, then partial annulment (extra muros trainings, former §4) |
| **04/06/2009** | [Law of 26/04/2009](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2009042631) (Justel ref. 2009-04-26/31), Art. 19 and 23 | **Inserts §1, 5°** (other trainings above a minimum of at least €5,000 over two years, with a rendement period of two years) and 6° (aircraft conversions) in the [law of 16/03/2000](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2000031635), and links its amounts to the pivot index 138.01 |
| 22/02/2010 | [Law of 10/01/2010](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2010011015) (Justel ref. 2010-01-10/15) | Air traffic controllers |
| **31/12/2013** | **[Law of 31/07/2013](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2013073104)** (Justel ref. 2013-07-31/04), Art. 271 to 280, put into force by the royal decrees of 26/12/2013 | Replaces Art. 179 to 184 of the [law of 28/02/2007](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2007022835) and inserts Art. 178/3, 183/1 and 184/1 (indexation as of the [law of 01/03/1977](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=1977030102)), with the same rules; Art. 230 of the [law of 28/02/2007](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2007022835) **repeals the [law of 16/03/2000](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2000031635)** on the same day |
| 02/01/2017 | [Law of 21/11/2016](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2016112120) (Justel ref. 2016-11-21/20) | Art. 182 and 183 (other categories of personnel) |
| 25/05/2018 | [Law of 30/04/2018](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2018043007) (Justel ref. 2018-04-30/07) | Art. 180 (air traffic controllers, table F2) |
| 11/03/2019 | [Law of 15/02/2019](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2019021501) (Justel ref. 2019-02-15/01) | Art. 179, §3: rendement period after an aircraft conversion raised from four to six years |
| 08/01/2026 | [Law of 08/12/2025](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2025120807) (Justel ref. 2025-12-08/07) | Art. 189: cases of non-activity |

The trainings of §1, 5° are thus governed by the [law of 16/03/2000](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2000031635) from 04/06/2009 to 30/12/2013, and by the law of
28/02/2007 from 31/12/2013 on, with the same wording: the simulator applies the same rules to both, to the trainings
ending from 04/06/2009 on.

## Explanatory memorandum of the law of 31/07/2013

The bill ([DOC 53 2879/001](https://www.lachambre.be/FLWB/PDF/53/2879/53K2879001.pdf), Chamber of Representatives, 2013; its articles are numbered one less
than in the law, its Art. 271 being Art. 272 of the law) comments the new Art. 179 as follows (page 82):

> The principle is laid down that the rendement period is equal to one and a half times the duration of the training,
> without however, per training, being shorter than three years or longer than twelve years. The duration of the
> training taken into account is set in table A of annex B. The rendement periods corresponding to various trainings
> are cumulated, and the overall rendement period may not exceed fifteen years. It must therefore be clear that any
> specialization followed after the basic training, such as the specialization training after the 7-year training of
> a physician, must be considered as a separate training and must give rise to a period of active service. The
> limitation to fifteen years aims at reasonably balancing the whole rendement period due to various trainings and the
> total duration of the career. This is for instance important for medical, veterinary, pharmacist and dentist
> officers who follow specializations leading to particular professional titles, because these trainings could
> sometimes, without the aforementioned restriction, lead to the obligation to perform more than fifteen years of
> active service.

It neither comments §1, 5° (taken over from the [law of 16/03/2000](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2000031635)) nor gives the minimum to be fixed by the King. The
opinion of the Council of State it includes makes no remark on Art. 179 to 183.

## Maximum total rendement period

The memorandum settles that the 15 years apply to the **cumulation of several trainings**, a single training being
limited by §2 (12 years for the trainings of §1, 1° to 3°, 2 years for those of §1, 5°). It does not say how the
cumulated period is measured, hence the two modes of the simulator (`--cap-mode`):

- **`bunch`** (default) - the months **served** per bunch of rendement periods served one after the other without
  interruption, which is what Art. 180 calls the "accumulated rendement period", whose end frees the military member
  from reimbursing. Once a bunch reaches 15 years, all its periods are forgiven at once, including those just started;
  a later training starts a new bunch.
- **`period`** - each rendement period on its own, forgiven 15 years after it started, the months it is suspended
  behind more recent periods included. This reads the 15 years as a limit on how long a single training can keep the
  military member bound, its period being stretched by the suspensions of §5.

A bunch reaches 15 years no later than its oldest period, so `bunch` never gives a higher amount than `period`: it is
the reading most favorable to the military member. Both give the same results as long as no rendement period is still
owed 15 years after it started.

## Who is concerned

Art. 179, §1, 5° applies to "the career military member or auxiliary officer", and each of the two categories has its
own subparagraph (al.) on the reimbursement, with the same amount but different cases of departure:

| | Art. 180, al. 3 - career military member | Art. 181, al. 4 - auxiliary officer |
|---|---|---|
| Departure | "who obtained their resignation or who was dismissed ex officio" | "who obtained the termination of their engagement or whose engagement is terminated for disciplinary reasons, moral or professional unfitness" |
| Before | "the end of the accumulated rendement period under the conditions referred to in Article 179, §1, 5°" | "the end of the accumulated rendement period for the reasons referred to in Article 179, §1, 5°" |
| Amount | "a fraction of the aforementioned cost": "the difference between the twenty-four months to be served for the rendement period, set in Article 179, §3, and the number of months already served" over "twenty-four months" | the same, the period being "set in Article 179, §3, subparagraph 1" |

The simulator computes this amount, the same for both, for any departure date. Whether it is actually owed depends on
the reason for leaving, which the simulator does not know:

- a **career military member** owes it when resigning or dismissed ex officio, but not, as these are not listed, when
  retiring - whereas Art. 180, al. 4 explicitly adds the pension for the aircraft conversions of §1, 6°;
- an **auxiliary officer** owes it when their engagement is terminated at their request, or for disciplinary reasons,
  moral or professional unfitness, but not when it is terminated for medical unfitness or ends at its term.

Under the [law of 16/03/2000](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2000031635), the same rules were in its Art. 4, al. 3 (career military members, and "complementary-cadre
military members" - *militaires de complément* -, a category the [law of 28/02/2007](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2007022835) no longer lists in §1, 5°) and Art. 5, al. 4 (auxiliary officers; al. 3
until the insertion of the air traffic controllers on 22/02/2010).

## Non-activity

As of Art. 189, the position of non-activity is that of the military member:

1. "who is temporarily withdrawn from their employment" - the [law of 28/02/2007](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2007022835) provides for temporary withdrawals of
   employment by career interruption, for family reasons, for health reasons, for personal convenience and as a
   disciplinary measure;
2. "who has been recognized as being in illegal absence";
3. "who is serving a custodial sentence" (except under limited detention, electronic monitoring or conditional
   release);
4. "who is on ex officio political leave";
5. who was convicted as of Art. 19 of the Criminal Code or Art. 5 of the Military Criminal Code, or deprived of some
   of the rights of Art. 31 of the Criminal Code.

Some periods (suspension by order, pre-trial detention, internment, absence of a military member separated from the
army) are converted afterwards into non-activity, depending on how they end.

## Open questions

- **Minimum fixed by the King** - Art. 179, §1, 5° (and the [law of 16/03/2000](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2000031635) before it) leaves the minimum to a royal
  decree, without it being lower than €5,000. No such decree is listed among the implementing decrees of either law on
  Justel: the simulator uses €5,000, indexed.
- **What a training is** - The law reasons per training, and the memorandum treats each specialization as "a
  separate training". Whether several courses (e.g. a course and its certification) are one training, as with
  [bundles](law.md#bundles), or several, is a matter of Defence practice.
- **How the 15 years are measured** - Per bunch of cumulated periods, or per rendement period (see
  [above](#maximum-total-rendement-period)): the simulator applies the most favorable one, per bunch, by default.
- **Who is concerned** - The simulator neither asks for the category of the military member nor for the reason for
  leaving, on which the obligation to reimburse depends (see [above](#who-is-concerned)).

## Sources

- [Law of 28/02/2007](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2007022835), consolidated
- [Law of 31/07/2013](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2013073104), consolidated
- [Law of 16/03/2000](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2000031635), consolidated (repealed)
- [Law of 01/03/1977](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=1977030102), consolidated
- Royal decree of 26/12/2013 putting the [law of 31/07/2013](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2013073104) into force: [Justel](https://www.ejustice.just.fgov.be/cgi_loi/article.pl?language=fr&sum_date=&numac_search=2013007329&page=&lg_txt=F&caller=article)
- Bill of the [law of 31/07/2013](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2013073104), with its explanatory memorandum and the opinion of the Council of State: [DOC 53 2879/001](https://www.lachambre.be/FLWB/PDF/53/2879/53K2879001.pdf)
- Constitutional Court, ruling 134/2000: [PDF](https://fr.const-court.be/public/f/2000/2000-134f.pdf)
- Indexation coefficients of the public sector since 1990: [BOSA](https://bosa.belgium.be/fr/themes/travailler-dans-la-fonction-publique/remuneration-et-avantages/traitement/indexation-0) ([archived copy of 07/12/2022](http://web.archive.org/web/20221207002526/https://bosa.belgium.be/fr/themes/travailler-dans-la-fonction-publique/remuneration-et-avantages/traitement/indexation-0))
