"""Task contract and scoring. Pure Python; no GPU dependencies."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {'adults', 'budget_eur', 'dairy'}

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def rows(path):
    return [json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]

def schema_ok(o):
    if not isinstance(o, dict) or set(o) != {'updates', 'clarify'}:
        return False
    u, c = o['updates'], o['clarify']
    if not isinstance(u, dict) or not set(u) <= FIELDS:
        return False
    if not isinstance(c, list) or not all(isinstance(x, str) for x in c):
        return False
    if not set(c) <= FIELDS or len(c) != len(set(c)) or set(u) & set(c):
        return False
    if 'adults' in u and (type(u['adults']) is not int or not 1 <= u['adults'] <= 20):
        return False
    if 'budget_eur' in u and (type(u['budget_eur']) not in (int, float) or not 1 <= u['budget_eur'] <= 10000):
        return False
    if 'dairy' in u and u['dairy'] not in ('dairy_free', 'no_restriction'):
        return False
    return True

def assess(raw, target):
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        return False, False, False
    valid = schema_ok(parsed)
    exact = valid and parsed['updates'] == target['updates'] and set(parsed['clarify']) == set(target['clarify'])
    return True, valid, exact

def score(cases, predictions):
    ids = [r['id'] for r in cases]
    pids = [p['id'] for p in predictions]
    assert len(set(ids)) == len(ids) and len(set(pids)) == len(pids), 'Duplicate IDs'
    assert set(ids) == set(pids), 'Missing or extra predictions'
    by_id = {p['id']: p['raw'] for p in predictions}
    totals = dict(n=len(cases), json_valid=0, schema_valid=0, exact_patch=0)
    for r in cases:
        assert schema_ok(r['target']), r['id']
        for key, passed in zip(('json_valid', 'schema_valid', 'exact_patch'), assess(by_id[r['id']], r['target'])):
            totals[key] += int(passed)
    return totals

def chat_prompt(tokenizer, system, row):
    return tokenizer.apply_chat_template([
        {'role': 'system', 'content': system},
        {'role': 'user', 'content': json.dumps(row['input'], ensure_ascii=False)},
    ], tokenize=False, add_generation_prompt=True)
