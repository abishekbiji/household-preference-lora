# Household preference extraction with LoRA

A small, measured fine-tuning experiment by **Abishek Biji**: adapt Qwen2.5-0.5B-Instruct to extract household preference updates as JSON.

On 24 newly authored synthetic evaluation cases, exact-match answers increased from **0/24 for the prompted base model to 12/24 for the adapted model**. The saved adapter reproduced all **16/16 development-validation predictions** after checkpoint repair and reload.

This is an independent learning project. It is not affiliated with Picnic, does not implement a grocery purchasing agent, and is not production-ready.

## Results you can inspect

| Final synthetic evaluation | Prompted base | LoRA adapter |
|---|---:|---:|
| Valid JSON | 22/24 (91.7%) | 24/24 (100%) |
| Valid task schema | 2/24 (8.3%) | 19/24 (79.2%) |
| Exact update + clarification match | 0/24 (0%) | 12/24 (50%) |

The exact-match difference is **50 percentage points**, not a relative improvement percentage. The adapted model still produced five schema-invalid answers and seven additional schema-valid but semantically wrong answers.

Inspect [predictions](results/final/adapted-predictions.json), [metrics](results/final/metrics.json), [all final failures](docs/error-analysis.md), and [experiment history](docs/experiment-notes.md).

### Verify reported counts without a GPU or downloads

From this repository's root, using Python 3.10 or newer:

```bash
python scripts/verify_results.py
```

This recomputes scores from the committed raw outputs, checks input/prompt hashes and checks the 16-case saved/reloaded output comparison. It does not independently rerun inference or authenticate the history of an uploaded experiment.

## Task

Input: `current_state` and one natural-language `instruction`. Output: exactly `updates` and `clarify`.

```json
{"updates":{"budget_eur":65},"clarify":[]}
```

Only three fields are supported: `adults` (integer 1–20), `budget_eur` (number 1–10000), and `dairy` (`dairy_free` or `no_restriction`). Unchanged fields are omitted. Ambiguous or unsupported values require clarification; a field cannot be both updated and clarified. Relative numeric changes deliberately require clarification. This is a restricted extraction contract, not a general shopping assistant or allergy safety system.

The authoritative instruction is [prompts/system.txt](prompts/system.txt). [Data documentation](data/README.md) explains splits and caveats.

## Model and experiment

- Base: [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct).
- Revision: `7ae557604adf67be50417f59c2c2f167def9a775`.
- Ordinary LoRA; frozen non-quantized base; rank 8, alpha 16, dropout 0.05, `q_proj` and `v_proj`.
- 540,672 trainable parameters, approximately 0.1093% of the reported total.
- 80 training examples; 16 development-validation cases; 24 original test cases inspected during development; 24 later evaluation cases.
- Initial run: 2 epochs / 20 optimizer updates. Continuation: 8 additional epochs / 80 updates with a new optimizer and schedule.
- A four-example memorization diagnostic ran in between; its adapter changes were restored before continuation.
- Greedy inference, maximum 160 new tokens; same final prompt for base and adapted predictions.
- Final baseline uses the verified adapter-loaded model with adapters disabled, recovering the unchanged base model.

The trainer reported selecting continuation checkpoint 70. Intermediate checkpoints are absent from the evidence archive, so this package does not claim an independently verified 90-update lineage for the distributed artifact. Its tensor contents and reload outputs were verified instead.

## Reproduce inference on the supplied artifact

The full base weights are not included and must be downloaded. A CUDA GPU is recommended; the script also supports CPU inference, which can be slow.

The recorded environment was Python 3.13, PyTorch `2.11.0+cu128`, Transformers `5.17.0`, PEFT `0.21.0`, Accelerate `1.15.0`. In a fresh virtual environment with a compatible NVIDIA driver:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r requirements.txt
python scripts/evaluate.py --output outputs/final-replay
```

If using an existing Colab runtime, retain its compatible PyTorch installation. An old preinstalled `torchao` caused an import error in the recorded experiment; ordinary LoRA here does not require it. Remove it in that dedicated runtime if necessary, then restart the session. Do not indiscriminately upgrade the pinned packages.

`evaluate.py` verifies all adapter tensors after loading, evaluates with adapters disabled/enabled, and writes new predictions and metrics under `outputs/`. It refuses to overwrite an existing output directory. Hardware/precision/library differences can change outputs.

## Retrain as a new experiment

```bash
python scripts/train.py --precision fp32 --output outputs/new-training
python scripts/evaluate.py --adapter outputs/new-training/continuation/adapter --data data/val.jsonl --output outputs/new-validation
```

The cleaned training script wraps the base once, uses response-only labels, and performs two training stages with separate optimizers. It does not recreate the accidental double wrapping or notebook recovery sequence. Its conservative default is FP32; explicit `fp16` and `bf16` options exist. The recorded run flags say BF16 on a Tesla T4; the archive does not establish whether that used native acceleration, so no BF16 hardware-speed claim is made.

**The cleaned GPU scripts and notebook have not been executed end to end during repository packaging.** Syntax/CLI checks and offline evidence verification were performed. The recorded results come from the supplied experimental notebook and artifacts, not from these newly refactored scripts. Retraining is not guaranteed to reproduce the same weights or scores.

Use validation for development. These published final cases are now exposed: if you tune using them, author another held-out set before reporting a new final result.

## Repository guide

| Path | Contents |
|---|---|
| `notebooks/reproduce.ipynb` | Clean entry point for verification, inference and optional new training |
| `notebooks/experiment-history.ipynb` | Sanitized historical notebook; interactive execution history, not Run All safe |
| `data/` | All four actual datasets |
| `prompts/` | Final and original prompts |
| `adapter/` | Repaired LoRA weights, config and tokenizer |
| `results/` | Recorded initial/continuation/final results and reload evidence |
| `scripts/` | Offline verifier and cleaned GPU workflows |
| `docs/` | Error analysis, experiment notes, provenance and upload instructions |
| `environment/` | Recorded package inventory |

## Limitations

Small synthetic datasets; one seed; close train/validation paraphrases despite different family IDs; no few-shot, larger-model, constrained-decoding or multi-seed comparison. Final cases were authored with knowledge of development failures, after model freezing; they are a post-development synthetic check, not an independently sampled real-world benchmark. Review of labels by the experimenter is encouraged; generation and schema checks alone do not establish label correctness.

Formatting compliance is not semantic accuracy. Half the final cases remain wrong. No production reliability, latency, cost reduction, purchasing safety or statistically robust population-level accuracy is established.

## Attribution and licensing

Base model and tokenizer: Qwen, Apache-2.0 as identified on its model card. See [THIRD_PARTY.md](THIRD_PARTY.md) and the included upstream license. No repository-wide license for the author's original code/data has been selected in this package; public visibility alone is not an open-source license grant.

AI assistance was used for learning guidance, synthetic examples, debugging and repository preparation; the owner executed the notebook and supplied the recorded evidence.
