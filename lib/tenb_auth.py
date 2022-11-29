from tenable.io import TenableIO
from tenable.sc import TenableSC
from tenable.nessus import Nessus
import logging


# Login to Tenable.sc
def tsc_login(sc_address, sc_access_key, sc_secret_key, sc_port):
    try:
        sc = TenableSC(sc_address, port=sc_port, access_key=sc_access_key,
                       secret_key=sc_secret_key, backoff=5.0, timeout=10,
                       retries=3, vendor='github.com/tecnobabble',
                       product='Tenb Scan Calendar')
        sc.current.user()
    except (NameError, TimeoutError, ConnectionError) as err:
        logging.debug(f"{type(err).__name__} was raised: {err}")
        logging.info("Please verify Tenable.sc connection details.")
        exit()
    except Exception as err:
        logging.debug(f"{type(err).__name__} was raised: {err}")
        logging.info("Please verify Tenable.sc API Keys and network details.")
        exit()
    return sc


# Login to Tenable.io
def tio_login(io_address, io_access_key, io_secret_key):
    try:
        io = TenableIO(access_key=io_access_key, secret_key=io_secret_key,
                       url=io_address, backoff=5.0, timeout=10, retries=3,
                       vendor='github.com/tecnobabble',
                       product='Tenb Scan Calendar')
        io.server.status()
    except (NameError, TimeoutError, ConnectionError) as err:
        logging.debug(f"{type(err).__name__} was raised: {err}")
        logging.info("Please verify Tenable.io connection details.")
        exit()
    except Exception as err:
        logging.debug(f"{type(err).__name__} was raised: {err}")
        logging.info("Please verify Tenable.io API Keys and network details.")
        exit()
    return io


def nessus_login(nessus_address, nessus_access_key, nessus_secret_key):
    try:
        nessus = Nessus(access_key=nessus_access_key,
                        secret_key=nessus_secret_key, url=nessus_address,
                        backoff=5.0, timeout=10, retries=3,
                        vendor='github.com/tecnobabble',
                        product='Tenb Scan Calendar')
        nessus.server.status()
    except (NameError, TimeoutError, ConnectionError) as err:
        logging.debug(f"{type(err).__name__} was raised: {err}")
        logging.info("Please verify Nessus connection details.")
        exit()
    except Exception as err:
        logging.debug(f"{type(err).__name__} was raised: {err}")
        logging.info("Please verify Nessus API Keys and network details.")
        exit()
    return nessus
