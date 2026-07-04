"""Vendor cloud API client for SP511E controllers.

This module intentionally contains no Home Assistant imports so the protocol
helpers can be tested outside HA. Network methods are synchronous and must run
in an executor from Home Assistant.
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


API_BASE = "https://fairyhome.ledhue.com/smarthome/v1/"
STD_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
VENDOR_B64 = "1sC2EFbHvJyLgNdPzkiTpV7XtZaG+MefOhSjRlmnoUqrBYuIwxKQ0AD3/96W85c4"
ENCODE_TRANS = str.maketrans(STD_B64, VENDOR_B64)
DECODE_TRANS = str.maketrans(VENDOR_B64, STD_B64)

EFFECTS: dict[str, dict[str, Any]] = {
    "rainbow": {"mode": 200, "sound_reactive": False},
    "fire": {"mode": 201, "sound_reactive": False},
    "stars": {"mode": 202, "sound_reactive": False},
    "ripple": {"mode": 203, "sound_reactive": False},
    "halloween": {"mode": 204, "sound_reactive": False},
    "theater": {"mode": 205, "sound_reactive": False},
    "gradient": {"mode": 206, "sound_reactive": False},
    "gorgeous": {"mode": 207, "sound_reactive": False},
    "romantic": {"mode": 208, "sound_reactive": False},
    "sunshine": {"mode": 209, "sound_reactive": False},
    "sunset": {"mode": 210, "sound_reactive": False},
    "seaside": {"mode": 211, "sound_reactive": False},
    "grassland": {"mode": 212, "sound_reactive": False},
    "violet": {"mode": 213, "sound_reactive": False},
    "crystal": {"mode": 214, "sound_reactive": False},
    "energy": {"mode": 215, "sound_reactive": False},
    "spectrum": {"mode": 216, "sound_reactive": False},
    "twinkle": {"mode": 217, "sound_reactive": False},
    "beats": {"mode": 218, "sound_reactive": True},
    "scrolling": {"mode": 219, "sound_reactive": False},
    "rhythm": {"mode": 220, "sound_reactive": True},
    "blink": {"mode": 221, "sound_reactive": False},
    "pulse": {"mode": 222, "sound_reactive": True},
    "ejection": {"mode": 223, "sound_reactive": False},
}

MODE_TO_EFFECT = {int(meta["mode"]): name for name, meta in EFFECTS.items()}


class SP511ECloudError(Exception):
    """Base API error."""


class SP511ECloudAuthError(SP511ECloudError):
    """Session is missing, expired, or rejected."""


@dataclass(slots=True)
class Session:
    """Signed SP511E cloud session."""

    sid: str
    token: str


@dataclass(slots=True)
class DeviceSnapshot:
    """Current device snapshot derived from user/info and optimistic writes."""

    device: dict[str, Any]
    state: dict[str, Any]


def custom_b64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii").translate(ENCODE_TRANS)


def custom_b64_decode(text: str) -> bytes:
    return base64.b64decode(text.translate(DECODE_TRANS))


def xor90(data: bytes) -> bytes:
    return bytes(byte ^ 0x5A for byte in data)


def obfuscate(text: str) -> str:
    return custom_b64_encode(xor90(text.encode("utf-8")))


def deobfuscate(text: str) -> str:
    return xor90(custom_b64_decode(text)).decode("utf-8")


def app_md5(text: str) -> str:
    return hashlib.md5((text + "@sperll").encode("utf-8")).hexdigest()


def sign_form(fields: dict[str, Any], token: str) -> str:
    joined = "".join(f"{fields[key]}+" for key in sorted(fields))
    return obfuscate(app_md5(joined + token))


def form_encode(fields: dict[str, Any]) -> bytes:
    return urllib.parse.urlencode(fields, safe="*").encode("utf-8")


def build_message(name: str, value: Any) -> str:
    return json.dumps({"from": "a", "name": name, "value": value}, separators=(",", ":"))


def user_info_fields() -> dict[str, Any]:
    return {
        "sysCode": 35,
        "appVer": 20,
        "appVerName": "1.8.0",
        "screen": "1080*2400",
        "timeZone": "GMT",
        "manufacturer": "Google",
        "system": "android",
        "sysName": 15,
        "model": "sdk_gphone64_x86_64",
        "brand": "google",
        "board": "goldfish_x86_64",
        "channelId": 10001,
    }


def iter_devices(response: dict[str, Any]) -> list[dict[str, Any]]:
    payload = response.get("payload")
    if not isinstance(payload, dict):
        return []
    devices_payload = payload.get("devices")
    if isinstance(devices_payload, dict) and isinstance(devices_payload.get("data"), list):
        return [item for item in devices_payload["data"] if isinstance(item, dict)]
    return []


def pick_device(devices: list[dict[str, Any]], selector: str | None) -> dict[str, Any]:
    if not devices:
        raise SP511ECloudError("No SP511E devices returned by cloud")
    if selector:
        selector_l = selector.lower()
        for device in devices:
            haystack = " ".join(
                str(device.get(key, ""))
                for key in ("name", "ip", "lanIp", "deviceCode", "productKey", "category")
            ).lower()
            if selector_l in haystack:
                return device
    if len(devices) == 1:
        return devices[0]
    for device in devices:
        if str(device.get("name", "")).upper().startswith("SP511E"):
            return device
    return devices[0]


def rgb_to_int(rgb: tuple[int, int, int]) -> int:
    red, green, blue = rgb
    for value in rgb:
        if value < 0 or value > 255:
            raise ValueError("RGB values must be 0..255")
    return (red << 16) | (green << 8) | blue


def int_to_rgb(value: int) -> tuple[int, int, int]:
    value = int(value)
    return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)


def brightness_ha_to_device(brightness: int | None) -> int | None:
    if brightness is None:
        return None
    brightness = max(1, min(255, int(brightness)))
    return max(1, min(100, round(brightness * 100 / 255)))


def brightness_device_to_ha(brightness: int | None) -> int | None:
    if brightness is None:
        return None
    brightness = max(1, min(100, int(brightness)))
    return max(1, min(255, round(brightness * 255 / 100)))


def normalize_effect(effect: str) -> str:
    key = effect.strip().lower()
    if key not in EFFECTS:
        raise ValueError(f"Unknown SP511E effect: {effect}")
    return key


def command_for_effect(effect: str) -> tuple[str, int]:
    key = normalize_effect(effect)
    return "SPLED.Mode", int(EFFECTS[key]["mode"])


def response_auth_failed(response: dict[str, Any]) -> bool:
    code = response.get("code")
    desc = str(response.get("desc", "")).lower()
    return code in {401, 403, 1001, 1002, 2001, 4001} or "auth" in desc or "login" in desc or "token" in desc


class SP511ECloudClient:
    """Synchronous vendor cloud client."""

    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout

    def _get_json(self, path: str) -> dict[str, Any]:
        req = urllib.request.Request(
            urllib.parse.urljoin(API_BASE, path.lstrip("/")),
            method="GET",
            headers={"Accept": "application/json", "User-Agent": "okhttp/3.12.1"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))

    def _post_form_unsigned(self, path: str, fields: dict[str, Any]) -> dict[str, Any]:
        req = urllib.request.Request(
            urllib.parse.urljoin(API_BASE, path.lstrip("/")),
            data=form_encode(fields),
            method="POST",
            headers={
                "Accept": "application/json",
                "Accept-Language": "en",
                "Cache-Control": "no-cache",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "okhttp/3.12.1",
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))

    def post_signed_form(self, path: str, session: Session, fields: dict[str, Any]) -> dict[str, Any]:
        signed_fields = dict(fields)
        signed_fields["ts"] = int(time.time() * 1000)
        req = urllib.request.Request(
            urllib.parse.urljoin(API_BASE, path.lstrip("/")),
            data=form_encode(signed_fields),
            method="POST",
            headers={
                "Accept": "application/json",
                "Accept-Language": "en",
                "Cache-Control": "no-cache",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "okhttp/3.12.1",
                "sp-data-sid": session.sid,
                "sp-data-sn": sign_form(signed_fields, session.token),
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            response = json.loads(resp.read().decode("utf-8", errors="replace"))
        if response_auth_failed(response):
            raise SP511ECloudAuthError(str(response))
        return response

    def login(self, account: str, password: str, country_code: str) -> Session:
        # Import lazily: Home Assistant ships cryptography, while local unit tests
        # for non-login helpers should not require it.
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding, rsa

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
        public_der = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        public_key_b64 = base64.b64encode(public_der).decode("ascii")

        apply_response = self._get_json("sign/apply?version=20")
        if apply_response.get("code") != 200 or not isinstance(apply_response.get("payload"), dict):
            raise SP511ECloudAuthError(f"sign/apply failed: {apply_response!r}")
        server_public_key_b64 = apply_response["payload"].get("pub-k") or apply_response["payload"].get("publicKey")
        if not server_public_key_b64:
            raise SP511ECloudAuthError("sign/apply did not return server public key")
        server_public_key = serialization.load_der_public_key(base64.b64decode(server_public_key_b64))

        def encrypt_to_b64(text: str) -> str:
            encrypted = server_public_key.encrypt(text.encode("utf-8"), padding.PKCS1v15())
            return base64.b64encode(encrypted).decode("ascii")

        sign_in_response = self._post_form_unsigned(
            "sign/sign-in",
            {
                "countryCode": country_code,
                "account": encrypt_to_b64(account),
                "password": encrypt_to_b64(password),
                "pub-k": public_key_b64,
            },
        )
        if sign_in_response.get("code") != 200 or not isinstance(sign_in_response.get("payload"), dict):
            raise SP511ECloudAuthError(f"sign/sign-in failed: {sign_in_response!r}")
        payload = sign_in_response["payload"]

        def decrypt_b64(value: str) -> str:
            raw = base64.b64decode(value)
            chunks = []
            for offset in range(0, len(raw), 128):
                chunks.append(private_key.decrypt(raw[offset : offset + 128], padding.PKCS1v15()))
            return b"".join(chunks).decode("utf-8")

        sid = str(payload.get("sid", "")).strip()
        token_cipher = payload.get("token")
        if not sid or not token_cipher:
            raise SP511ECloudAuthError("login response did not contain sid/token")
        # Keep a small cryptography reference used by some HA frozen builds.
        hashes.SHA256()
        return Session(sid=sid, token=decrypt_b64(str(token_cipher)))

    def get_devices(self, session: Session) -> list[dict[str, Any]]:
        response = self.post_signed_form("user/info", session, user_info_fields())
        if response.get("code") != 200:
            raise SP511ECloudError(f"user/info failed: {response!r}")
        return iter_devices(response)

    def get_snapshot(
        self,
        session: Session,
        selector: str | None,
        previous_state: dict[str, Any] | None = None,
    ) -> DeviceSnapshot:
        device = pick_device(self.get_devices(session), selector)
        state = dict(previous_state or {})
        if "power" in device:
            state["p"] = int(device["power"])
        state.setdefault("bn", 100)
        state.setdefault("c", 0xFF0E9A)
        state.setdefault("m", 200)
        state.setdefault("ms", 100)
        state.setdefault("rgb", 0)
        state.setdefault("s", 57)
        return DeviceSnapshot(device=device, state=state)

    def send_command(self, session: Session, hash_key: str, name: str, value: Any) -> dict[str, Any]:
        fields = {
            "hashKey": obfuscate(hash_key),
            "message": build_message(name, value),
        }
        response = self.post_signed_form("user/device/control", session, fields)
        if response.get("code") != 200:
            raise SP511ECloudError(f"control failed: {response!r}")
        return response
