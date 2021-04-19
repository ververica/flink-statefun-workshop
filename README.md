# Flink Stateful Functions Workshop 

This is a simple Stateful Function that scores feature vectors using a random model.
It is packaged in a separate branch so simulate developing functions across multiple teams and deployments.

## Build Locally 

When developing the model, you can build the docker image locally for use with the workshop material.

```bash 
$ docker build . -b model:latest
```

Afterwards, update the `model` container in `docker-compose.yml` of the main branch to use your tagged image
instead of pulling from a registry. 

## Publish 

This branch is setup with a Github Action to publish on each [release](https://docs.github.com/en/github/administering-a-repository/managing-releases-in-a-repository).


