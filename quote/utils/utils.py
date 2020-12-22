import os
from configparser import ConfigParser

def read_api_token_from_config():
    config = ConfigParser()
    config.read('token.ini')
    token = config['TOKENS']['API_TOKEN']
    if token is None:
        raise Exception('Cannot read API_TOKEN from ini file')
    else:
        print(f'token: {token}')
        return token

def read_api_token_from_env():
    token = os.getenv('API_TOKEN')
    if token is None:
        raise Exception('Cannot read API_TOKEN from env')
    else:
        print(f'token: {token}')
        return token

def get_api_token():

    try:
        return get_api_token.token
    except AttributeError:

        print('first time try to get api token ...')

        try:
            get_api_token.token = read_api_token_from_config()
            return get_api_token.token
        except Exception as e:
            print(e)

        try:
            get_api_token.token = read_api_token_from_env()
            return get_api_token.token
        except Exception as e:
            print(e)

        raise Exception('API_TOKEN not found')
