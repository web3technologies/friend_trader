import requests
from django.utils.functional import SimpleLazyObject


class KosettoClient:

    KOSSETTO_URL = "https://prod-api.kosetto.com/users"

    def get_kossetto_user(self, address):
        res = requests.get(f"{self.KOSSETTO_URL}/{address}", timeout=3)
        res.raise_for_status()
        kossetto_data = res.json()
        return kossetto_data
    


kossetto_client = SimpleLazyObject(KosettoClient)