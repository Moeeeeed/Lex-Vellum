import sys
import os
from datetime import datetime

# Add app to path
sys.path.append(os.path.join(os.getcwd(), "app"))
sys.path.append(os.getcwd())

from app.services.pdf_utils import render_template_to_pdf

def test_pdf_generation():
    print("Testing ToS PDF generation...")
    try:
        tos_pdf = render_template_to_pdf("tos_pdf.html", {
            "doc_id": 1,
            "status": "Approved",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "lawyer_name": "Test Lawyer",
            "text": "This is a test Terms of Service document content."
        })
        with open("test_tos.pdf", "wb") as f:
            f.write(tos_pdf)
        print("ToS PDF generated successfully: test_tos.pdf")
    except Exception as e:
        print(f"ToS PDF generation failed: {e}")

    print("\nTesting Audit Trail PDF generation...")
    try:
        # Mock audit trail entries
        class MockAudit:
            def __init__(self, timestamp, user_name, action, original_text, new_text):
                self.timestamp = timestamp
                self.user_name = user_name
                self.action = action
                self.original_text = original_text
                self.new_text = new_text

        audit_trail = [
            MockAudit("2026-05-07 10:00", "CEO", "Initial Submission", "N/A", "Initial text..."),
            MockAudit("2026-05-07 10:05", "Lawyer", "Compliance Remediation", "Old text", "New compliant text"),
            MockAudit("2026-05-07 10:10", "Lawyer", "Final Approval", "Pending Review", "Approved")
        ]

        audit_pdf = render_template_to_pdf("audit_pdf.html", {
            "doc_id": 1,
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "audit_trail": audit_trail
        })
        with open("test_audit.pdf", "wb") as f:
            f.write(audit_pdf)
        print("Audit Trail PDF generated successfully: test_audit.pdf")
    except Exception as e:
        print(f"Audit Trail PDF generation failed: {e}")

if __name__ == "__main__":
    test_pdf_generation()
