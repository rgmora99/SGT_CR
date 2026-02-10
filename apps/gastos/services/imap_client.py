import imaplib
from datetime import date

class IMAPClient:
    def __init__(self, host: str, port: int, use_ssl: bool):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.conn = None

    def connect(self, username: str, password: str):
        if self.use_ssl:
            self.conn = imaplib.IMAP4_SSL(self.host, self.port)
        else:
            self.conn = imaplib.IMAP4(self.host, self.port)

        self.conn.login(username, password)
        return self.conn
    
    def mark_seen(self, msg_id: bytes):
        """
        Marca un correo como leído (SEEN)
        """
        if not self.conn:
            raise RuntimeError("Conexión IMAP no inicializada")

        self.conn.store(msg_id, "+FLAGS", "\\Seen")

    def select_folder(self, folder: str):
        typ, data = self.conn.select(folder)
        if typ != "OK":
            raise RuntimeError(f"No se pudo abrir carpeta IMAP: {folder}")
        return data

    # ✅ NUEVO: buscar por AÑO (solo ese año)
    def search_by_year(self, year: int, subject: str = None, unseen_only: bool = False):
        since = date(year, 1, 1).strftime("%d-%b-%Y")      # 01-Jan-YYYY
        before = date(year + 1, 1, 1).strftime("%d-%b-%Y") # 01-Jan-(YYYY+1)

        parts = []
        if unseen_only:
            parts.append("UNSEEN")

        parts.append(f"SINCE {since}")
        parts.append(f"BEFORE {before}")

        if subject:
            # SUBJECT "factura"
            parts.append(f'SUBJECT "{subject}"')

        query = f'({" ".join(parts)})'

        typ, data = self.conn.search(None, query)
        if typ != "OK":
            return []
        return data[0].split()

    # (tu método original, si lo quieres conservar)
    def search_unseen(self):
        typ, data = self.conn.search(None, '(UNSEEN SUBJECT "factura")')
        if typ != "OK":
            return []
        return data[0].split()

    def fetch_rfc822(self, msg_id: bytes):
        typ, data = self.conn.fetch(msg_id, "(RFC822)")
        if typ != "OK":
            raise RuntimeError("No se pudo leer el correo.")
        return data[0][1]

    def mark_seen(self, msg_id: bytes):
        self.conn.store(msg_id, "+FLAGS", "\\Seen")

    def logout(self):
        try:
            if self.conn:
                self.conn.logout()
        except Exception:
            pass