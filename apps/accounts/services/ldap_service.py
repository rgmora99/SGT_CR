from ldap3 import Server, Connection, Tls, ALL
import ssl

LDAP_SERVER = "ldaps://10.0.0.20"
LDAP_PORT = 636
LDAP_DOMAIN = "netcor.correos.go.cr"
LDAP_BASE_DN = "DC=netcor,DC=correos,DC=go,DC=cr"

LDAP_BIND_USER = "admin_cd@netcor.correos.go.cr"
LDAP_BIND_PASSWORD = "Correos2025$$."

def authenticate_ldap(username: str, password: str) -> dict | None:
    """
    Autentica contra Active Directory.
    Retorna datos del usuario o None.
    """

    tls = Tls(validate=ssl.CERT_NONE)

    server = Server(
        LDAP_SERVER,
        port=LDAP_PORT,
        use_ssl=True,
        get_info=ALL,
        tls=tls
    )

    # 1️⃣ Bind técnico
    with Connection(
        server,
        user=LDAP_BIND_USER,
        password=LDAP_BIND_PASSWORD,
        auto_bind=True
    ) as conn:

        # 2️⃣ Buscar usuario
        search_filter = f"(sAMAccountName={username})"
        conn.search(
            search_base=LDAP_BASE_DN,
            search_filter=search_filter,
            attributes=["cn", "mail", "givenName", "sn"]
        )

        if not conn.entries:
            return None

        user_dn = conn.entries[0].entry_dn

    # 3️⃣ Intentar login del usuario
    try:
        with Connection(
            server,
            user=user_dn,
            password=password,
            auto_bind=True
        ):
            entry = conn.entries[0]
            return {
                "username": username,
                "first_name": entry.givenName.value,
                "last_name": entry.sn.value,
                "email": entry.mail.value,
            }
    except Exception:
        return None
