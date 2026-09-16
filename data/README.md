# Dataset provenance and task rules

| File | Rows | Role |
|---|---:|---|
| train.jsonl | 80 | Supervised training |
| val.jsonl | 16 | Development, prompt revisions and checkpoint selection |
| test.jsonl | 24 | Original test; examined before later development, so no longer untouched |
| final_test.jsonl | 24 | New synthetic evaluation after freezing the repaired model |

Each row has id, family, input (current_state + instruction), and target (updates + clarify). IDs/family strings are metadata and are never sent to the model. Clarification list order and JSON object key order do not affect exact-match scoring; raw generated JSON is not repaired.

Examples were AI-assisted synthetic data. The supplied train/validation files were used in the notebook; this repository does not silently relabel them. Some phrasing has interpretation ambiguity (for example explicit same-value settings versus instructions to preserve a value). The generation contract was documented, but an independent semantic annotation audit was not supplied.

The final set retains eight categories with three examples each: single updates, multiple updates, correction, negation, ambiguity, no change, irrelevant content, preservation. Its author had seen development errors. It was checked for exact instruction duplicates against the 120 earlier rows; family renaming does not prove semantic independence. The schema's relative-change rule is deliberately restrictive: lower budget BY an amount requires clarification; lower it TO an explicit euro value is an update.

Do not insert any of the published evaluation answers into new training and retain an untouched-test claim. The small final set should be reported with counts and denominators.
