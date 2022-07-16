"""Tenable Scan Calendar Generator - Primary."""
# !/usr/bin/env python

from tenable.io import TenableIO
from tenable.sc import TenableSC
from tenable.nessus import Nessus


def tsc_login(sc_address: str, sc_access_key: str, sc_secret_key: str,
              sc_port: str) -> TenableSC:
    """Generate authentication object for Tenable.sc.

    Args:
        sc_address (str): IP or hostname of Tenable SC
        sc_access_key (str): TenableSC Org User API Access Key
        sc_secret_key (str): TenableSC Org User API Secret Key
        sc_port (str): Tenable SC TCP Port (default 443)

    Raises:
        SystemExit: Breaks on timeout or connection error

    Returns:
        TenableSC: Authentication object
    """
    try:
        sc = TenableSC(sc_address, port=sc_port, access_key=sc_access_key,
                       secret_key=sc_secret_key, backoff=5.0, timeout=10,
                       vendor='Seth Matheson', product='Tenb Scan Calendar',
                       build='v0.1')
    except (NameError, TimeoutError):
        print("Please verify connection details.")
        exit()
    except (ConnectionError) as err:
        raise SystemExit(err)
    return sc


# Login to Tenable.io
def tio_login(io_address: str, io_access_key: str,
              io_secret_key: str) -> TenableIO:
    """Generate authentication object for Tenable.io.

    Args:
        io_address (str): Tenable.io URL
        io_access_key (str): Tenable.io user API Access Key
        io_secret_key (str): Tenable.io user API Secret Key

    Raises:
        SystemExit: Breaks on timeout or connection error

    Returns:
        TenableIO: Authentication object
    """
    try:
        io = TenableIO(access_key=io_access_key, secret_key=io_secret_key,
                       url=io_address, backoff=5.0, timeout=10,
                       vendor='Seth Matheson', product='Tenb Scan Calendar',
                       build='v0.1')
    except (NameError, TimeoutError):
        print("Please verify connection details.")
        exit()
    except (ConnectionError) as err:
        raise SystemExit(err)
    return io


def nessus_login(nessus_address: str, nessus_access_key: str,
                 nessus_secret_key: str) -> Nessus:
    """Generate authentication object for Nessus.

    Args:
        nessus_address (str): Nessus URL
        nessus_access_key (str): Nessus User API Accss Key
        nessus_secret_key (str): Nessus User API Secret Key

    Raises:
        SystemExit: Breaks on timeout or connection error

    Returns:
        Nessus: Authentication object
    """
    try:
        nessus = Nessus(access_key=nessus_access_key,
                        secret_key=nessus_secret_key, url=nessus_address,
                        backoff=5.0, timeout=10, vendor='Seth Matheson',
                        product='Tenb Scan Calendar', build='v0.1')
    except (NameError, TimeoutError):
        print("Please verify connection details.")
        exit()
    except (ConnectionError) as err:
        raise SystemExit(err)
    return nessus
