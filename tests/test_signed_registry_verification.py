import argparse
import base64
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("muc_build_registry_signed_tests", ROOT / "tools" / "build_registry.py")
signer = load_module(
    "muc_build_and_sign_signed_tests",
    ROOT / "tools" / "build_and_sign_registry.py",
)


@unittest.skipUnless(shutil.which("openssl"), "OpenSSL is required")
class SignedRegistryVerificationTests(unittest.TestCase):
    KEY_ID = "muc-registry-test-only"

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.private_key = self.root / "private.pem"
        self.public_key = self.root / "public.pem"
        self.fingerprint = self.root / "public.sha256"
        self.unsigned = self.root / "unsigned.json"
        self.signed = self.root / "signed.json"

        signer.run_openssl(
            [
                "genpkey",
                "-algorithm",
                "RSA",
                "-pkeyopt",
                "rsa_keygen_bits:2048",
                "-out",
                str(self.private_key),
            ]
        )
        signer.run_openssl(
            [
                "pkey",
                "-in",
                str(self.private_key),
                "-pubout",
                "-out",
                str(self.public_key),
            ]
        )
        self.fingerprint.write_text(
            signer.public_key_fingerprint(self.public_key) + "\n",
            encoding="ascii",
        )

        builder.write_registry(self.unsigned, [])
        signer.sign_registry(
            argparse.Namespace(
                source=str(self.unsigned),
                private_key=str(self.private_key),
                public_key=str(self.public_key),
                fingerprint=str(self.fingerprint),
                output=str(self.signed),
                key_id=self.KEY_ID,
            )
        )

    def tearDown(self):
        self.temporary.cleanup()

    def verify(self, source=None, public_key=None, fingerprint=None, key_id=None):
        signer.verify_signed(
            argparse.Namespace(
                source=str(source or self.signed),
                public_key=str(public_key or self.public_key),
                fingerprint=str(fingerprint or self.fingerprint),
                key_id=key_id or self.KEY_ID,
            )
        )

    def load_envelope(self):
        return json.loads(self.signed.read_text(encoding="utf-8"))

    def write_envelope(self, envelope, name):
        path = self.root / name
        path.write_text(
            json.dumps(envelope, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return path

    def test_valid_signed_registry_is_accepted(self):
        self.verify()

    def test_untrusted_key_id_is_rejected(self):
        with self.assertRaises(signer.RegistryBuildError):
            self.verify(key_id="another-key")

    def test_modified_valid_payload_is_rejected(self):
        envelope = self.load_envelope()
        payload = json.loads(base64.b64decode(envelope["payload"]).decode("utf-8"))
        payload["generated_at"] = "2026-01-01T00:00:00Z"
        canonical = signer.canonical_payload(payload)
        envelope["payload"] = base64.b64encode(canonical).decode("ascii")
        altered = self.write_envelope(envelope, "altered-payload.json")
        with self.assertRaises(signer.RegistryBuildError):
            self.verify(source=altered)

    def test_modified_signature_is_rejected(self):
        envelope = self.load_envelope()
        signature = bytearray(base64.b64decode(envelope["signature"]))
        signature[len(signature) // 2] ^= 1
        envelope["signature"] = base64.b64encode(bytes(signature)).decode("ascii")
        altered = self.write_envelope(envelope, "altered-signature.json")
        with self.assertRaises(signer.RegistryBuildError):
            self.verify(source=altered)

    def test_noncanonical_payload_bytes_are_rejected(self):
        envelope = self.load_envelope()
        payload = json.loads(base64.b64decode(envelope["payload"]).decode("utf-8"))
        noncanonical = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
        envelope["payload"] = base64.b64encode(noncanonical).decode("ascii")
        altered = self.write_envelope(envelope, "noncanonical-payload.json")
        with self.assertRaises(signer.RegistryBuildError):
            self.verify(source=altered)

    def test_noncanonical_base64_is_rejected(self):
        envelope = self.load_envelope()
        envelope["payload"] = envelope["payload"] + "="
        altered = self.write_envelope(envelope, "noncanonical-base64.json")
        with self.assertRaises(signer.RegistryBuildError):
            self.verify(source=altered)


if __name__ == "__main__":
    unittest.main()
