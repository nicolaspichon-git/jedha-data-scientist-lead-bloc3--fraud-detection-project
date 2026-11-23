-- One payment followed from the raw zone to the analyst's notification, for
-- the video (scenario, act 3). Run from psql, never pasted:
--     \i /work/sql/demo/paiement_bout_en_bout.sql
-- Block: B3.
-- Covers: B3-EE06, B3-EI11.
--
-- WHY A FILE. Pasted into an interactive psql, a block of lines that holds
-- meta-commands arrives as ONE line: the first backslash command then swallows
-- the rest as its arguments, quotes stripped. \i reads the file line by line.
--
-- THE EXAMPLE. The notified fraud of YESTERDAY (Paris) that weighs the most,
-- score times amount: it opens section 2 of this morning's report. If
-- yesterday holds none, the most recent notified fraud WHOSE DAY HAS A REPORT
-- -- a fraud of today has none until tomorrow's delivery, and act 3 ends on
-- the report. Only then a fraud without one. The day and its report are printed.
--
-- Reads only. Shows the NAMES of the identifying fields of the raw zone,
-- never their values.

SET TIME ZONE 'Europe/Paris';
\pset null '(vide)'
\unset txn_id

-- THE START OF THE REPORTED DAY, as governance.yml declares it for the mode in
-- force (report.mode): 00:00 nominal, 12:00 demo. psql cannot read the YAML,
-- so it is given here; in demo mode, before \i:   \set day_start 12:00
\if :{?day_start}
\else
\set day_start 00:00
\endif

SELECT txn_id,
       jour,
       :'day_start'                   AS debut_de_journee,
       split_part(txn_id, ':', 1)     AS trans_num,
       CASE WHEN hier THEN 'oui' ELSE 'non : plan de secours' END AS fraude_d_hier,
       CASE WHEN rapporte THEN 'oui' ELSE 'NON : pas encore produit' END AS rapport_existe
  FROM (SELECT f.txn_id,
               -- The REPORTED day of the payment: its local time minus the
               -- start of the day, so that 09:00 belongs to yesterday's
               -- noon-to-noon day in demo mode.
               ((t.txn_ts AT TIME ZONE 'Europe/Paris')
                 - :'day_start'::interval)::date AS jour,
               ((t.txn_ts AT TIME ZONE 'Europe/Paris')
                 - :'day_start'::interval)::date
                 = ((now() AT TIME ZONE 'Europe/Paris')
                    - :'day_start'::interval)::date - 1 AS hier,
               EXISTS (SELECT 1 FROM fd_reports r
                        WHERE r.report_date
                              = ((t.txn_ts AT TIME ZONE 'Europe/Paris')
                                 - :'day_start'::interval)::date) AS rapporte,
               f.score * t.amt AS poids
          FROM fd_frauds f
          JOIN fd_transactions t USING (txn_id)
         WHERE f.notified_at IS NOT NULL) AS c
 ORDER BY hier DESC, rapporte DESC, jour DESC, poids DESC
 LIMIT 1 \gset

\if :{?txn_id}
\echo
\echo 'Exemple      :' :txn_id
\echo 'Journee      :' :jour '  (fraude d''hier :' :fraude_d_hier ')'
\echo 'Journee de   :' :debut_de_journee 'a' :debut_de_journee '; rapport de cette journee existe :' :rapport_existe
\echo 'A chercher dans runtime/channels/frauds/frauds.jsonl :' :trans_num
\echo
\x on

\echo '1. Zone brute : l''identite du porteur existe, et seulement ici'
SELECT r.batch_id, r.line_no, r.ingested_at,
       (SELECT string_agg(k, ', ' ORDER BY k)
          FROM jsonb_object_keys(r.payload->'row') AS k
         WHERE k IN ('first', 'last', 'street', 'city', 'zip', 'dob', 'cc_num'))
         AS champs_identifiants
  FROM fd_raw_events r
  JOIN fd_transactions t ON t.batch_id = r.batch_id
 WHERE t.txn_id = :'txn_id'
   AND r.payload->>'trans_num' = split_part(t.txn_id, ':', 1);

\echo '2. Couche exploitee : un pseudonyme et des features, plus d''identite'
SELECT txn_id, txn_ts, client_key, merchant, category, amt,
       f_tx_count, f_avg_amount, f_home_distance_km
  FROM fd_transactions
 WHERE txn_id = :'txn_id';

\echo '3. Le score, le seuil, la version du modele'
SELECT model_version, score, threshold, flagged, scored_at
  FROM fd_scores
 WHERE txn_id = :'txn_id';

\echo '4. L''alerte et sa notification'
SELECT raised_at, notified_at, channel, attempts
  FROM fd_frauds
 WHERE txn_id = :'txn_id';

\x off
\else
\echo
\echo 'AUCUNE fraude notifiee en base : l''acte 3 n''a pas d''exemple.'
\echo 'Laisser tourner l''ingestion (.\fd-manager.ps1 realtime -Start) et revenir.'
\endif
