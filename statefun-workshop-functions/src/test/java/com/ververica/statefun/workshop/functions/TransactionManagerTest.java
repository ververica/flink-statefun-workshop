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

package com.ververica.statefun.workshop.functions;

import static com.ververica.statefun.workshop.identifiers.*;
import static com.ververica.statefun.workshop.io.identifiers.ALERT;
import static org.apache.flink.statefun.testutils.matchers.StatefulFunctionMatchers.*;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.equalTo;

import com.google.protobuf.Any;
import com.google.protobuf.Timestamp;
import com.ververica.statefun.workshop.functions.exercises.TransactionManager;
import com.ververica.statefun.workshop.generated.FeatureVector;
import com.ververica.statefun.workshop.generated.FraudScore;
import com.ververica.statefun.workshop.generated.QueryFraud;
import com.ververica.statefun.workshop.generated.Transaction;
import com.ververica.statefun.workshop.generated.MerchantScore;
import com.ververica.statefun.workshop.generated.QueryMerchantScore;
import com.ververica.statefun.workshop.generated.ReportedFraud;
import org.apache.flink.statefun.sdk.Address;
import org.apache.flink.statefun.testutils.function.FunctionTestHarness;
import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;

@Ignore
public class TransactionManagerTest {

    private static final String ACCOUNT = "account-id";

    private static final String MERCHANT = "merchant-id";

    private static final Transaction TRANSACTION = Transaction.newBuilder()
            .setAccount(ACCOUNT)
            .setMerchant(MERCHANT)
            .setTimestamp(Timestamp.getDefaultInstance())
            .setAmount(100)
            .build();

    @Test
    public void initialTransactionTest() {
        FunctionTestHarness harness = FunctionTestHarness.test(ignore -> new TransactionManager(), MANAGER_FN, "id");

        Assert.assertThat(
            harness.invoke(TRANSACTION),
            sent(
                    messagesTo(new Address(FRAUD_FN, ACCOUNT), equalTo(QueryFraud.getDefaultInstance())),
                    messagesTo(new Address(MERCHANT_FN, MERCHANT), equalTo(QueryMerchantScore.getDefaultInstance()))));
    }

    @Test
    public void reportFraudThenMerchantTest() {
        FunctionTestHarness harness = FunctionTestHarness.test(ignore -> new TransactionManager(), MANAGER_FN, "id");

        harness.invoke(TRANSACTION);

        Assert.assertThat(harness.invoke(ReportedFraud.newBuilder().setCount(1).build()), sentNothing());

        Assert.assertThat(
            harness.invoke(MerchantScore.newBuilder().setScore(1).build()),
            sent(
                messagesTo(
                    new Address(MODEL_FN, ACCOUNT),
                    equalTo(Any.pack(FeatureVector.newBuilder().setFraudCount(1).setMerchantScore(1).build())))));
    }

    @Test
    public void reportMerchantThenFraudTest() {
        FunctionTestHarness harness = FunctionTestHarness.test(ignore -> new TransactionManager(), MANAGER_FN, "id");

        harness.invoke(TRANSACTION);

        Assert.assertThat(harness.invoke(MerchantScore.newBuilder().setScore(1).build()), sentNothing());

        Assert.assertThat(
            harness.invoke(ReportedFraud.newBuilder().setCount(1).build()),
            sent(
                messagesTo(
                    new Address(MODEL_FN, ACCOUNT),
                    equalTo(Any.pack(FeatureVector.newBuilder().setFraudCount(1).setMerchantScore(1).build())))));
    }

    @Test
    public void discoveredFraudTest() {
        FunctionTestHarness harness = FunctionTestHarness.test(ignore -> new TransactionManager(), MANAGER_FN, "id");
        harness.invoke(TRANSACTION);

        Assert.assertThat(harness.invoke(Any.pack(FraudScore.newBuilder().setScore(81).build())), sentNothing());

        Assert.assertThat(harness.getEgress(ALERT), contains(equalTo(TRANSACTION)));
    }

    @Test
    public void falseFraudTest() {
        FunctionTestHarness harness = FunctionTestHarness.test(ignore -> new TransactionManager(), MANAGER_FN, "id");
        harness.invoke(TRANSACTION);

        Assert.assertThat(harness.invoke(Any.pack(FraudScore.newBuilder().setScore(81).build())), sentNothing());

        Assert.assertThat(harness.getEgress(ALERT), contains(equalTo(TRANSACTION)));
    }
}
