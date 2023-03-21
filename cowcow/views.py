from django.http import JsonResponse
from django.views import View
import requests
import json
from django.conf import settings

def get_image_url(name):
    index = name[name.find("#") + 1:]

    return f'https://coffee-dear-mongoose-513.mypinata.cloud/ipfs/QmP8XL56WtNnRvWUXHh1W8MLAjekMyY5JtMw5FC72Lf3bK/{index}.png'

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
    elif hat == 'Golf Polo':
        daos.append('golf')
    
    if hat == 'Milk Bottle':
        daos.append('milk bottle')
    elif hat == 'Sombrero':
        daos.append('sombrero')
    elif hat == 'Clown Hat':
        daos.append('joker')
    
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