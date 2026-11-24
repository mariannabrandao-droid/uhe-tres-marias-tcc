"""HTTPS com validação de certificados, sem injeção global de SSL."""
import ssl
from urllib.request import urlopen

def open_official(url, timeout):
    context = ssl.create_default_context()
    return urlopen(url, timeout=timeout, context=context)
