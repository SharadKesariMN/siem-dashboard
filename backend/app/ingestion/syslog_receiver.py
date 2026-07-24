import socketserver
import threading

from app.models.database import SessionLocal
from app.ingestion.service import save_raw_syslog_line

SYSLOG_HOST = "0.0.0.0"
SYSLOG_PORT = 5514  # using 5514 instead of 514 (514 needs root privileges)


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        source_ip = self.client_address[0]

        try:
            raw_line = data.decode("utf-8", errors="replace")
        except Exception:
            raw_line = str(data)

        db = SessionLocal()
        try:
            save_raw_syslog_line(db, raw_line, source_ip)
        finally:
            db.close()


def start_syslog_server():
    server = socketserver.UDPServer((SYSLOG_HOST, SYSLOG_PORT), SyslogUDPHandler)
    print(f"Syslog UDP receiver listening on {SYSLOG_HOST}:{SYSLOG_PORT}")
    server.serve_forever()


def start_syslog_thread():
    thread = threading.Thread(target=start_syslog_server, daemon=True)
    thread.start()