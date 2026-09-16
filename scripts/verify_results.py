"""Recompute committed result counts without loading a model."""
import hashlib
from common import ROOT, read_json, rows, score

def main():
    final = ROOT / 'results/final'
    cases = rows(ROOT / 'data/final_test.jsonl')
    claimed = read_json(final / 'metrics.json')
    for tag in ('base', 'adapted'):
        actual = score(cases, read_json(final / f'{tag}-predictions.json'))
        assert actual == claimed[tag], (tag, actual, claimed[tag])
        print(tag, actual)
    config = read_json(final / 'evaluation-config.json')
    for path, key in [(ROOT / 'data/final_test.jsonl', 'dataset_sha256'), (ROOT / 'prompts/system.txt', 'prompt_sha256')]:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == config[key], key
    val = rows(ROOT / 'data/val.jsonl')
    preds = read_json(ROOT / 'results/continuation/validation-predictions.json')
    assert score(val, preds) == read_json(ROOT / 'results/continuation/validation-metrics.json')
    replay = read_json(ROOT / 'results/reload/validation-replay.json')
    assert {p['id']:p['raw'] for p in preds} == {p['id']:p['raw'] for p in replay}
    claimed_replay = read_json(ROOT / 'results/reload/validation-replay-metrics.json')
    assert {**score(val, replay), 'matches_saved_prediction': len(val)} == claimed_replay
    print('Final counts, dataset/prompt hashes, validation counts and 16/16 replay verified.')

if __name__ == '__main__':
    main()
