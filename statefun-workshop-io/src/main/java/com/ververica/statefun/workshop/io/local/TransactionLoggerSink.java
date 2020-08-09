/*
 * Copyright 2020 Ververica GmbH
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.ververica.statefun.workshop.io.local;

import com.ververica.statefun.workshop.generated.Transaction;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.metrics.Counter;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TransactionLoggerSink extends RichSinkFunction<Transaction> {

    private static final Logger LOG = LoggerFactory.getLogger(TransactionLoggerSink.class);

    private transient Counter counter;

    @Override
    public void open(Configuration parameters) {
        counter = getRuntimeContext().getMetricGroup().counter("alerts");
    }

    @Override
    public void invoke(Transaction value, Context context) {
        counter.inc();

        FeedbackChannel.confirmSomeAsFraud(value);

        LOG.info(String.format("Suspected Fraud for account id %s at %s", value.getAccount(), value.getMerchant()));
    }
}
