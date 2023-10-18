#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rsactftool.attacks.abstract_attack import AbstractAttack
from tqdm import tqdm
from rsactftool.lib.keys_wrapper import PrivateKey
from rsactftool.lib.number_theory import is_divisible
from rsactftool.lib.pickling import *
import glob


class Attack(AbstractAttack):
    def __init__(self, timeout=60):
        super().__init__(timeout)
        self.speed = AbstractAttack.speed_enum["fast"]

    def attack(self, publickey, cipher=[], progress=True):
        """Search for rapid7 gcd primes"""
        for txtfile in glob.glob("data/*.pkl.bz2"):
            self.logger.info("[+] loading prime list file %s..." % txtfile)
            # primes = sorted([int(l.rstrip()) for l in open(txtfile,"r").readlines()])
            primes = decompress_pickle(txtfile)
            for prime in tqdm(primes, disable=(not progress)):
                if is_divisible(publickey.n, prime):
                    publickey.q = prime
                    publickey.p = publickey.n // publickey.q
                    priv_key = PrivateKey(
                        int(publickey.p),
                        int(publickey.q),
                        int(publickey.e),
                        int(publickey.n),
                    )
                    return priv_key, None
        return None, None

    def test(self):
        from rsactftool.lib.keys_wrapper import PublicKey

        key_data = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDEUCMPvSGioBgCAD3j1ZTNOiHQ
wu4Kv8DSTBm2NgwZGQD0hjoQR7HQz5VtVoYnomtcM9Nv4RmG0eSyiH6RQ2jRSBRv
ENq6t4qAHJYpCkRKVvoILiXklsfAFMMjd+u3qDQoEinztzMydkdGOTe/HafCnD6r
1FV+zN3cw0ykBw2C9wIDAQAB
-----END PUBLIC KEY-----"""
        result = self.attack(PublicKey(key_data), progress=False)
        return result != (None, None)
