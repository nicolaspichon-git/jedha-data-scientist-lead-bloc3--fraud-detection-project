-- The recorded state of each control. A control absent from the table is 'ok'.
-- Block: B3.
-- Lot: B3-N9.
-- Competency: B3-C4.
-- Covers: B3-EC14.
SELECT control, state, since, detail
  FROM fd_ops_state;
