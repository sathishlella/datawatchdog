import os
import resend
from datetime import datetime


def send_quality_alert(
    email: str,
    dataset_name: str,
    score: float,
    threshold: float,
    issues: list[dict],
) -> bool:
    """Send quality alert email via Resend. Returns True if sent successfully."""
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    if not resend.api_key:
        print(f"[alerter] RESEND_API_KEY not set — skipping email for {dataset_name}")
        return False

    issues_html = "".join(
        f"<li><strong>{i['column']}</strong> ({i['rule_type']}): {i['message']}</li>"
        for i in issues
    )

    html = f"""
    <div style="font-family: system-ui; max-width: 600px; margin: 0 auto;
                background: #080308; color: #e0d0e8; padding: 32px; border-radius: 12px;">
      <h1 style="color: #f9a8d4; font-size: 1.4rem; margin-bottom: 8px;">
        &#x26A0; Data Quality Alert &mdash; {dataset_name}
      </h1>
      <p style="color: #94a3b8; margin-bottom: 24px;">
        {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
      </p>
      <div style="background: #1a0a1a; border: 1px solid #be185d55; border-radius: 8px;
                  padding: 16px 20px; margin-bottom: 20px;">
        <div style="font-size: 2rem; font-weight: 900; color: #f87171;">{score:.1f}</div>
        <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">
          Quality Score (threshold: {threshold:.0f})
        </div>
      </div>
      <h2 style="color: #f9a8d4; font-size: 1rem; margin-bottom: 12px;">Issues Found:</h2>
      <ul style="color: #e0d0e8; line-height: 2;">{issues_html}</ul>
      <p style="margin-top: 24px; color: #64748b; font-size: 0.8rem;">
        Sent by DataWatchdog &middot; Automated data quality monitoring
      </p>
    </div>
    """

    try:
        resend.Emails.send({
            "from": "DataWatchdog <alerts@resend.dev>",
            "to": email,
            "subject": f"Quality Alert: {dataset_name} scored {score:.1f} (below {threshold:.0f})",
            "html": html,
        })
        return True
    except Exception as e:
        print(f"[alerter] Failed to send email: {e}")
        return False
