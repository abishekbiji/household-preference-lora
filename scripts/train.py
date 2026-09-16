"""Clean two-stage reproduction attempt, not the source of committed results.

Only train/validation data are opened. Each invocation starts a fresh base and
attaches LoRA exactly once. GPU execution has not been rerun during packaging.
"""
import argparse
import json
import time
from pathlib import Path
from common import ROOT, read_json, rows, schema_ok, chat_prompt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(ROOT / 'outputs/training'))
    parser.add_argument('--precision', choices=['fp32', 'fp16', 'bf16'], default='fp32')
    opts = parser.parse_args()
    out = Path(opts.output)
    if out.exists():
        raise FileExistsError('Use a new output directory; this script starts from scratch.')
    import torch
    from datasets import Dataset
    from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, set_seed
    from peft import LoraConfig, get_peft_model, get_peft_model_state_dict
    from safetensors.torch import load_file
    assert torch.cuda.is_available(), 'Use a CUDA GPU for this training script.'
    cfg = read_json(ROOT / 'config/experiment.json')
    set_seed(42)
    system = (ROOT / 'prompts/system.txt').read_text()
    tok = AutoTokenizer.from_pretrained(ROOT / 'adapter')
    tok.padding_side = 'right'
    model = AutoModelForCausalLM.from_pretrained(cfg['base_model'], revision=cfg['base_revision'], torch_dtype=torch.float32).to('cuda')
    assert not any('lora_' in n for n,_ in model.named_parameters()), 'Base is already adapted'
    model = get_peft_model(model, LoraConfig(task_type='CAUSAL_LM', r=8, lora_alpha=16, lora_dropout=0.05, target_modules=['q_proj','v_proj'], bias='none'))
    assert all('lora_' in n for n,p in model.named_parameters() if p.requires_grad)
    model.print_trainable_parameters()
    def encode(r):
        assert schema_ok(r['target'])
        prompt = tok(chat_prompt(tok, system, r), add_special_tokens=False)['input_ids']
        answer = tok(json.dumps(r['target'], ensure_ascii=False, separators=(',',':')) + tok.eos_token, add_special_tokens=False)['input_ids']
        assert len(prompt)+len(answer) <= 512, r['id']
        return {'input_ids':prompt+answer, 'attention_mask':[1]*(len(prompt)+len(answer)), 'labels':[-100]*len(prompt)+answer}
    train = Dataset.from_list([encode(r) for r in rows(ROOT/'data/train.jsonl')])
    val = Dataset.from_list([encode(r) for r in rows(ROOT/'data/val.jsonl')])
    def collate(batch):
        width = max(len(r['input_ids']) for r in batch)
        return {k:torch.tensor([r[k]+[pad]*(width-len(r[k])) for r in batch]) for k,pad in [('input_ids',tok.pad_token_id),('attention_mask',0),('labels',-100)]}
    out.mkdir(parents=True)
    for stage, epochs, warmup in [('initial',2,0.1),('continuation',8,0)]:
        model.config.use_cache = False
        args = TrainingArguments(output_dir=str(out/stage/'checkpoints'), per_device_train_batch_size=1, per_device_eval_batch_size=1, gradient_accumulation_steps=8, num_train_epochs=epochs, learning_rate=1e-4, lr_scheduler_type='linear', warmup_steps=warmup, logging_steps=1 if stage=='initial' else 10, eval_strategy='epoch', save_strategy='epoch', load_best_model_at_end=True, metric_for_best_model='eval_loss', greater_is_better=False, save_total_limit=2, fp16=opts.precision=='fp16', bf16=opts.precision=='bf16', optim='adamw_torch', report_to='none', seed=42, label_names=['labels'])
        trainer = Trainer(model=model, args=args, train_dataset=train, eval_dataset=val, data_collator=collate)
        started = time.time()
        trainer.train()
        model.config.use_cache = True
        dest = out/stage/'adapter'
        model.save_pretrained(dest)
        tok.save_pretrained(dest)
        disk = load_file(str(dest/'adapter_model.safetensors'))
        exported = get_peft_model_state_dict(model)
        assert set(disk)==set(exported)
        assert all(torch.equal(t,exported[k].detach().cpu()) for k,t in disk.items())
        (out/stage/'training-log.json').write_text(json.dumps(trainer.state.log_history,indent=2))
        arguments=args.to_dict();arguments.pop('hub_token',None)
        (out/stage/'run.json').write_text(json.dumps({**cfg,'precision':opts.precision,'seconds':time.time()-started,'steps':trainer.state.global_step,'best_checkpoint':trainer.state.best_model_checkpoint,'arguments':arguments},indent=2,default=str))
        del trainer
    print('Saved a new reproduction run. Use evaluate.py --adapter with its continuation adapter, initially on validation data.')

if __name__ == '__main__':
    main()
