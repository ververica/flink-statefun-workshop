# Flink Stateful Functions Workshop 

## Setup Instructions

The following instructions guide you through the process of setting up a development environment for developing,
debugging and executing solutions for the workshop.

### Software Requirements

This workshop includes embedded stateful functions written in Java,
and a remote function implemented in Python.

The following software is required for running the code for this workshop:

* Git
* Docker

For the exercises described below, you will also need a text editor for making (minor) modifications to the Python code, and `curl` for using the REST API.

### Clone and Prepare the Software

```bash
$ git clone https://github.com/ververica/flink-statefun-workshop.git
$ cd flink-statefun-workshop 
$ docker-compose build
```

If you haven't done this before, at this point, you'll end up downloading all of the dependencies for this project and its Docker image.
This usually takes a few minutes, depending on the speed of your internet connection.

### Get it Running

```bash
$ docker-compose up -d 
```

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

This Stateful Functions application is composed of _Remote Functions_ which run in a seperate, stateless container, connected via HTTP. It has two ingresses, one for Transactions (that need to be scored), and another for Transactions that have been confirmed by the customer as having been fraudulent. The egress handles Alert messages for Transactions that have been scored as being possibly fraudulent by the Model.

Incoming Transactions are routed to the TransactionManager, which sends them to both the MerchantFunction (for the relevant Merchant) and to the FraudCount function (for the relevant account). These functions send back feature data that gets packed into a FeatureVector that is then sent to the Model for scoring. The Model responds with a FraudScore that the TransactionManager uses to determine whether or not to create an Alert.

All ConfirmFraud messages are routed to the FraudCount function, which keeps one piece of per-account state: a count of Transactions that have been confirmed as fraudulent during the past 30 days. 

The TransactionManager keeps three items of per-transaction state, which are cleared once the transaction has been fully processed.

The MerchantFunction uses an asynchronously connected MerchantScoreService to provide the score for each Merchant. This mimics the HTTP connection you might have in a real-world application that uses a third-party service to provide enrichment data. The MerchantFunction handles timeouts and retries for the merchant scoring service.

## Exercises (Python)

The activities in this section can be done via the command line.

### Restart the Functions

Since the functions are stateless, and running in their own container, we can redeploy and rescale it independently of the rest of the infrastructure.

We can't truly achieve a proper zero-downtime restart of the functions without a more elaborate setup, but can do a restart that merely causes the ongoing HTTP requests to be retried.

In one terminal window:

```bash
$ docker-compose up -d
```

and then restart the python-worker container:

```bash
$ docker-compose restart python-worker
```

<details>
<summary>
Solution
</summary>

Stateful Function applications seperate compute from the Apache Flink runtime, so functions can be redeployed without any downtime. 

If you search the TaskManager logs, you will find it logged a `RetryableException`, which means the functions were unavailable but the runtime will attempt to reconnect. When Flink is able to reconnect, the log lines will go away.

```bash
$ docker-compose logs -f worker

worker_1         | 2020-10-13 19:07:15,327 WARN  org.apache.flink.statefun.flink.core.httpfn.RetryingCallback [] - Retriable exception caught while trying to deliver a message: ToFunctionRequestSummary(address=Address(ververica, counter, 0x007B6AB1), batchSize=1, totalSizeInBytes=108, numberOfStates=1)
worker_1         | java.net.ConnectException: Failed to connect to python-worker/192.168.16.2:8000
```

Checking the JobManager logs, you will find the application continues to operate without issue and **does not** restart from checkpoint.

```bash

$ docker-compose logs -f master

master_1         | 2020-10-13 19:07:45,548 INFO  org.apache.flink.runtime.checkpoint.CheckpointCoordinator    [] - Triggering checkpoint 11 (type=CHECKPOINT) @ 1602616065531 for job fc1fce4f02097b11cfda8caef36bee9c.
master_1         | 2020-10-13 19:07:46,153 INFO  org.apache.flink.runtime.checkpoint.CheckpointCoordinator    [] - Completed checkpoint 11 for job fc1fce4f02097b11cfda8caef36bee9c (53147 bytes in 605 ms).
```

</details>

### Change the Model

Now that you know how to redeploy the model without disrupting the pipeline, go ahead and modify and then redeploy the functions by editing `statefun-functions/main.py`. 
The function `fraud_count` currently increments the count per `Address` forever. 
Modify the function to maintain a 30 day rolling window, i.e., everytime the count is incremented there should be a corresponding event in 30 days time that decrements it. You can use the `ExpireFraud` type to implement your solution.

<details>
<summary>
Hint 1
</summary>

A function instance can message any other, including itself.

</details>

<details>
<summary>
Hint 2
</summary>

The function `context` contains a method [pack_and_send_after](https://ci.apache.org/projects/flink/flink-statefun-docs-stable/sdk/python.html#sending-delayed-messages) which will send a message that arrives after some duration.

</details>

<details>
<summary>
Solution
</summary>

Everytime a `ConfirmFraud` message is received, the function should send itself a delayed message to decrement the count after 30 days.
Delayed messages are non-blocking and durable so they function will continue to process messages during that time and the expiration notice is guarunteed to arrive even if the application has to restart from failure. 

```python
@functions.bind("ververica/counter")
def fraud_count(context, message: Union[ConfirmFraud, QueryFraud, ExpireFraud]):

    if isinstance(message, ConfirmFraud):
        count = context.state("fraud_count").unpack(ReportedFraud)
        if not count:
            count = ReportedFraud()
            count.count = 1
        else:
            count.count += 1

        context.state("fraud_count").pack(count)
        context.pack_and_send_after(
            timedelta(days=30),
            context.address.typename(),
            context.address.identity,
            ExpireFraud())

    elif isinstance(message, QueryFraud):
        count = context.state("fraud_count").unpack(ReportedFraud)

        if not count:
            count = ReportedFraud()

        context.pack_and_reply(count)

    elif isinstance(message, ExpireFraud):
        count = context.state("fraud_count").unpack(ReportedFraud)
        count.count -= 1
        
        if count.count == 0: 
            del context["fraud_count"]
        else:
            context.state("fraud_count").pack(count)
```

</details>

## Exercises (Operations)

### Explore the Flink WebUI

The Stateful Functions runtime is based on a [Apache Flink](https://flink.apache.org). If you browse to [http://localhost:8001](http://localhost:8001) this will bring up the Flink WebUI which you can use to explore the cluster running this application.

Start by clicking on this StatefulFunctions job in the list of running jobs:

![](images/stateful-functions-job-overview.png)

This will then bring up a depiction of the Flink pipeline used for running Stateful Functions application, and some metrics about the activity in the Flink cluster.

Go ahead and explore! 

### Use the Flink CLI to do a Stateful Restart

Flink is playing the role of a database in this application: it is managing all of the persistent state. You may have noticed that regular checkpoints are being mentioned in the logs. In the case of a failure, Flink will restart from the most recent checkpoint.

Flink checkpoints are normally used only for automatic recovery in event of failure. To rescale or redeploy the cluster, you should take a _savepoint_ and use that savepoint when restarting.

The steps involved are:

1. Find the job ID
1. Take a savepoint
1. Stop the job
1. Restart the job with the savepoint

#### Finding the job ID

```bash
$ curl localhost:8001/jobs
{"jobs":[{"id":"3df90de7785eb1920b517d409e2fe475","status":"RUNNING"}]}
```

(You can also find the job ID in the WebUI.)

#### Taking a Savepoint

Be sure to replace `'jobid` with the job ID you found above.

```bash
$ curl -X POST localhost:8001/jobs/:jobid/savepoints -d '{"cancel-job": false}'
```

#### Stopping the Job

You can simply bring down all of the Docker containers. The savepoint includes all of the state needed to resume cleanly.

#### Restarting the Job with the Savepoint

You will find the savepoint in `./savepoint-dir`, e.g.,

```bash
$ ls savepoint-dir/
savepoint-3df90d-aa82d691740f
```

To bring up a brand new instance, using the state in this savepoint as the starting point, modify `./docker-compose.yml`. You will need to find a line that looks like this:

```
    #command: -s /savepoint-dir/savepoint-3df90d-aa82d691740f
```

Uncomment this line, and modify the savepoint path to point to your savepoint. 

Then restart the containers:

```bash
$ docker-compose up
```

If you look closely at the logs you will see the savepoint being mentioned, as in

```
master_1        | 2020-08-12 10:24:57,982 INFO  org.apache.flink.runtime.checkpoint.CheckpointCoordinator     - Starting job 53a0baf235b4f1db93157079b60f3719 from savepoint /savepoint-dir/savepoint-3df90d-aa82d691740f ()
```

## Exercises (Advanced)

This exercise ties together SDK and operational concepts to make a complex change to the application.

After succesfully deploying a Stateful Functions application to production, a new product requirement comes into the team.
The final score, returned by the model, is judged to be fraudulent if it is greater than a predefined threshold.
Different accounts have different levels of tolerance for suspicous activity, and users want to have the option to set 
their own theshold. 

The operations team has made available a Kafka topic called `thresholds` which contains messages for accounts that wish to
set custom thresholds. The topic key is the `account` and the value is the following schema.

```protobuf
message CustomThreshold {
    int32 threshold = 1;
    string account = 2;
}
```

The typeurl for this message is `com.googleapis/workshop.CustomThreshold`.

The transaction manager should be updated to use the accounts custom threshold if one exists, otherwise it should continue to use the default value. Additionally, the application should be updated **statefully**. This means existing function state such as fraud counts and merchant scores should not be lost, and old transactions should not be reprocessed. 

<details>
<summary>
Hint 1
</summary>

Just like `fraud_count` and `merchant`, we can create an additional function the `transaction manager` can query to get the accounts
configured threshold.

</details>

<details>
<summary>
Hint 2
</summary>

The `transaction manager` needs to have a way to query the current threshold. There is a predefined protobuf type `QueryThreshold`
you can use for this purpose. Its typeurl is `com.googleapis/workshop.QueryThresdhold`.

</details>

<details>
<summary>
Hint 3
</summary>

While the `thresholds` topic already exists, it is not a configured ingress. It needs to be added to the current module defined via `statefun-runtime/module.yaml`.

</details>
