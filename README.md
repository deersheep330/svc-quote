# Quote  Service

#### run without docker
```
python main.py
```

#### start a docker service
```
docker-compose build
docker-compose push
docker stack deploy -c docker-compose.yml quote
```