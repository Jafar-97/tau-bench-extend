# τ-bench-extend

**An extension of Sierra's [τ-bench](https://github.com/sierra-research/tau-bench) that adds new domains and a consistency scoring engine.**

Built by [Jafar](https://github.com/jafar-97) on top of Sierra's open-source benchmark framework.

---

## What This Adds

Sierra's τ-bench covers **retail** and **airline** domains. Their own research notes this as a limitation:

> *"τ-bench's limited coverage of only two domains"* cited in LAM Simulator (ICLR 2025)

This project adds:

### 1. 🏥 New Domains
| Domain | Tasks | Description |
|--------|-------|-------------|
| `healthcare` | 50 | Patient scheduling, prescription inquiries, insurance coverage questions |
| `insurance` | 40 | Claims processing, policy lookups, coverage disputes |
| `ecommerce` | 45 | Subscription management, return disputes, fraud escalations |

### 2. 📊 Consistency Scorer
Sierra's research found agents succeed in **<25% of tasks when repeated 8 times**. The consistency scorer:
- Runs the **same task N times** against any agent
- Computes a **consistency score** (how often it gets the same correct answer)
- Identifies **failure patterns** where exactly the agent breaks
- Generates a **full report** with per-task breakdowns

### 3. 🔴 Adversarial Test Suite
A curated set of **edge-case inputs** that expose:
- Policy boundary violations
- Brand safety failures 
- Hallucinated refund amounts / policy details
- Context-window drop-off in long conversations

---

## Quickstart

```bash
git clone https://github.com/jafar-97/tau-bench-extend
cd tau-bench-extend
pip install -e .
```

Set your API key:
```bash
export ANTHROPIC_API_KEY=your_key_here
# or
export OPENAI_API_KEY=your_key_here
```

### Run a new domain
```bash
python run_eval.py --domain healthcare --model claude-sonnet-4-6 --num-tasks 10
```

### Run the consistency scorer
```bash
python run_consistency.py --domain retail --model gpt-4o --trials 8 --task-id 42
```

### Run the adversarial suite
```bash
python run_adversarial.py --domain healthcare --model claude-sonnet-4-6
```

### Generate full report
```bash
python report.py --results-dir ./results --output report.html
```

---

## Results

Consistency scores across domains on an LLM (3 trials per task, real API runs):

| Domain | Tasks | Pass@1 | Consistency@3 | Avg Failure Turn |
|--------|-------|--------|---------------|-----------------|
| healthcare | 10 | 20% | 96.7% | 2.8 |
| insurance | 8 | 25% | 100% | 2.7 |
| ecommerce | 10 | 30% | 100% | 2.7 |

**Key finding:** High consistency but low pass rate means the agent is *consistently failing* 
it reliably uses the wrong tools or doesn't complete tasks. Failures cluster at Turn 2.7,
confirming Sierra's own research about early conversation breakdown.

The consistency@N metric exposes something pass@1 hides: an agent that always fails the same
way is actually easier to fix than one that randomly passes and fails. The failure mode breakdown
shows `incomplete_action` (agent stops before task is done) as the dominant issue across all
three domains a clear signal for where to focus supervisor improvements.

---

## Project Structure

```
tau-bench-extend/
├── tau_bench_extend/
│ ├── core/
│ │ ├── consistency_scorer.py # Multi-trial consistency engine
│ │ ├── adversarial.py # Adversarial test case generator
│ │ ├── evaluator.py # Base evaluator (wraps τ-bench)
│ │ └── reporter.py # HTML/JSON report generator
│ └── domains/
│ ├── healthcare/
│ │ ├── tasks.py # 50 healthcare tasks
│ │ ├── policy.md # Domain policy document
│ │ └── tools.py # Healthcare-specific tools
│ ├── insurance/
│ │ ├── tasks.py
│ │ ├── policy.md
│ │ └── tools.py
│ └── ecommerce/
│ ├── tasks.py
│ ├── policy.md
│ └── tools.py
├── run_eval.py # Main eval runner
├── run_consistency.py # Consistency scorer CLI
├── run_adversarial.py # Adversarial suite runner
├── report.py # Report generator
└── results/ # Output directory
```

---

## Why This Matters

Sierra's own benchmark paper showed:
- GPT-4 succeeds on **<50% of tasks**
- Consistency (same task, 8 trials) drops to **~25%**

This extension surfaces *where* and *why* agents fail across more real-world domains giving agent engineers actionable signal for improvement.

---

## Citation

If you use this work, please also cite the original τ-bench:

```bibtex
@misc{yao2024tau,
 title={$\tau$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains},
 author={Shunyu Yao and Noah Shinn and Pedram Razavi and Karthik Narasimhan},
 year={2024},
 eprint={2406.12045},
 archivePrefix={arXiv}
}
```

---

## Contributing

Issues and PRs welcome. Especially interested in:
- New domain contributions
- Additional adversarial patterns
- Integration with τ²-bench / τ³-bench

Contact: jafar97dev@gmail.com
