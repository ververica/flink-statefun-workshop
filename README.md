# Flink Stateful Functions Workshop

This is a simple, single threaded `Python` script that produces records into `Kafka` topics for the Stateful Functions workshop.

## Build Locally

When developing the simulator, you can build the docker image locally for use with the workshop material

```bash
docker build . -t statefun-workshop-simulator:1.0.0
```  

Afterwards, update the `simulator` container in `docker-compose.yml` of the main branch
to use your tagged image instead of pulling from a registry. 