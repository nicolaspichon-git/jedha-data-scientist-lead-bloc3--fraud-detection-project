-- The rejected line of the last manual ingestion, for the video (scenario,
-- act 4). Run from psql right after `.\fd-manager.ps1 ingest -Corrupt`:
--     \i /work/sql/demo/erreur_quarantaine.sql
-- Block: B3.
-- Covers: B3-EC23, B3-EC26.
--
-- Shows the REASONS of the rejection, never the content of the line: the
-- payload of fd_quarantine holds the raw record, identity included.

SET TIME ZONE 'Europe/Paris';
\x off

\echo 'La ligne rejetee : ses motifs, jamais son contenu'
SELECT q.batch_id, q.line_no, q.reason_class, q.reason_code, q.rejected_at
  FROM fd_quarantine q
 WHERE q.batch_id = (SELECT batch_id FROM fd_pipeline_runs
                      WHERE dag_id = 'ingest_once'
                      ORDER BY started_at DESC LIMIT 1)
 ORDER BY q.line_no, q.reason_code;

\echo 'Les compteurs du lot : lues = valides + rejetees'
SELECT run_id, state, n_read, n_valid, n_rejected
  FROM fd_pipeline_runs
 WHERE dag_id = 'ingest_once'
 ORDER BY started_at DESC
 LIMIT 1;
