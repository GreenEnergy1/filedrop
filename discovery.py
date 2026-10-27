"""mDNS/DNS-SD advertisement for the Filedrop web server."""

import logging
import re
import socket

from zeroconf import IPVersion, ServiceInfo, Zeroconf

from config import Config

logger = logging.getLogger(__name__)
SERVICE_TYPE = "_filedrop._tcp.local."


def _host_addresses():
    addresses = set()
    try:
        for result in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            address = result[4][0]
            if not address.startswith(("127.", "169.254.")):
                addresses.add(address)
    except OSError:
        pass

    # Hostname resolution can omit the active LAN address on some systems.
    if not addresses:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe.connect(("224.0.0.251", 5353))
            address = probe.getsockname()[0]
            if not address.startswith("127."):
                addresses.add(address)
        except OSError:
            pass
        finally:
            probe.close()
    return sorted(addresses)


class ServiceAdvertisement:
    def __init__(self):
        self.zeroconf = None
        self.info = None

    def start(self):
        addresses = _host_addresses()
        if not addresses:
            logger.warning("Could not determine a LAN address; Filedrop discovery is unavailable")
            return

        hostname = socket.gethostname()
        friendly_name = Config.SERVICE_NAME or f"Filedrop - {hostname}"
        # DNS-SD instance labels are limited to 63 bytes. Add part of the
        # persistent ID so duplicate friendly names remain distinguishable.
        label = re.sub(r"[^A-Za-z0-9 _-]", "-", friendly_name).strip() or "Filedrop"
        suffix = Config.SERVER_ID.replace("-", "")[:8]
        label = f"{label[:45].rstrip()} ({suffix})"
        safe_hostname = re.sub(r"[^A-Za-z0-9-]", "-", hostname).strip("-") or "filedrop"

        self.info = ServiceInfo(
            SERVICE_TYPE,
            f"{label}.{SERVICE_TYPE}",
            addresses=addresses,
            port=Config.PORT,
            properties={
                "id": Config.SERVER_ID,
                "name": friendly_name,
                "path": "/",
            },
            server=f"{safe_hostname}.local.",
        )
        self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        try:
            self.zeroconf.register_service(self.info, allow_name_change=True)
            logger.info("Advertising %s on port %s via mDNS", friendly_name, Config.PORT)
        except Exception:
            logger.exception("Could not advertise Filedrop over mDNS")
            self.close()

    def close(self):
        if self.zeroconf is None:
            return
        try:
            if self.info is not None:
                self.zeroconf.unregister_service(self.info)
        except Exception:
            logger.debug("Could not withdraw mDNS service cleanly", exc_info=True)
        finally:
            self.zeroconf.close()
            self.zeroconf = None
