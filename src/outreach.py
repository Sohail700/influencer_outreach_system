from __future__ import annotations

import csv
import os
import smtplib
import sqlite3
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

from .models import PersonalizedMessage


class OutreachTracker:
    def __init__(self, db_path: str = "out/outreach.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS outreach_log (
                influencer_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                message_id TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                sent_at TEXT,
                status TEXT NOT NULL,
                error TEXT DEFAULT ''
            )
            """
        )
        self.conn.commit()

    def already_sent(self, influencer_id: str) -> bool:
        row = self.conn.execute(
            "SELECT status FROM outreach_log WHERE influencer_id = ?", (influencer_id,)
        ).fetchone()
        return bool(row and row[0] == "sent")

    def record(self, influencer_id: str, email: str, message_id: str, generated_at: str, status: str, error: str = "") -> None:
        sent_at = datetime.now(timezone.utc).isoformat() if status == "sent" else None
        self.conn.execute(
            """
            INSERT INTO outreach_log(influencer_id,email,message_id,generated_at,sent_at,status,error)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(influencer_id) DO UPDATE SET
                email=excluded.email,
                message_id=excluded.message_id,
                generated_at=excluded.generated_at,
                sent_at=excluded.sent_at,
                status=excluded.status,
                error=excluded.error
            """,
            (influencer_id, email, message_id, generated_at, sent_at, status, error),
        )
        self.conn.commit()

    def export_csv(self, output_path: str = "out/outreach_log.csv") -> None:
        rows = self.conn.execute(
            "SELECT influencer_id,email,message_id,generated_at,sent_at,status,error FROM outreach_log ORDER BY generated_at DESC"
        ).fetchall()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["influencer_id", "email", "message_id", "generated_at", "sent_at", "status", "error"])
            writer.writerows(rows)


class OutreachSender:
    def __init__(self, tracker: OutreachTracker, smtp_host: str, smtp_port: int, smtp_username: str, smtp_password: str, smtp_from: str):
        self.tracker = tracker
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_from = smtp_from or smtp_username

    def simulate(self, message: PersonalizedMessage) -> str:
        message_id = f"sim-{message.influencer_id}"
        if message.email == "Not Found":
            self.tracker.record(message.influencer_id, message.email, message_id, message.generated_at, "skipped", "No public email found")
            return "skipped"
        if self.tracker.already_sent(message.influencer_id):
            return "duplicate_blocked"
        self.tracker.record(message.influencer_id, message.email, message_id, message.generated_at, "simulated")
        return "simulated"

    def send(self, message: PersonalizedMessage) -> str:
        if message.email == "Not Found":
            self.tracker.record(message.influencer_id, message.email, f"smtp-{message.influencer_id}", message.generated_at, "skipped", "No public email found")
            return "skipped"
        if self.tracker.already_sent(message.influencer_id):
            return "duplicate_blocked"
        if not all([self.smtp_host, self.smtp_username, self.smtp_password, self.smtp_from]):
            self.tracker.record(message.influencer_id, message.email, f"smtp-{message.influencer_id}", message.generated_at, "failed", "SMTP configuration missing")
            return "failed"

        email = EmailMessage()
        email["From"] = self.smtp_from
        email["To"] = message.email
        email["Subject"] = message.email_subject
        email.set_content(message.email_pitch)
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(email)
            self.tracker.record(message.influencer_id, message.email, f"smtp-{message.influencer_id}", message.generated_at, "sent")
            return "sent"
        except Exception as exc:
            self.tracker.record(message.influencer_id, message.email, f"smtp-{message.influencer_id}", message.generated_at, "failed", str(exc))
            return "failed"
