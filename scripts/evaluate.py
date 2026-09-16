"""Fresh inference using the supplied adapter; does not overwrite recorded results."""
import argparse
import hashlib
import json
from contextlib import nullcontext
from common import ROOT, read_json, rows, score, chat_prompt

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--adapter', type=str, default=str(ROOT / 'adapter'))
    p.add_argument('--data', type=str, default=str(ROOT / 'data/final_test.jsonl'))
    p.add_argument('--output', type=str, default=str(ROOT / 'outputs/evaluation'))
    args = p.parse_args()
    from pathlib import Path
    import torch
    from peft import PeftModel, get_peft_model_state_dict
    from safetensors.torch import load_file
    from transformers import AutoTokenizer, AutoModelForCausalLM
    config = read_json(ROOT / 'config/experiment.json')
    system = (ROOT / 'prompts/system.txt').read_text()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('Choose a new output directory to preserve previous results.')
    adapter = Path(args.adapter)
    tok = AutoTokenizer.from_pretrained(adapter)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    base = AutoModelForCausalLM.from_pretrained(config['base_model'], revision=config['base_revision'], torch_dtype=torch.float32).to(device)
    assert not any('lora_' in name for name, _ in base.named_parameters())
    model = PeftModel.from_pretrained(base, str(adapter)).eval()
    disk = load_file(str(adapter / 'adapter_model.safetensors'))
    loaded = get_peft_model_state_dict(model)
    assert set(disk) == set(loaded), 'Adapter key mismatch'
    assert all(torch.equal(v, loaded[k].detach().cpu()) for k,v in disk.items()), 'Adapter tensor mismatch'
    assert all(not m.merged_adapters for m in model.modules() if hasattr(m, 'merged_adapters'))
    cases = rows(args.data)
    out.mkdir(parents=True)
    results = {}
    for tag in ('base', 'adapted'):
        predictions = []
        with model.disable_adapter() if tag == 'base' else nullcontext():
            for r in cases:
                inputs = tok(chat_prompt(tok, system, r), add_special_tokens=False, return_tensors='pt').to(device)
                with torch.inference_mode():
                    generated = model.generate(**inputs, do_sample=False, max_new_tokens=160, pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
                raw = tok.decode(generated[0, inputs['input_ids'].shape[1]:], skip_special_tokens=True).strip()
                predictions.append({'id': r['id'], 'raw': raw})
        (out / f'{tag}-predictions.json').write_text(json.dumps(predictions, indent=2))
        results[tag] = score(cases, predictions)
    (out / 'metrics.json').write_text(json.dumps(results, indent=2))
    (out / 'run.json').write_text(json.dumps({**config, 'adapter': str(adapter), 'device': device, 'dataset_sha256': hashlib.sha256(Path(args.data).read_bytes()).hexdigest(), 'prompt_sha256': hashlib.sha256(system.encode()).hexdigest(), 'do_sample': False, 'max_new_tokens': 160}, indent=2))
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
