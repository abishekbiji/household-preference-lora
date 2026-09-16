# Final evaluation errors

All 12 non-exact cases from the recorded adapted predictions. Five fail schema validation; seven pass the schema but fail exact task correctness. These are observations, not new model executions.

## final-001 — schema error

Input:
```json
{
  "current_state": {
    "adults": 9,
    "budget_eur": 180,
    "dairy": "dairy_free"
  },
  "instruction": "The booking form has the wrong headcount. Please enter eleven in its adults field."
}
```

Expected:
```json
{"updates": {"adults": 11}, "clarify": []}
```

Actual:
```text
{"updates":{"adults":11},"clarify":["adults"]}
```

## final-005 — semantic error

Input:
```json
{
  "current_state": {
    "adults": 7,
    "budget_eur": 185,
    "dairy": "no_restriction"
  },
  "instruction": "Please record a 132.50 euro spending budget and a dairy-free preference for this order."
}
```

Expected:
```json
{"updates": {"budget_eur": 132.5, "dairy": "dairy_free"}, "clarify": []}
```

Actual:
```text
{"updates":{"budget_eur":132.5},"clarify":["adults"]}
```

## final-008 — schema error

Input:
```json
{
  "current_state": {
    "adults": 3,
    "budget_eur": 88,
    "dairy": "dairy_free"
  },
  "instruction": "I wrote 12 in the adult-count box by mistake. Replace that entry with 10."
}
```

Expected:
```json
{"updates": {"adults": 10}, "clarify": []}
```

Actual:
```text
{"updates":{"adults":10},"clarify":["adults"]}
```

## final-011 — schema error

Input:
```json
{
  "current_state": {
    "adults": 4,
    "budget_eur": 98,
    "dairy": "no_restriction"
  },
  "instruction": "Do not apply the suggested 160 euro budget. The budget I want is 117 euros."
}
```

Expected:
```json
{"updates": {"budget_eur": 117}, "clarify": []}
```

Actual:
```text
{"updates":{"budget_eur":117},"clarify":["budget_eur"]}
```

## final-012 — schema error

Input:
```json
{
  "current_state": {
    "adults": 5,
    "budget_eur": 133,
    "dairy": "dairy_free"
  },
  "instruction": "Our adult count is not 9; it is 8. The budget must not be edited."
}
```

Expected:
```json
{"updates": {"adults": 8}, "clarify": []}
```

Actual:
```text
{"updates":{"adults":8,"budget_eur":133},"clarify":["adults"]}
```

## final-013 — semantic error

Input:
```json
{
  "current_state": {
    "adults": 3,
    "budget_eur": 79,
    "dairy": "dairy_free"
  },
  "instruction": "Two guest lists disagree: one says 8 adults, the other says 11. Neither has been confirmed. The budget is definitely 164 euros."
}
```

Expected:
```json
{"updates": {"budget_eur": 164}, "clarify": ["adults"]}
```

Actual:
```text
{"updates":{"adults":8,"dairy":"dairy_free"},"clarify":[]}
```

## final-014 — schema error

Input:
```json
{
  "current_state": {
    "adults": 6,
    "budget_eur": 142,
    "dairy": "no_restriction"
  },
  "instruction": "Please lower the grocery budget by 15 euros."
}
```

Expected:
```json
{"updates": {}, "clarify": ["budget_eur"]}
```

Actual:
```text
{"updates":{"budget_eur":-15},"clarify":[]}
```

## final-018 — semantic error

Input:
```json
{
  "current_state": {
    "adults": 1,
    "budget_eur": 38,
    "dairy": "no_restriction"
  },
  "instruction": "The current profile is approved in full; no preference edits are authorized."
}
```

Expected:
```json
{"updates": {}, "clarify": []}
```

Actual:
```text
{"updates":{},"clarify":["dairy"]}
```

## final-019 — semantic error

Input:
```json
{
  "current_state": {
    "adults": 4,
    "budget_eur": 106,
    "dairy": "no_restriction"
  },
  "instruction": "The cereal box was crushed on arrival. Can you arrange a replacement?"
}
```

Expected:
```json
{"updates": {}, "clarify": []}
```

Actual:
```text
{"updates":{"dairy":"dairy_free"},"clarify":[]}
```

## final-020 — semantic error

Input:
```json
{
  "current_state": {
    "adults": 2,
    "budget_eur": 64,
    "dairy": "no_restriction"
  },
  "instruction": "Put a carton of dairy-free coconut drink on my shopping list."
}
```

Expected:
```json
{"updates": {}, "clarify": []}
```

Actual:
```text
{"updates":{"dairy":"dairy_free"},"clarify":[]}
```

## final-021 — semantic error

Input:
```json
{
  "current_state": {
    "adults": 7,
    "budget_eur": 192,
    "dairy": "dairy_free"
  },
  "instruction": "Your courier found the entrance straight away today. Much appreciated!"
}
```

Expected:
```json
{"updates": {}, "clarify": []}
```

Actual:
```text
{"updates":{"dairy":"dairy_free"},"clarify":[]}
```

## final-024 — semantic error

Input:
```json
{
  "current_state": {
    "adults": 3,
    "budget_eur": 92,
    "dairy": "no_restriction"
  },
  "instruction": "The grocery allowance should read 104 euros. Leave the other saved preferences alone."
}
```

Expected:
```json
{"updates": {"budget_eur": 104}, "clarify": []}
```

Actual:
```text
{"updates":{"dairy":"dairy_free"},"clarify":[]}
```
