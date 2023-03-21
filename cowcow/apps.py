from django.apps import AppConfig


class CowcowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cowcow'

    def ready(self):
        from django.conf import settings
        import requests
        import json

        collection_dict = {}

        payload={}
        headers = {}

        url = "https://api.multiversx.com/collections/COW-cd463d/nfts?size=10000"
        response = requests.request("GET", url, headers=headers, data=payload)
        temp_dict = json.loads(response.text)

        for nft in temp_dict:
            collection_dict[nft['identifier']] = nft
        
        setattr(settings, 'MY_DICT', collection_dict)

        print('GATA')