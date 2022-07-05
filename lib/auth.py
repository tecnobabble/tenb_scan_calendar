from tenable.io import TenableIO
from tenable.sc import TenableSC

# Login to Tenable.sc
def tsc_login(sc_address, sc_access_key, sc_secret_key, sc_port):
    try:
        sc = TenableSC(sc_address, port=sc_port, access_key=sc_access_key, secret_key=sc_secret_key, backoff=5.0, timeout=10)
    except (NameError, TimeoutError) as err:
        print("Please verify connection details.")
        exit()
    except (ConnectionError) as err:
        raise SystemExit(err)
    return sc