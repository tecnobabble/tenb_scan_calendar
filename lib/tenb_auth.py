"""Authenticate to Tenable products, Nessus, Tenable.io and Tenable.sc."""

from tenable.io import TenableIO
from tenable.sc import TenableSC
from tenable.nessus import Nessus
import logging


# Login to Tenable.sc
def tsc_login(sc_address: str, sc_access_key: str, sc_secret_key: str, 
              sc_port: int):
    """
    Return an authenticated pyTenable Tenable.sc object.

        Parameters:
                sc_address (str): URL of Tenable.sc server
                sc_access_key (str): Access key for Tenable.sc org user
                sc_secret_key (str): Secret key for Tenable.sc org user
                sc_port (int): Port that Tenable.sc is running on

        Returns:
                sc (object): Authenticated pyTenable Tenable.sc object
    """
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
def tio_login(io_address: str, io_access_key: str, io_secret_key: str):
    """
    Return an authenticated pyTenable Tenable.io object.

        Parameters:
                io_address (str): URL of Tenable.io instance
                io_access_key (str): Access key for Tenable.io user
                io_secret_key (str): Secret key for Tenable.io user

        Returns:
                io (object): Authenticated pyTenable Tenable.io object
    """
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


def nessus_login(nessus_address: str, nessus_access_key: str, 
                 nessus_secret_key: str, nessus_port: int):
    """
    Return an authenticated pyTenable Nessus object.

        Parameters:
                nessus_address (str): URL of Tenable Nessus server
                nessus_access_key (str): Access key for Nessus user
                nessus_secret_key (str): Secret key for Nessus user
                nessus_port (int): Port that Nessus is running on

        Returns:
                nessus (object): Authenticated pyTenable Nessus object
    """
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
