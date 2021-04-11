# Flink Stateful Functions Workshop 

## Setup Instructions

The following instructions guide you through the process of setting up a development environment for developing,
debugging and executing solutions for the workshop.

### Software Requirements

This workshop includes stateful functions written in Python.

The following software is required for running the code for this workshop:

* python3
* pip 
* docker 
* docker-compose


For the exercises described below, you will also need a text editor for making (minor) modifications to the Python code, and `curl` for using the REST API.

### Clone and Prepare the Software
#### Using venv

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install .
```

### Executing Tests

The workshop contains a number of unit tests to help validate the correctness of your functions.
These can be executed by running: `python3 -m unittest`

### Get it Running

This setup does not reflect how you would normally deploy StateFun processes and functions.

From one terminal: `python3 -m workshop`

This will start the user code process and is a simplified environment to allow you to explore the interaction between
functions and the StateFun processes by setting debugger breakpoints in the function code in your IDE.

From another terminal: `docker-compose up -d`

If you haven't done this before, at this point, you'll end up downloading all of the dependencies for this project and its Docker image.
This usually takes a few minutes, depending on the speed of your internet connection.

This will start all the cluster components.
Once everything is up and running, after a minute or so you should start to see messages like this in the simulator logs:

```
$ docker-compose logs -f simulator

Attaching to statefun-workshop_simulator_1
simulator_1      | Suspected Fraud for account id 0x00F3CD51 at Hypergrid for 36 USD
simulator_1      | Suspected Fraud for account id 0x009D999B at Uparc for 835 USD
```

## Architecture

![architecture diagram](images/statefun-workshop.svg)

This Stateful Functions application is composed of functions which run in a separate, stateless container, connected via HTTP.
It has two ingresses, one for Transactions (that need to be scored), and another for Transactions that have been confirmed by the customer as having been fraudulent.
The egress handles Alert messages for Transactions that have been scored as being possibly fraudulent by the Model.

Incoming Transactions are routed to the TransactionManager, which sends them to both the MerchantFunction (for the relevant Merchant) and to the FraudCount function (for the relevant account).
These functions send back feature data that gets packed into a FeatureVector that is then sent to the Model for scoring.
The Model responds with a FraudScore that the TransactionManager uses to determine whether or not to create an Alert.

All ConfirmFraud messages are routed to the FraudCount function, which keeps one piece of per-account state: a count of Transactions that have been confirmed as fraudulent during the past 30 minutes. 

The TransactionManager keeps three items of per-transaction state, which are cleared once the transaction has been fully processed.

The MerchantFunction uses an asynchronously connected MerchantScoreService to provide the score for each Merchant.
This mimics the HTTP connection you might have in a real-world application that uses a third-party service to provide enrichment data.
The MerchantFunction handles timeouts and retries for the merchant scoring service.

