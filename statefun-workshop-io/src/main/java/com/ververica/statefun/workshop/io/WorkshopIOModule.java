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

package com.ververica.statefun.workshop.io;

import static com.ververica.statefun.workshop.io.identifiers.ALERT;
import static com.ververica.statefun.workshop.io.identifiers.CONFIRM_FRAUD;
import static com.ververica.statefun.workshop.io.identifiers.TRANSACTIONS;

import com.ververica.statefun.workshop.generated.ConfirmFraud;
import com.ververica.statefun.workshop.generated.Transaction;
import java.util.Map;

import com.ververica.statefun.workshop.io.local.ConfirmedTransactionSource;
import com.ververica.statefun.workshop.io.local.TransactionLoggerSink;
import com.ververica.statefun.workshop.io.local.TransactionSource;
import org.apache.flink.statefun.flink.io.datastream.SinkFunctionSpec;
import org.apache.flink.statefun.flink.io.datastream.SourceFunctionSpec;
import org.apache.flink.statefun.sdk.io.EgressSpec;
import org.apache.flink.statefun.sdk.io.IngressSpec;
import org.apache.flink.statefun.sdk.spi.StatefulFunctionModule;

public class WorkshopIOModule implements StatefulFunctionModule {

    @Override
    public void configure(Map<String, String> globalConfiguration, Binder binder) {
        IOConfig config = IOConfig.fromGlobalConfig(globalConfiguration);
        configureLocal(config.getLocalConfig(), binder);
    }

    private void configureLocal(IOConfig.LocalConfig config, Binder binder) {
        IngressSpec<Transaction> transactions = new SourceFunctionSpec<>(
                TRANSACTIONS,
                new TransactionSource(config.getTransactionRate().getSeconds()));

        binder.bindIngress(transactions);

        IngressSpec<ConfirmFraud> confirmedFraud = new SourceFunctionSpec<>(
                CONFIRM_FRAUD,
                new ConfirmedTransactionSource(10));

        binder.bindIngress(confirmedFraud);

        EgressSpec<Transaction> alert = new SinkFunctionSpec<>(ALERT, new TransactionLoggerSink());
        binder.bindEgress(alert);
    }
}
