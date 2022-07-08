from tenable.io import TenableIO
from tenable.sc import TenableSC
from tenable.nessus import Nessus

# Login to Tenable.sc
def tsc_login(sc_address, sc_access_key, sc_secret_key, sc_port):
    try:
        sc = TenableSC(sc_address, port=sc_port, access_key=sc_access_key, secret_key=sc_secret_key, backoff=5.0, timeout=10, vendor='Seth Matheson', product='Tenb Scan Calendar', build='v0.1')
    except (NameError, TimeoutError) as err:
        print("Please verify connection details.")
        exit()
    except (ConnectionError) as err:
        raise SystemExit(err)
    return sc

# Login to Tenable.io
def tio_login(io_address, io_access_key, io_secret_key):
    try:
        io = TenableIO(access_key=io_access_key, secret_key=io_secret_key, url=io_address, backoff=5.0, timeout=10, vendor='Seth Matheson', product='Tenb Scan Calendar', build='v0.1')
    except (NameError, TimeoutError) as err:
        print("Please verify connection details.")
        exit()
    except (ConnectionError) as err:
        raise SystemExit(err)
    return io

def nessus_login(nessus_address, nessus_access_key, nessus_secret_key):
    try:
        nessus = Nessus(access_key=nessus_access_key, secret_key=nessus_secret_key, url=nessus_address, backoff=5.0, timeout=10, vendor='Seth Matheson', product='Tenb Scan Calendar', build='v0.1')
    except (NameError, TimeoutError) as err:
        print("Please verify connection details.")
        exit()
    except (ConnectionError) as err:
        raise SystemExit(err)
    return nessus