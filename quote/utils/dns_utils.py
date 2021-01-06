import socket

def get_db_hostname():
    try:
        socket.gethostbyname('db')
        print(f'db hostname = db')
        return 'db'
    except Exception as e:
        #print(f'gethostbyname(\'db\') failed: {e}')
        print(f'db hostname = localhost')
        return 'localhost'

def get_grpc_hostname():
    try:
        socket.gethostbyname('grpc')
        print(f'grpc hostname = grpc')
        return 'grpc'
    except Exception as e:
        #print(f'gethostbyname(\'grpc\') failed: {e}')
        print(f'grpc hostname = localhost')
        return 'localhost'

def get_restapi_hostname():
    try:
        socket.gethostbyname('rest')
        print(f'restapi hostname = rest')
        return 'rest'
    except Exception as e:
        #print(f'gethostbyname(\'rest\') failed: {e}')
        print(f'restapi hostname = localhost')
        return 'localhost'
