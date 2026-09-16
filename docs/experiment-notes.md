# Recorded experiment history

1. Refreshed loss, gradients, backpropagation and LoRA fundamentals.
2. Defined a restricted preference-update contract; prepared 80/16/24 synthetic splits.
3. Ran the prompted base and revised the prompt on validation. Revised validation exact match was 1/16.
4. Resolved an optional TorchAO dependency conflict and a Transformers warmup argument change.
5. Trained an initial adapter for 20 updates. The original test result was 0/24 exact; validation generation also failed the schema despite decreasing loss.
6. Checked response labels and prompt/data consistency. A four-case diagnostic achieved 4/4 on memorized cases; its temporary parameter changes were restored. This is not a generalization result.
7. Continued full-data training for 80 updates. The trainer reported minimum validation loss at continuation step 70. Current-model validation yielded 10/16 exact.
8. Reload failed: all 96 LoRA tensors were missing under the expected names. Exported tensors exactly matched the saved tensors, but both had a duplicated `base_model.model.` prefix. The origin of the extra wrapping is not established.
9. Created a separate repaired copy, removed exactly one duplicated wrapper prefix, and supplied the base model/revision metadata. All 96 tensors matched after fresh loading, and all 16 saved validation predictions replayed exactly.
10. Froze the repaired artifact and evaluated 24 newly authored synthetic cases. Base: 0/24 exact. Adapter: 12/24 exact.

## What was checked during packaging

Recomputed final/validation scores from raw predictions; checked final data and prompt hashes; compared original-export and repaired safetensors payloads under the demonstrated key mapping; checked notebook/script syntax and command-line help; scanned included text for common credential patterns; checked ZIP integrity and per-file browser-upload size.

No GPU training or inference was rerun by the repository packager. Intermediate checkpoints are not supplied. The recorded best-checkpoint path is retained as a claim from the trainer, not independent proof that restoring that earlier checkpoint succeeded under the then-wrapped model structure.

## Cleaned reproduction differences

A fresh model is wrapped once. The cleaned trainer starts from the pinned base revision and uses the final saved prompt; it does not replicate interactive prompt edits, accidental nesting, or the memory-reset diagnostic. It recreates the intended two-stage procedure with a new optimizer for continuation, not an uninterrupted ten-epoch run. The default training precision is FP32; the original log records BF16. These differences mean exact score/weight replication should not be promised.

## Next experiments, after this frozen result

Inspect clarification and no-op coverage; resolve ambiguous annotation rules; compare a few-shot base and a larger model; select checkpoints by semantic validation metrics; evaluate multiple seeds with independently collected inputs. These are future work, not completed features.
