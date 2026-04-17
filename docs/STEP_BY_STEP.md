# Step-by-Step Guide: From ZIP to Cold Email Sent

## What You Have Built

A benchmark extension for Sierra AI called tau-bench-extend.

Sierra built tau-bench to measure how reliable their AI agents are. It only covers
retail and airline domains. Sierra's own blog said healthcare and financial services
are the hardest domains for their agent supervisors, but there is no benchmark for those.

You built that benchmark. Three new domains (healthcare, insurance, ecommerce), a
consistency scorer that runs the same task multiple times to measure reliability, and
an adversarial test suite for edge cases like hallucination bait and prompt injection.

Real results from 84 actual LLM API calls:
- Healthcare: Pass@1 = 20%, Consistency@3 = 96.7%, Avg failure turn = 2.8
- Insurance: Pass@1 = 25%, Consistency@3 = 100%, Avg failure turn = 2.7
- Ecommerce: Pass@1 = 30%, Consistency@3 = 100%, Avg failure turn = 2.7

Target: Clay Bavor, Co-founder of Sierra AI
Visa: Sierra's own careers page says they sponsor visas.

---

## Step 1: Rotate Your Anthropic API Key

You shared your API key during this session. Rotate it now before anything else.

1. Go to console.anthropic.com
2. Click API Keys in the left sidebar
3. Delete the key that starts with sk-ant-api03-kgoUC...
4. Create a new key
5. Save it somewhere safe

---

## Step 2: Push to GitHub

1. Unzip tau-bench-extend-FINAL.zip on your computer
2. Go to github.com and create a new public repo called "tau-bench-extend"
3. Open terminal in the unzipped folder and run:

```
git init
git add .
git commit -m "Initial commit: tau-bench-extend with healthcare, insurance, ecommerce domains"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tau-bench-extend.git
git push -u origin main
```

4. On GitHub, go to your repo Settings > About and add a description:
 "Extension of Sierra's tau-bench benchmark with healthcare, insurance and ecommerce domains plus a consistency scorer"

5. Pin it to your GitHub profile so it shows up first

---

## Step 3: Run It With Your Real API Key (Optional but Recommended)

If you want to include fresh results in your email:

1. Copy .env.example to .env
2. Add your new API key: ANTHROPIC_API_KEY=your_new_key_here
3. Run:

```
pip install -e .
python run_eval.py --domain healthcare --model gpt-4o --provider anthropic --num-tasks 10 --trials 3
python run_eval.py --domain insurance --model gpt-4o --provider anthropic --num-tasks 8 --trials 3
python run_eval.py --domain ecommerce --model gpt-4o --provider anthropic --num-tasks 10 --trials 3
```

This will generate fresh HTML reports in the results/ folder. Open them in your browser
and take a screenshot for the Loom.

---

## Step 4: Record the Loom Video

Keep it under 4 minutes. Fast and technical is better than slow and polished.

Script is in docs/loom_script.md. Short version:

1. Open your terminal. cd into the project folder.
2. Show the folder structure: ls -la
3. Run one eval live: python run_eval.py --domain healthcare --model gpt-4o --provider anthropic --num-tasks 5 --trials 3
4. While it runs, talk through what is happening (tasks, trials, consistency)
5. When it finishes, open the HTML report in the browser
6. Point out: Pass@1 vs Consistency@3 - the gap is the story
7. Show the Sierra quote block on the report - "healthcare is the hardest"
8. Show the failure mode breakdown
9. End with: "This is the crash test infrastructure for the domains Sierra called hardest"

Upload to loom.com and copy the share link.

---

## Step 5: Send the Cold Email

The email is in docs/cold_email_clay_bavor.txt

Before sending:
1. Add your Loom link where it says [ADD LINK BEFORE SENDING]
2. Add your GitHub repo link (replace github.com/jafar-97/tau-bench-extend with your actual URL)
3. Double-check your name and contact info at the bottom

How to find Clay Bavor:
- LinkedIn: search "Clay Bavor Sierra" - he is active there
- Email: try clay@sierra.ai (common pattern for co-founders)
- Twitter/X: @claybavor

Subject line is already in the email. Use it as-is.

Send it as plain text, not HTML. Plain text emails from real engineers look better
than formatted marketing emails.

---

## Step 6: Follow Up

If no reply in 5 days, send one follow-up. Keep it to 2 sentences:

"Hi Clay, following up on the tau-bench-extend repo I sent over. Happy to walk through
it on a quick call if useful."

That's it. No more than one follow-up.

---

## What to Say if He Replies

If he asks what role you are looking for:

"I am an AI/ML engineer (MS in AI from University of Cincinnati, 2 years production
experience building LLM systems). I am on F1 OPT right now and would need visa
sponsorship. I saw that Sierra sponsors visas. I am interested in an agent engineering
or platform engineering role."

If he asks a technical question about the project, answer it directly and concisely.
Do not oversell. Just answer the question.

---

## File Reference

| File | What it is |
|------|-----------|
| run_eval.py | Runs a full domain eval with consistency scoring |
| run_consistency.py | Runs one task N times to measure consistency |
| run_adversarial.py | Runs the adversarial edge case suite |
| results/*.html | The Sierra-branded HTML reports |
| docs/cold_email_clay_bavor.txt | The cold email, ready to send |
| docs/loom_script.md | Script for the Loom recording |
| .env.example | Copy this to .env and add your API key |
