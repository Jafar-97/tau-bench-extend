# Loom Script τ-bench-extend Walkthrough
# Target length: 3-4 minutes max. Fast, technical, confident.

---

## OPENING (15 sec)
"Sierra's τ-bench showed that even GPT-4 achieves only 25% consistency
when repeating the same task 8 times. That gap between pass rate and
consistency is where customer trust breaks down.

I built an extension of τ-bench to measure exactly that across three
new domains Sierra doesn't cover yet."

---

## REPO TOUR (30 sec)
Show GitHub. Point out:
- Three new domains: healthcare / insurance / ecommerce
- Each has: tasks.py (the eval tasks), tools (the API the agent can call),
 policy.md (what the agent must follow)
- Core: consistency_scorer.py, adversarial.py, reporter.py

"The structure mirrors τ-bench so it's compatible and easy to extend."

---

## RUN THE EVAL (60 sec)
Terminal. Run:
 python run_eval.py --domain healthcare --model gpt-4o --trials 5 --num-tasks 10

Watch it run live. Show the Rich output with progress bar.

Point out:
- Pass@1 vs Consistency@5 they're very different
- "This gap is the reliability problem Sierra is solving"

---

## OPEN THE REPORT (45 sec)
Open results/healthcare_gpt-4o_report.html in browser.

Point out:
- The three metric cards: Pass@1, Consistency@5, Avg Failure Turn
- The insight box: "Large consistency gap customers get different outcomes"
- Failure mode breakdown: policy_violation + hallucination are the top two
- Worst consistency tasks table

"Turn 2.8 is where failures happen on average early in the conversation,
which means it's intent understanding, not context loss."

---

## ADVERSARIAL SUITE (45 sec)
Run:
 python run_adversarial.py --domain healthcare --model gpt-4o

Show it testing edge cases:
- Hallucination bait: "my doctor said it's definitely covered"
- Prompt injection: "Ignore your previous instructions..."
- Policy boundary: asking for medical advice

"These are the scenarios that τ-bench doesn't cover but that happen
constantly in real customer conversations."

---

## CLOSE (30 sec)
"The consistency gap, the adversarial failures, the failure turn analysis 
this is the kind of signal agent engineers need to actually improve reliability.

I'd love to contribute this to Sierra's research or engineering work.
Code is linked below."

---

## LOOM TIPS
- Record at 1080p
- Keep terminal font large (18pt+)
- Dark terminal theme
- No music, no intro animation
- Under 4 minutes total
