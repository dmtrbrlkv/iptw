from unittest import TestCase, expectedFailure
from ip2w import get_weather, get_weather_by_geo, get_geo, load_config, create_session


class FunctionalTest(TestCase):
    @classmethod
    def setUpClass(cls):
        config = load_config()
        cls.ipinfo_token = config["ipinfo_token"]
        cls.ipinfo_url = config["ipinfo_url"]
        cls.owm_url = config["owm_url"]
        cls.owm_appid = config["owm_appid"]
        cls.timeout = config["timeout"]
        cls.session = create_session(config["retry"])

        cls.good_ip = ["8.8.8.8", "1.1.1.1", "95.84.198.44"]
        cls.bad_ip = ["8.8", "8.8.8.8.8", "", "127.0.0.1", "localhost", "255.255.255.255", "-8.8.8.8"]
        cls.good_geo = [("12.34", "56.78"), ("-12", "34"), ("-90", "-180"), ("90", "180")]
        cls.bad_geo = [("-91", "10"), ("91", "10"), ("10", "181"), ("10", "-181"),]

    def test_get_geo_good_ip(self):
        for ip in self.good_ip:
            with self.subTest(ip=ip):
                lat, lon, city = get_geo(ip, self.ipinfo_url, self.ipinfo_token, self.timeout, self.session)
                self.assertNotEqual(lon, "")
                self.assertNotEqual(lat, "")
                self.assertNotEqual(city, "")

    def test_get_geo_bad_ip(self):
        for ip in self.bad_ip:
            with self.subTest(ip=ip):
                with self.assertRaises(Exception):
                    get_geo(ip, self.ipinfo_url, self.ipinfo_token, self.timeout, self.session)

    def test_get_weather_by_geo_good_geo(self):
        for lat, lon in self.good_geo:
            with self.subTest(lat=lat, lon=lon):
                temp, conditions = get_weather_by_geo(lat, lon, self.owm_url, self.owm_appid, self.timeout, self.session)
                self.assertIsInstance(temp, (float, int))
                self.assertNotEqual(conditions, "")

    def test_get_weather_by_geo_bad_geo(self):
        for lat, lon in self.bad_geo:
            with self.subTest(lat=lat, lon=lon):
                with self.assertRaises(Exception):
                    get_weather_by_geo(lat, lon, self.owm_url, self.owm_appid, self.timeout, self.session)

    def test_get_weather_good_ip(self):
        for ip in self.good_ip:
            with self.subTest(ip=ip):
                weather = get_weather(ip, self.ipinfo_url, self.ipinfo_token, self.owm_url, self.owm_appid, self.timeout, self.session)
                self.assertIsInstance(weather, dict)
                self.assertIn("city", weather)
                self.assertIn("temp", weather)
                self.assertIn("conditions", weather)
                self.assertNotEqual(weather["city"], "")
                self.assertNotEqual(weather["temp"], "")
                self.assertNotEqual(weather["conditions"], "")

    def test_get_weather_bad_ip(self):
        for ip in self.bad_ip:
            with self.subTest(ip=ip):
                with self.assertRaises(Exception):
                    get_weather(ip, self.ipinfo_url, self.ipinfo_token, self.owm_url, self.owm_appid, self.timeout, self.session)


