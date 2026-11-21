-- Journal one message of the operations channel, AFTER it was sent.
-- Block: B3.
-- Lot: B3-R9 (B3-S6).
-- Competency: B3-C4.
-- Covers: B3-EC14, B3-EC17.
--
-- Run in the transaction that records fd_ops_state (fraud/health.py,
-- notify_ops): the state and its journal commit together or not at all.
-- The casts are not decoration: psycopg sends untyped parameters, and an
-- untyped one is text -- which a jsonb or integer column refuses.
INSERT INTO fd_ops_notifications
       (control, state, detail, channel, dag_id, run_id, window_minutes, facts)
VALUES (%(control)s, %(state)s, %(detail)s, %(channel)s, %(dag_id)s,
        %(run_id)s, %(window_minutes)s::integer, %(facts)s::jsonb);
