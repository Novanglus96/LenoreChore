"""
Module: generate_vapid_keys.py
Description: Generate a VAPID key pair for Web Push notifications, formatted
    for the VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY environment variables.
"""

import base64

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate a VAPID key pair for Web Push notifications."

    def handle(self, *args, **options):
        from py_vapid import Vapid01
        from cryptography.hazmat.primitives import serialization

        vapid = Vapid01()
        vapid.generate_keys()

        public_key = (
            base64.urlsafe_b64encode(
                vapid.public_key.public_bytes(
                    serialization.Encoding.X962,
                    serialization.PublicFormat.UncompressedPoint,
                )
            )
            .rstrip(b"=")
            .decode()
        )
        private_key = (
            base64.urlsafe_b64encode(
                vapid.private_key.private_numbers().private_value.to_bytes(
                    32, "big"
                )
            )
            .rstrip(b"=")
            .decode()
        )

        self.stdout.write(
            "Add these to your .env (keep the private key secret):\n"
        )
        self.stdout.write(f"VAPID_PUBLIC_KEY={public_key}")
        self.stdout.write(f"VAPID_PRIVATE_KEY={private_key}")
        self.stdout.write("VAPID_SUBJECT=mailto:you@example.com")
