#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rsactftool.attacks.abstract_attack import AbstractAttack
import subprocess
from rsactftool.lib.crypto_wrapper import RSA
from rsactftool.lib.keys_wrapper import PrivateKey
from rsactftool.lib.utils import rootpath


class Attack(AbstractAttack):
    def __init__(self, timeout=60):
        super().__init__(timeout)
        self.speed = AbstractAttack.speed_enum["medium"]
        self.required_binaries = ["sage"]

    def attack(self, publickey, cipher=[], progress=True):
        """
        Use sage's internal quadratic sieve method.
        If input is less than 40 digits, i'll fallback to sage factor method.
        """
        try:
            sageresult = (
                subprocess.check_output(
                    [
                        "sage",
                        "%s/sage/qs.sage" % rootpath,
                        str(publickey.n),
                    ],
                    timeout=self.timeout,
                    stderr=subprocess.DEVNULL,
                )
                .decode("utf8")
                .rstrip()
            )
            sageresult = sageresult.split("\n")
            if len(sageresult) > 0:
                for line in sageresult:
                    # print(line)
                    if not line.rstrip().find("// ** ") == 0:
                        p, q = line.split(" ")
                        p, q = int(p), int(q)
                        publickey.p, publickey.q = p, q
                        privatekey = PrivateKey(
                            p=int(publickey.p),
                            q=int(publickey.q),
                            e=int(publickey.e),
                            n=int(publickey.n),
                        )
            return (privatekey, None)

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return (None, None)

    def test(self):
        from rsactftool.lib.keys_wrapper import PublicKey

        key_data = """-----BEGIN PUBLIC KEY-----
MCwwDQYJKoZIhvcNAQEBBQADGwAwGAIRAvBQ/pOJQ63t/HNvO76IB8UCAwEAAQ==
-----END PUBLIC KEY-----"""
        result = self.attack(PublicKey(key_data), progress=False)
        return result != (None, None)
