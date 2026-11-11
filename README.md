# Weekly Finance AI & Agentic Intelligence Digest ⚡

An autonomous, production-ready weekly news aggregator and executive intelligence briefing service focused on **how AI and Agentic AI are being implemented across the global financial sector**.

Every **Saturday at 09:00 AM IST (03:30 AM UTC)**, this service automatically ingests and filters the most critical financial AI developments from the preceding 7 days (168-hour lookback), synthesizes them into an executive briefing using Google Gemini (with OpenAI and offline fallback support), and delivers a responsive, financial-terminal-styled HTML email digest to financial leaders, quantitative researchers, and technology teams.

---

## 🏛️ System Architecture

```
                                ┌──────────────────────────────────────┐
                                │     Specialized Finance Sources      │
                                │  • Finextra AI & Fintech Futures     │
                                │  • Google News (Agentic Finance AI)  │
                                │  • Google News (Wall Street / Banks) │
                                │  • ArXiv q-fin & cs.AI (Filtered)    │
                                │  • Hacker News Finance Discussions   │
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │  1. Ingestion & Smart Deduplication  │
                                │     (src/fetcher.py • 7-day window)  │
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │  2. Financial AI LLM Synthesizer     │
                                │     (src/synthesizer.py)             │
                                │     - Gemini 2.5/Flash & Fallback    │
                                │     - Domain Taxonomy & Spotlight    │
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │  3. Financial-Grade Mailer & HTML    │
                                │     (src/mailer.py • Dark Terminal)  │
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │  4. Automation & Triggers            │
                                │     - APScheduler (Saturdays 9 AM)   │
                                │     - GitHub Actions (cron: 25 3 * * 6)
                                │     - GCP Cloud Run + Cloud Scheduler│
                                └──────────────────────────────────────┘
```

---

## 🎯 Domain Coverage & Taxonomy

The briefing is tailored to answer **how AI and autonomous agents are transforming finance**:

| Category | Focus Area |
| :--- | :--- |
| **🏦 Institutional Deployment** | Tier-1 investment banks (JPMorgan, Goldman Sachs, Morgan Stanley, Citi), asset managers, and hedge funds implementing enterprise AI models into production. |
| **🤖 Agentic AI & Automation** | Multi-agent financial research, automated tool-calling, autonomous KYC/AML triage, document reconciliation, and self-healing agent pipelines. |
| **📈 Quant & Trading** | Algorithmic trading, alpha generation, synthetic financial time series, alternative data processing, and earnings transcript sentiment extraction. |
| **💳 FinTech & Payments** | AI-native neobanks, automated lending and credit underwriting, payment rails, real-time transaction monitoring, and agentic commerce. |
| **⚖️ RegTech & Compliance** | SEC, FINRA, Fed, ECB, and RBI AI oversight, algorithmic auditability, model risk management (SR 11-7), and hallucination prevention in financial math. |
| **🔬 Applied Research** | Academic breakthroughs in quantitative finance, econometric LLMs, financial knowledge graphs, and open-source quant frameworks. |

---

## 📁 Repository Structure

```text
finance-ai-alerts/
├── .env                        # Local credentials & active configuration
├── .env.example                # Template for environment configuration
├── .gitignore                  # Git ignore definitions
├── Dockerfile                  # Container definition for serverless/Cron execution
├── README.md                   # System documentation & setup guide
├── requirements.txt            # Locked Python dependencies
├── deploy_gcp.sh               # Google Cloud Run + Cloud Scheduler automated deployment
├── .github/
│   └── workflows/
│       └── weekly_finance_briefing.yml  # GitHub Actions Saturday automation
├── output/                     # Saved local HTML/text previews
└── src/
    ├── __init__.py             # Package marker
    ├── fetcher.py              # 7-day ingestion, RSS parsing, keyword filtering & deduplication
    ├── synthesizer.py          # Gemini/OpenAI financial domain synthesis & categorization
    ├── mailer.py               # Dark financial terminal HTML & plain-text email renderer
    └── scheduler.py            # CLI entry point & APScheduler weekly Saturday trigger
```

---

## 🚀 Quick Start & Local Setup

### 1. Prerequisites
- Python 3.10+
- Pip package manager

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Verify or edit `.env`:
```env
# LLM Provider Configuration
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# SMTP Email Configuration
SENDER_EMAIL=your_email@gmail.com
RECIPIENT_EMAIL=recipient1@domain.com, recipient2@domain.com
USE_BCC=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# Application Settings
TIMEZONE=Asia/Kolkata
MAX_STORIES=10
HOURS_LOOKBACK=168
```

---

## 🧪 Execution Commands

### Run Immediate Dry-Run (No Email Sent, Writes HTML Preview)
```bash
python src/scheduler.py --now --dry-run
```
Output files will be saved in `output/`:
- `output/digest_finance_[date].html` (Open in any web browser to preview responsive styling)
- `output/digest_finance_[date].txt` (Plain text preview)

### Run Immediate Production Pipeline (Sends Email via SMTP)
```bash
python src/scheduler.py --now
```

### Start Background Scheduler (Runs Every Saturday at 09:00 AM IST)
```bash
python src/scheduler.py --schedule
```

### Custom Lookback Window or Story Count
```bash
# E.g., Look back 10 days and curate up to 12 stories
python src/scheduler.py --now --dry-run --hours 240 --max-stories 12
```

---

## ⚡ GitHub Actions Automation

A pre-configured GitHub Actions workflow is located at `.github/workflows/weekly_finance_briefing.yml`.

### Setup:
1. Push this repository to GitHub.
2. Navigate to **Settings > Secrets and variables > Actions** in your GitHub repository.
3. Add the following repository secrets:
   - `GEMINI_API_KEY`
   - `RECIPIENT_EMAIL`
   - `SENDER_EMAIL`
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USER`
   - `SMTP_PASS`
4. The workflow runs every Saturday at **03:25 UTC (08:55 AM IST)** and can also be triggered manually on-demand with the `workflow_dispatch` button.

---

## ☁️ Google Cloud Platform (GCP) Deployment

Deploy serverlessly as a **Cloud Run Job** triggered every Saturday at **09:00 AM IST** by **Cloud Scheduler**:

```bash
chmod +x deploy_gcp.sh
./deploy_gcp.sh
```

---

## 🐳 Docker Deployment

Build the container image:
```bash
docker build -t weekly-finance-ai-digest .
```

Run container execution locally with `.env`:
```bash
docker run --rm --env-file .env weekly-finance-ai-digest
```

