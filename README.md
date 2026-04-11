# SuiDistro

**SuiDistro** is a Python library and CLI helper for distributing SUI tokens to
a list of recipients in bulk.  It supports both live on-chain transfers (via
[pysui](https://github.com/FrankC01/pysui)) and a *dry-run* simulation mode so
you can verify your recipient list without spending gas.

---

## Features

* Load recipients from a **CSV** or **JSON** file.
* Specify amounts in **SUI** (human-readable) or **MIST** (raw integer).
* **Dry-run** mode – log what would be sent without submitting any transactions.
* Per-transfer error isolation – a single failure doesn't abort the whole run.
* Clean summary of total SUI sent, successes, and failures.

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Quick-start

### 1. Prepare a recipient list

**CSV** (`config/example_recipients.csv`):

```csv
address,amount_sui,label
0x0000000000000000000000000000000000000000000000000000000000000001,10.5,Alice
0x0000000000000000000000000000000000000000000000000000000000000002,25.0,Bob
```

**JSON** (`config/example_recipients.json`):

```json
[
  {"address": "0x...", "amount_sui": 10.5, "label": "Alice"},
  {"address": "0x...", "amount_sui": 25.0, "label": "Bob"}
]
```

### 2. Run a dry-run

```python
from src import SuiDistributor

distributor = SuiDistributor.from_rpc(
    rpc_url="https://fullnode.mainnet.sui.io:443",
    signer="0x<your-address>",
    dry_run=True,
)
recipients = SuiDistributor.load_recipients_csv("config/example_recipients.csv")
summary = distributor.distribute(recipients)

print(f"Would send {summary.total_sui_sent:.4f} SUI to {len(summary.succeeded)} recipients")
```

### 3. Execute live transfers

```python
from src import SuiDistributor

distributor = SuiDistributor.from_rpc(
    rpc_url="https://fullnode.mainnet.sui.io:443",
    signer="0x<your-address>",
    keystore_path="/path/to/sui.keystore",
)
recipients = SuiDistributor.load_recipients_json("config/example_recipients.json")
summary = distributor.distribute(recipients)

print(f"Sent {summary.total_sui_sent:.4f} SUI")
for result in summary.failed:
    print(f"  FAILED {result.recipient.address}: {result.error}")
```

---

## Project structure

```
SuiDistro/
├── config/
│   ├── example_recipients.csv   # Example CSV recipient list
│   └── example_recipients.json  # Example JSON recipient list
├── src/
│   ├── __init__.py
│   ├── distributor.py           # Core SuiDistributor class
│   └── models.py                # Recipient, DistributionResult, DistributionSummary
├── tests/
│   ├── test_distributor.py      # Tests for SuiDistributor
│   └── test_models.py           # Tests for data models
├── requirements.txt
└── requirements-dev.txt
```

---

## Running tests

```bash
pip install -r requirements-dev.txt
pytest
```

---

## License

MIT
