"""HTTPS com validação do sistema operacional para ANA e ONS."""
import ssl
from urllib.request import urlopen

import truststore


def open_official(url, timeout):
    # No Windows, usa a CryptoAPI e as raízes instaladas pela organização.
    # O contexto é exclusivo desta consulta e mantém a validação do servidor.
    context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    return urlopen(url, timeout=timeout, context=context)
