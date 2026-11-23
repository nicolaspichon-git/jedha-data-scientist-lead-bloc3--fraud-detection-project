-- The mornings with no report. MUST RETURN ZERO ROWS.
-- Block: B3.
-- Lot: B3-P3.
-- Competency: B3-C4.
-- Covers: B3-EC14.
--
-- A wrong report is seen; an absent one is not. This is B3-EC14 -- detect the
-- absence -- applied to the one deliverable of this project that a human reads.
--
-- IT STARTS AT THE FIRST RECORDED REPORT AND NOT THIRTY DAYS AGO, and that is
-- the difference between a control and an alarm. A pipeline three days old
-- would otherwise list twenty-seven missing mornings that nobody ever expected,
-- and a check that fails on reality teaches its reader to ignore it -- the
-- lesson of criterion 13 of B3-S3, paid for once already.
--
-- So the span runs from the first report (or thirty days ago, whichever is
-- later, to keep the answer readable) to YESTERDAY. Two kinds of gap are
-- therefore caught, and the second matters more:
--
--   a hole BETWEEN two reports   one morning failed and was never replayed
--   a hole AFTER the last one    the DAG stopped, and has been stopped since
--
-- AN EMPTY TABLE RETURNS NOTHING, by the HAVING below: before the first report
-- ever produced, no morning is missing. "No report has ever been produced" is a
-- different finding, and it belongs to the acceptance criteria of B3-P5 rather than
-- here -- a control that fires on a system not yet started is noise.

WITH span AS (
    SELECT greatest(min(report_date), current_date - 30) AS first_day,
           -- The last day whose report is DUE, not yesterday. The report of
           -- day D is written on D+1 at the delivery hour of the mode in force
           -- -- 06:00 nominal, 14:00 demo (governance.yml, report.mode) --
           -- within its 30-minute dagrun_timeout. Read as "yesterday", the
           -- check failed every night on a report not yet due.
           --
           -- THE HOUR IS READ FROM THE REPORTS THEMSELVES, not written here: a
           -- report's knowledge_date is the end of its Airflow interval, i.e.
           -- the delivery instant, so knowledge_date - (report_date + 1 day)
           -- is the delivery hour. The largest of the last three, so that a
           -- report produced by hand (knowledge at midnight) does not advance
           -- the due hour. Just after a switch nominal -> demo, the day before
           -- the first 14:00 report reads as missing from 06:30 to 14:30.
           ((now() AT TIME ZONE 'Europe/Paris')
             - (SELECT max((r.knowledge_date AT TIME ZONE 'Europe/Paris')
                           - (r.report_date + 1)::timestamp)
                  FROM (SELECT report_date, knowledge_date FROM fd_reports
                         ORDER BY report_date DESC LIMIT 3) AS r)
             - interval '30 minutes')::date - 1          AS last_day
      FROM fd_reports
    HAVING count(*) > 0
)
SELECT day::date                                          AS journee_sans_rapport,
       current_date - day::date                           AS il_y_a_jours
  FROM span,
       generate_series(span.first_day, span.last_day, interval '1 day') AS day
 WHERE NOT EXISTS (SELECT 1 FROM fd_reports r
                    WHERE r.report_date = day::date)
 ORDER BY day;
