from django.http import JsonResponse
from django.views import View
import requests
import json
from django.conf import settings
import datetime


def get_image_url(name):
    index = name[name.find("#") + 1:]

    return f'https://coffee-dear-mongoose-513.mypinata.cloud/ipfs/QmP8XL56WtNnRvWUXHh1W8MLAjekMyY5JtMw5FC72Lf3bK/{index}.png'

def int_to_hex(number):
    hex_nr = hex(number)[2:]
    if len(hex_nr) % 2 != 0:
        hex_nr = "0" + hex_nr
    return hex_nr

def get_daos(metadata):
    clothes = ''
    eyewear = ''
    hat = ''
    fur = ''
    eyes = ''
    mouth = ''

    daos = []

    for trait in metadata['attributes']:
        if trait['trait_type'] == 'Clothes':
            clothes = trait['value']
        elif trait['trait_type'] == 'Hat':
            hat = trait['value']
        elif trait['trait_type'] == 'Mouth':
            mouth = trait['value']
        elif trait['trait_type'] == 'Eyewear':
            eyewear = trait['value']
        elif trait['trait_type'] == 'Fur':
            fur = trait['value']
        else:
            eyes = trait['value']
    
    if clothes == 'Space Suit':
        daos.append('space')
    elif clothes == 'Golf Polo':
        daos.append('golf')
    elif clothes == 'Waiter Suit' or clothes == 'Chef Tunic':
        daos.append('tavern')
    elif clothes == 'Rockstar Jacket':
        daos.append('rockstar')

    if hat == 'Milk Bottle':
        daos.append('milk_bottle')
    elif hat == 'Sombrero':
        daos.append('sombrero')
    elif hat == 'Clown Hat':
        daos.append('joker')
    elif hat == '23 Ear Tag':
        daos.append('23')
    
    if fur == 'Robot' or fur == 'Manifesto' or fur == 'Gold':
        daos.append('triumvirate')
    
    if eyewear == 'Aviator Sunglasses' or clothes == 'Aviator Jacket':
        daos.append('aviator')
    
    if clothes == 'None' and eyewear == 'None' and hat == 'None':
        daos.append('naked')

    return daos

def add_nfts_from_wallet(address):
    url = f"https://api.multiversx.com/accounts/{address}/nfts/count?collection=COW-cd463d"
    payload={}
    headers = {}

    size = requests.request("GET", url, headers=headers, data=payload).text

    url = f"https://api.multiversx.com/accounts/{address}/nfts?collection=COW-cd463d&from=0&size={size}"
    response = requests.request("GET", url, headers=headers, data=payload)
    response = json.loads(response.text)

    for nft in response:
        nft['staked'] = 'no'
        nft['daos'] = get_daos(nft['metadata'])
    
    return response

'''
def add_staked_nfts(address):
    collection_dict = settings.MY_DICT
    temp_list = []

    url = f"https://api.xoxno.com/getUserPoolInfo/{address}/92"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response = json.loads(response.text)

    stakedIdentifiers = response['stakedIdentifiers']
    for value in stakedIdentifiers:
        temp_value = collection_dict[value]
        temp_value['staked'] = 'yes'
        temp_value['daos'] = get_daos(temp_value['metadata'])
        temp_list.append(temp_value)

    unboundIdentifiers = response['unboundInfo']['unboundIdentifiers']
    for value in unboundIdentifiers:
        temp_value = collection_dict[value]
        temp_value['staked'] = 'yes'
        temp_value['daos'] = get_daos(temp_value['metadata'])
        temp_list.append(temp_value)

    return temp_list
'''

def add_staked_nfts(address):
    collection_dict = settings.MY_DICT
    temp_list = []

    url = f"https://cowcow-api.vercel.app/staking-data/{address}"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response = json.loads(response.text)

    stakedIdentifiers = response['staked_nfts']
    for value in stakedIdentifiers:
        temp_value = collection_dict[f"COW-cd463d-{int_to_hex(int(value))}"]
        temp_value['staked'] = 'yes'
        temp_value['daos'] = get_daos(temp_value['metadata'])
        temp_list.append(temp_value)
    
    unboundIdentifiers = response['unstaked_nfts']
    for value in unboundIdentifiers:
        temp_value = collection_dict[f"COW-cd463d-{int_to_hex(int(value))}"]
        temp_value['staked'] = 'yes'
        temp_value['daos'] = get_daos(temp_value['metadata'])
        temp_list.append(temp_value)
    
    return temp_list
        
class MyListView(View):
    def get(self, request, address):
        wallet_nfts = add_nfts_from_wallet(address)
        staked_nfts = add_staked_nfts(address)

        nft_list = wallet_nfts + staked_nfts

        from_param = int(request.GET.get('from', 0))
        size_param = int(request.GET.get('size', len(nft_list)))

        if from_param >= size_param:
            return JsonResponse({'error': 'from must be smaller than size'}, status=400)
        
        filtered_list = nft_list[from_param:size_param]
        response_data = {'data': filtered_list}
        return JsonResponse(response_data)

class ListSizeView(View):
    def get(self, request, address):
        wallet_nfts = add_nfts_from_wallet(address)
        staked_nfts = add_staked_nfts(address)

        nft_list = wallet_nfts + staked_nfts

        response_data = {'size': len(nft_list)}
        return JsonResponse(response_data)
    
class UnbondView(View):
    def get(self, request):
        global_dict = {}

        url = "https://api.multiversx.com/accounts/erd1qqqqqqqqqqqqqpgqqgzzsl0re9e3u0t3mhv3jwg6zu63zssd7yqs3uu9jk/transactions?function=unstake&size=10000&order=asc"

        payload = {}
        headers = {
        'Cookie': '__cflb=02DiuJNkBBX5Wn6Z6yZNTBmZLC2j5TpzLaVwHUct2FcSG'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        my_json = json.loads(response.text)

        for el in my_json:
            dt = datetime.datetime.fromtimestamp(el['timestamp']) + datetime.timedelta(days=7)
            month = dt.strftime("%B")
            current_date = f"{dt.day}-{month}"

            if current_date not in global_dict:
                global_dict[current_date] = [el['sender']]
            else:
                global_dict[current_date].append(el['sender'])
        
        final_dict = {}
        
        for key in global_dict:
            final_dict[key] = len(global_dict[key])

        return JsonResponse(final_dict)