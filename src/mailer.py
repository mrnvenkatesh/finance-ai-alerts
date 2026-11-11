"""
Mailer Module for Weekly Finance & Agentic AI Intelligence Digest.

Renders executive financial-grade HTML & plain-text briefings using Jinja2 and delivers via SMTP.
Features a luxury terminal aesthetic with emerald, cyan, and amber financial market accents.
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import re
import smtplib
from typing import Optional

from jinja2 import Template

try:
    from src.synthesizer import WeeklyDigestContent
except ImportError:
    from synthesizer import WeeklyDigestContent

logger = logging.getLogger("FinanceMailer")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Weekly Finance AI & Agentic Intelligence Briefing — {{ content.date_str }}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Outfit:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body {
      margin: 0;
      padding: 0;
      background-color: #05070e;
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: #e2e8f0;
      -webkit-font-smoothing: antialiased;
    }
    .wrapper {
      width: 100%;
      background-color: #05070e;
      background-image: radial-gradient(circle at 50% 0%, rgba(16, 185, 129, 0.15) 0%, rgba(5, 7, 14, 0) 65%);
      padding: 40px 15px;
      box-sizing: border-box;
    }
    .container {
      max-width: 700px;
      margin: 0 auto;
      background: #0b1120;
      border: 1px solid rgba(16, 185, 129, 0.25);
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.9), 0 0 40px rgba(16, 185, 129, 0.08);
    }
    .energy-bar {
      height: 4px;
      background: linear-gradient(90deg, #10b981 0%, #06b6d4 50%, #f59e0b 100%);
      width: 100%;
    }
    .header {
      background: linear-gradient(180deg, rgba(6, 78, 59, 0.35) 0%, rgba(11, 17, 32, 0.95) 100%);
      padding: 34px 32px 26px;
      text-align: left;
      border-bottom: 1px solid rgba(16, 185, 129, 0.2);
    }
    .header-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
    }
    .header-badge {
      display: inline-flex;
      align-items: center;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #34d399;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1.2px;
      text-transform: uppercase;
      padding: 5px 12px;
      border-radius: 20px;
    }
    .pulse-dot {
      display: inline-block;
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
      margin-right: 8px;
    }
    .system-pill {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: #94a3b8;
      letter-spacing: 0.5px;
    }
    .header h1 {
      margin: 0;
      font-family: 'Outfit', sans-serif;
      color: #ffffff;
      font-size: 27px;
      font-weight: 800;
      line-height: 1.25;
      letter-spacing: -0.3px;
    }
    .gradient-text {
      background: linear-gradient(135deg, #10b981 0%, #06b6d4 50%, #38bdf8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .header-date {
      margin: 8px 0 0 0;
      color: #94a3b8;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .telemetry-strip {
      margin-top: 18px;
      padding-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      font-size: 12px;
      color: #94a3b8;
      font-family: 'JetBrains Mono', monospace;
    }
    .telemetry-chip {
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 6px;
      padding: 4px 10px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .telemetry-chip strong {
      color: #10b981;
    }
    .section {
      padding: 26px 30px;
      border-bottom: 1px solid rgba(16, 185, 129, 0.12);
    }
    .section-title {
      font-family: 'Outfit', sans-serif;
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1.2px;
      color: #10b981;
      margin-top: 0;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .macro-box {
      background: rgba(15, 23, 42, 0.65);
      border-left: 3px solid #10b981;
      border-radius: 0 8px 8px 0;
      padding: 18px 20px;
      font-size: 15px;
      line-height: 1.65;
      color: #cbd5e1;
    }
    .spotlight-card {
      background: linear-gradient(145deg, rgba(16, 185, 129, 0.08) 0%, rgba(15, 23, 42, 0.8) 100%);
      border: 1px solid rgba(16, 185, 129, 0.35);
      border-radius: 12px;
      padding: 22px;
      margin-bottom: 8px;
    }
    .spotlight-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .spotlight-inst {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      color: #f59e0b;
      letter-spacing: 1px;
    }
    .spotlight-theme {
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.35);
      color: #fbbf24;
      font-size: 10px;
      font-family: 'JetBrains Mono', monospace;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }
    .spotlight-title {
      margin: 0 0 10px 0;
      font-family: 'Outfit', sans-serif;
      font-size: 18px;
      font-weight: 700;
      line-height: 1.35;
      color: #ffffff;
    }
    .spotlight-analysis {
      margin: 0 0 12px 0;
      font-size: 14px;
      line-height: 1.6;
      color: #cbd5e1;
    }
    .spotlight-link {
      font-size: 12px;
      font-family: 'JetBrains Mono', monospace;
      color: #10b981;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .spotlight-link:hover {
      text-decoration: underline;
    }
    .card {
      background: rgba(15, 23, 42, 0.55);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 16px;
      transition: all 0.2s ease;
    }
    .card:hover {
      border-color: rgba(16, 185, 129, 0.35);
      background: rgba(15, 23, 42, 0.85);
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .tag {
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid transparent;
    }
    .tag-InstitutionalDeployment {
      background: rgba(59, 130, 246, 0.15);
      border-color: rgba(59, 130, 246, 0.35);
      color: #60a5fa;
    }
    .tag-AgenticAIAutomation, .tag-AgenticAI {
      background: rgba(16, 185, 129, 0.15);
      border-color: rgba(16, 185, 129, 0.35);
      color: #34d399;
    }
    .tag-QuantTrading {
      background: rgba(6, 182, 212, 0.15);
      border-color: rgba(6, 182, 212, 0.35);
      color: #22d3ee;
    }
    .tag-FinTechPayments {
      background: rgba(168, 85, 247, 0.15);
      border-color: rgba(168, 85, 247, 0.35);
      color: #c084fc;
    }
    .tag-RegTechCompliance {
      background: rgba(245, 158, 11, 0.15);
      border-color: rgba(245, 158, 11, 0.35);
      color: #fbbf24;
    }
    .tag-AppliedResearch {
      background: rgba(244, 63, 94, 0.15);
      border-color: rgba(244, 63, 94, 0.35);
      color: #fb7185;
    }
    .source-name {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: #64748b;
    }
    .card-title {
      margin: 0 0 10px 0;
      font-family: 'Outfit', sans-serif;
      font-size: 17px;
      font-weight: 700;
      line-height: 1.35;
    }
    .card-title a {
      color: #ffffff;
      text-decoration: none;
    }
    .card-title a:hover {
      color: #10b981;
    }
    .card-summary {
      margin: 0 0 10px 0;
      font-size: 14px;
      line-height: 1.6;
      color: #cbd5e1;
    }
    .card-takeaway {
      background: rgba(6, 78, 59, 0.2);
      border-left: 2px solid #10b981;
      padding: 6px 12px;
      border-radius: 0 4px 4px 0;
      font-size: 12px;
      color: #a7f3d0;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-weight: 500;
    }
    .footer {
      padding: 30px;
      text-align: center;
      background: #070c18;
      border-top: 1px solid rgba(16, 185, 129, 0.15);
    }
    .footer-note {
      margin: 6px 0;
      color: #64748b;
      font-size: 13px;
    }
    .footer-subnote {
      margin: 2px 0;
      font-size: 11px;
      color: #475569;
      font-family: 'JetBrains Mono', monospace;
    }
    .footer-contribute {
      margin-top: 18px;
      padding-top: 16px;
      border-top: 1px dashed rgba(16, 185, 129, 0.15);
    }
    .footer-contribute a {
      color: #34d399;
      text-decoration: none;
      font-weight: 600;
      font-size: 12px;
      font-family: 'JetBrains Mono', monospace;
      padding: 7px 16px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: 6px;
      display: inline-block;
    }
    .footer-contribute a:hover {
      background: rgba(16, 185, 129, 0.2);
      border-color: #10b981;
      color: #6ee7b7;
    }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="container">
      
      <!-- Energy Bar -->
      <div class="energy-bar"></div>

      <!-- Header -->
      <div class="header">
        <div class="header-top">
          <span class="header-badge">
            <span class="pulse-dot"></span>FinAI Radar &bull; Weekly
          </span>
          <span class="system-pill">Every Saturday 09:00 AM IST</span>
        </div>
        <h1>Finance & Agentic AI <span class="gradient-text">Intelligence Briefing</span></h1>
        <p class="header-date">
          <span>⚡ {{ content.date_str }}</span>
          <span>&bull;</span>
          <span>7-Day Strategic Intelligence Cycle</span>
        </p>

        <!-- Telemetry Strip -->
        <div class="telemetry-strip">
          <span class="telemetry-chip">
            📡 Feeds: <strong>{{ content.total_sources_scanned }}</strong>
          </span>
          <span class="telemetry-chip">
            ⚡ Ingested: <strong>{{ content.total_items_ingested }}</strong>
          </span>
          <span class="telemetry-chip">
            🎯 Strategic Stories: <strong>{{ content.top_breakthroughs|length }}</strong>
          </span>
        </div>
      </div>

      <!-- Section 1: Executive Macro Overview -->
      <div class="section">
        <div class="section-title">
          <span>⚡</span>
          <span>Executive Macro Radar (Week in Review)</span>
        </div>
        <div class="macro-box">
          {{ content.macro_overview }}
        </div>
      </div>

      {% if content.spotlight %}
      <!-- Section 2: Strategic Implementation Spotlight -->
      <div class="section">
        <div class="section-title">
          <span>🏆</span>
          <span>Strategic Implementation Spotlight</span>
        </div>
        <div class="spotlight-card">
          <div class="spotlight-header">
            <span class="spotlight-inst">{{ content.spotlight.institution }}</span>
            <span class="spotlight-theme">{{ content.spotlight.theme }}</span>
          </div>
          <h3 class="spotlight-title">{{ content.spotlight.title }}</h3>
          <p class="spotlight-analysis">{{ content.spotlight.analysis }}</p>
          {% if content.spotlight.url %}
          <a href="{{ content.spotlight.url }}" target="_blank" rel="noopener" class="spotlight-link">
            Examine Source Analysis &rarr;
          </a>
          {% endif %}
        </div>
      </div>
      {% endif %}

      <!-- Section 3: Core Finance AI Breakthroughs & Deployments -->
      <div class="section">
        <div class="section-title">
          <span>📊</span>
          <span>Institutional Deployments & Agentic Workflows</span>
        </div>
        {% for story in content.top_breakthroughs %}
        <div class="card">
          <div class="card-header">
            <span class="tag tag-{{ story.tag.replace(' ', '').replace('&', '') }}">{{ story.tag }}</span>
            <span class="source-name">{{ story.source }}</span>
          </div>
          <h3 class="card-title">
            <a href="{{ story.url }}" target="_blank" rel="noopener">{{ story.headline }} &rarr;</a>
          </h3>
          <p class="card-summary">{{ story.summary }}</p>
          {% if story.key_takeaway %}
          <div class="card-takeaway">
            <strong>Key Strategic Takeaway:</strong> {{ story.key_takeaway }}
          </div>
          {% endif %}
        </div>
        {% endfor %}
      </div>

      {% if content.notable_initiatives %}
      <!-- Section 4: Notable Quant & Product Initiatives -->
      <div class="section">
        <div class="section-title">
          <span>📈</span>
          <span>Notable Quant & FinTech Launches</span>
        </div>
        {% for item in content.notable_initiatives %}
        <div class="card">
          <div class="card-header">
            <span class="tag tag-{{ item.tag.replace(' ', '').replace('&', '') }}">{{ item.tag }}</span>
            <span class="source-name">{{ item.source }}</span>
          </div>
          <h3 class="card-title">
            <a href="{{ item.url }}" target="_blank" rel="noopener">{{ item.headline }} &rarr;</a>
          </h3>
          <p class="card-summary">{{ item.summary }}</p>
        </div>
        {% endfor %}
      </div>
      {% endif %}

      <!-- Footer -->
      <div class="footer">
        <p class="footer-note">Weekly Finance AI & Agentic Intelligence Aggregator &bull; Autonomous Briefing Pipeline</p>
        <p class="footer-subnote">Delivered Weekly Every Saturday at 09:00 AM IST &bull; Asia/Kolkata</p>
        <div class="footer-contribute">
          <p style="margin: 0 0 10px 0; color: #94a3b8; font-size: 12px;">Want to suggest new finance AI sources or improvements?</p>
          <a href="https://github.com/mrnvenkatesh/finance-ai-alerts" target="_blank" rel="noopener">
            Contribute on GitHub &rarr;
          </a>
        </div>
      </div>

    </div>
  </div>
</body>
</html>
"""

PLAIN_TEXT_TEMPLATE = """WEEKLY FINANCE & AGENTIC AI INTELLIGENCE BRIEFING — {{ content.date_str }}
====================================================================
Schedule: Every Saturday at 09:00 AM IST (Asia/Kolkata)
Monitored: {{ content.total_items_ingested }} items across {{ content.total_sources_scanned }} feeds

EXECUTIVE MACRO RADAR (WEEK IN REVIEW)
--------------------------------------------------------------------
{{ content.macro_overview }}

{% if content.spotlight %}
STRATEGIC IMPLEMENTATION SPOTLIGHT
--------------------------------------------------------------------
Title: {{ content.spotlight.title }}
Institution: {{ content.spotlight.institution }} | Theme: {{ content.spotlight.theme }}
Analysis: {{ content.spotlight.analysis }}
Link: {{ content.spotlight.url }}
{% endif %}

INSTITUTIONAL DEPLOYMENTS & AGENTIC WORKFLOWS
--------------------------------------------------------------------
{% for story in content.top_breakthroughs %}
[{{ story.tag }}] {{ story.headline }}
Source: {{ story.source }}
Link: {{ story.url }}
Summary: {{ story.summary }}
{% if story.key_takeaway %}Takeaway: {{ story.key_takeaway }}{% endif %}
--------------------------------------------------------------------
{% endfor %}

{% if content.notable_initiatives %}
NOTABLE QUANT & FINTECH LAUNCHES
--------------------------------------------------------------------
{% for item in content.notable_initiatives %}
[{{ item.tag }}] {{ item.headline }}
Source: {{ item.source }}
Link: {{ item.url }}
Summary: {{ item.summary }}
--------------------------------------------------------------------
{% endfor %}
{% endif %}

====================================================================
Delivered automatically via Scheduled Weekly Pipeline (Saturday 9:00 AM IST).
Contribute or suggest improvements on GitHub: https://github.com/mrnvenkatesh/finance-ai-alerts
"""


class FinanceDigestMailer:
    """Renders and delivers weekly finance briefings."""

    def __init__(self):
        self.sender_email = os.getenv("SENDER_EMAIL", "finance-digest@domain.com").strip()
        recipients_raw = os.getenv("RECIPIENT_EMAIL", "")
        self.recipient_list = [r.strip() for r in re.split(r"[,;]+", recipients_raw) if r.strip()]
        self.smtp_host = os.getenv("SMTP_HOST", "").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "").strip()
        self.smtp_pass = os.getenv("SMTP_PASS", "").strip()
        self.use_bcc = os.getenv("USE_BCC", "true").strip().lower() in ("true", "1", "yes")

    def render_html(self, content: WeeklyDigestContent) -> str:
        """Renders responsive HTML template."""
        template = Template(HTML_TEMPLATE)
        return template.render(content=content)

    def render_text(self, content: WeeklyDigestContent) -> str:
        """Renders plain text fallback template."""
        template = Template(PLAIN_TEXT_TEMPLATE)
        return template.render(content=content)

    def save_local_preview(self, content: WeeklyDigestContent, output_dir: str = "output") -> tuple[str, str]:
        """Saves rendered HTML and plain text files for local inspection."""
        os.makedirs(output_dir, exist_ok=True)
        safe_date = content.date_str.replace(" ", "_").replace(",", "").lower()
        html_path = os.path.join(output_dir, f"digest_finance_{safe_date}.html")
        text_path = os.path.join(output_dir, f"digest_finance_{safe_date}.txt")

        html_body = self.render_html(content)
        text_body = self.render_text(content)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_body)

        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text_body)

        logger.info(f"Saved local HTML preview: {html_path}")
        logger.info(f"Saved local text preview: {text_path}")
        return html_path, text_path

    def send_digest(self, content: WeeklyDigestContent, dry_run: bool = False) -> bool:
        """Sends briefing via SMTP or saves to disk if dry_run=True or SMTP unconfigured."""
        html_body = self.render_html(content)
        text_body = self.render_text(content)

        # Always save local preview for auditing and browser preview
        self.save_local_preview(content)

        if dry_run or not self.recipient_list or not self.smtp_host:
            logger.info("Dry-run mode active or SMTP credentials missing. Written output to local preview files.")
            return True

        subject = f"Weekly Finance & Agentic AI Intelligence Briefing — {content.date_str}"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender_email

        if self.use_bcc and len(self.recipient_list) > 1:
            msg["To"] = self.sender_email
        else:
            msg["To"] = ", ".join(self.recipient_list)

        part1 = MIMEText(text_body, "plain", "utf-8")
        part2 = MIMEText(html_body, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        try:
            logger.info(f"Connecting to SMTP server {self.smtp_host}:{self.smtp_port}...")
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15)
            server.ehlo()

            if self.smtp_port == 587:
                server.starttls()
                server.ehlo()

            if self.smtp_user and self.smtp_pass:
                server.login(self.smtp_user, self.smtp_pass)

            server.sendmail(self.sender_email, self.recipient_list, msg.as_string())
            server.quit()
            delivery_mode = "BCC" if (self.use_bcc and len(self.recipient_list) > 1) else "standard"
            logger.info(f"Successfully delivered weekly finance briefing ({delivery_mode}) to {len(self.recipient_list)} recipient(s): {', '.join(self.recipient_list)}")
            return True
        except Exception as e:
            logger.error(f"Failed to deliver email via SMTP: {e}")
            logger.info("Saving fallback HTML/text files locally.")
            self.save_local_preview(content)
            return False


if __name__ == "__main__":
    from datetime import datetime
    try:
        from src.synthesizer import WeeklyDigestContent, StoryBrief, StrategicSpotlight
    except ImportError:
        from synthesizer import WeeklyDigestContent, StoryBrief, StrategicSpotlight

    sample_content = WeeklyDigestContent(
        date_str=datetime.now().strftime("%B %d, %Y"),
        macro_overview="Global investment banks are aggressively deploying agentic multi-model architectures for autonomous trade reconciliation, while regulatory watchdogs prepare new compliance guidelines.",
        spotlight=StrategicSpotlight(
            title="JPMorgan Launches Autonomous Research Agent Network",
            institution="JPMorgan Chase",
            theme="Autonomous Financial Analysis",
            analysis="The bank rolled out specialized agents capable of parsing SEC 10-K filings, earnings transcripts, and quantitative metrics to generate synthesized analyst briefings.",
            url="https://example.com/jpmorgan-ai-agent",
        ),
        top_breakthroughs=[
            StoryBrief(
                headline="Citigroup Integrates Multi-Agent LLMs for Risk & Compliance Auditing",
                url="https://example.com/citi-risk-agents",
                source="Finextra AI & ML",
                tag="Agentic AI & Automation",
                summary="Citigroup completed a pilot replacing rule-based AML checks with autonomous reasoning agents that synthesize transaction graphs.",
                key_takeaway="Reduces false-positive alert remediation time by 45%.",
            ),
            StoryBrief(
                headline="BlackRock Expands Aladdin With Generative Scenario Simulation",
                url="https://example.com/blackrock-aladdin",
                source="Google News (Wall Street AI)",
                tag="Institutional Deployment",
                summary="BlackRock introduced generative stress-testing models within Aladdin, allowing portfolio managers to simulate macroeconomic shocks.",
                key_takeaway="Enables real-time risk assessment across multi-asset portfolios.",
            ),
        ],
        total_sources_scanned=8,
        total_items_ingested=124,
    )

    mailer = FinanceDigestMailer()
    mailer.save_local_preview(sample_content)

