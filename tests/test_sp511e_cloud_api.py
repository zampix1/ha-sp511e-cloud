import importlib.util
import pathlib
import sys
import unittest


API_PATH = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "sp511e_cloud" / "api.py"
SPEC = importlib.util.spec_from_file_location("sp511e_cloud_api", API_PATH)
api = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = api
SPEC.loader.exec_module(api)


class SP511ECloudApiTests(unittest.TestCase):
    def test_obfuscation_matches_existing_cloud_client_vector(self):
        value = "deadbeefdeadbeefdeadbeefdeadbeef"

        self.assertEqual(api.deobfuscate(api.obfuscate(value)), value)
        self.assertEqual(api.obfuscate(value), "Pj8WPjO4PQwcPQBcd284P2/4dQ//PQ88Pj8WPjO4PQw=")

    def test_signature_matches_existing_cloud_client_vector(self):
        fields = {
            "message": '{"from":"a","name":"SPLED.Mode","value":200}',
            "hashKey": "abc",
            "ts": 1234567890,
        }

        self.assertEqual(api.sign_form(fields, "t_FAKE_TOKEN_1234567890"), "Pblqa7lBPmYUPQxIGbR9GbJUdbv/Gj//PbNqdblIGDO=")

    def test_color_and_brightness_helpers(self):
        self.assertEqual(api.rgb_to_int((255, 5, 213)), 0xFF05D5)
        self.assertEqual(api.int_to_rgb(0x112233), (0x11, 0x22, 0x33))
        self.assertEqual(api.brightness_ha_to_device(255), 100)
        self.assertEqual(api.brightness_device_to_ha(100), 255)

    def test_effect_whitelist(self):
        self.assertEqual(api.command_for_effect("Rainbow"), ("SPLED.Mode", 200))
        self.assertEqual(api.command_for_effect("pulse"), ("SPLED.Mode", 222))
        with self.assertRaises(ValueError):
            api.command_for_effect("unknown")


if __name__ == "__main__":
    unittest.main()
