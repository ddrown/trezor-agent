"""Solo-related code."""

import hashlib
import os
import logging
from struct import pack

import solo
import solo.fido2
from fido2.ctap import CtapError

from . import interface
from .. import formats

log = logging.getLogger(__name__)


class Solo(interface.Device):
    """Connection to Solo device."""

    # singleton connection
    cached_connection = None

    @classmethod
    def package_name(cls):
        """Python package name (at PyPI)."""
        return 'solo-agent'

    def _verify_curve_support(self, identity):
        """Make sure the device supports given configuration."""
        if identity.curve_name not in {formats.CURVE_NIST256}:
            raise NotImplementedError(
                'Unsupported elliptic curve: {}'.format(identity.curve_name))

    def _find_device(self):
        """Selects a hardware key based on `SOLO_SERIAL`/`SOLO_UDP` environment variables.

        If unset, picks first connected device.
        """
        if Solo.cached_connection != None:
            return Solo.cached_connection

        try:
            serial = os.environ.get("SOLO_SERIAL")
            udp = os.environ.get("SOLO_UDP")
            log.debug(f"connecting with serial: {serial} udp: {udp}")
            client = solo.client.find(serial, udp=udp)
            Solo.cached_connection = client
            return client
        except Exception as e:  # pylint: disable=broad-except
            log.error(f"Failed to find a Solo device: {e}")

    def _verify_version(self, connection):
        required_extension = 'solo-ssh-agent'
        info = connection.get_info()
        log.debug('connected to %s: %s', self, info)
        if required_extension not in info.extensions:
            err = f'Please upgrade your firmware to a version that supports the {required_extension} extension'
            raise ValueError(err)

    def connect(self):
        """Enumerate and connect to the first available interface."""
        connection = self._find_device()
        if not connection:
            raise interface.NotFoundError('{} not connected'.format(self))

        log.debug('using connection: %s', connection)
        self._verify_version(connection)
        return connection

    def close(self):
        """Close connection."""
        self.conn = None

    def pubkey(self, identity, ecdh=False):
        """Return public key."""
        self._verify_curve_support(identity)
        curve_name = identity.get_curve_name(ecdh=ecdh)
        log.debug('"%s" getting public key (%s) from %s',
                  identity.to_string(), curve_name, self)
        result = self.conn.ssh_agent(pack("B", 11))
        status = result[0]
        public_key = result[1:]
        if status != CtapError.ERR.SUCCESS:
            raise CtapError(status)
        return public_key

    def sign(self, identity, blob):
        """Sign given blob and return the signature (as bytes)."""
        log.debug("sign requested")
        if identity.identity_dict['proto'] in {'ssh'}:
            digest = hashlib.sha256(blob).digest()
        else:
            digest = blob
        signcmd = pack("B", 13)
        result = self.conn.ssh_agent(signcmd + digest)
        status = result[0]
        signature = result[1:]
        if status != CtapError.ERR.SUCCESS:
            log.error(f"sign status: {status}")
            raise CtapError(status)
        return signature
