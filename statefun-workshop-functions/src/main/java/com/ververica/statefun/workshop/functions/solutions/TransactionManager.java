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

package com.ververica.statefun.workshop.functions.solutions;

import static com.ververica.statefun.workshop.identifiers.*;
import static com.ververica.statefun.workshop.io.identifiers.ALERT;

import com.google.protobuf.Any;
import com.google.protobuf.InvalidProtocolBufferException;
import com.ververica.statefun.workshop.generated.FeatureVector;
import com.ververica.statefun.workshop.generated.FraudScore;
import com.ververica.statefun.workshop.generated.QueryFraud;
import com.ververica.statefun.workshop.generated.Transaction;
import com.ververica.statefun.workshop.generated.MerchantScore;
import com.ververica.statefun.workshop.generated.QueryMerchantScore;
import com.ververica.statefun.workshop.generated.ReportedFraud;
import org.apache.flink.statefun.sdk.Context;
import org.apache.flink.statefun.sdk.StatefulFunction;
import org.apache.flink.statefun.sdk.annotations.Persisted;
import org.apache.flink.statefun.sdk.state.PersistedValue;

public class TransactionManager implements StatefulFunction {

    private static final int THRESHOLD = 80;

    @Persisted
    private final PersistedValue<Transaction> transactionState = PersistedValue.of("transaction", Transaction.class);

    @Persisted
    private final PersistedValue<Integer> recentFraudCount = PersistedValue.of("recent-fraud-count", Integer.class);

    @Persisted
    private final PersistedValue<MerchantScore> merchantScore = PersistedValue.of("merchant-score", MerchantScore.class);

    @Override
    public void invoke(Context context, Object input) {
        if (input instanceof Transaction) {
            Transaction transaction = (Transaction) input;
            transactionState.set(transaction);

            String account = transaction.getAccount();
            context.send(FRAUD_FN, account, QueryFraud.getDefaultInstance());

            String merchant = transaction.getMerchant();
            context.send(MERCHANT_FN, merchant, QueryMerchantScore.getDefaultInstance());
        }

        if (input instanceof ReportedFraud) {
            ReportedFraud reported = (ReportedFraud) input;
            recentFraudCount.set(reported.getCount());

            MerchantScore merchant = merchantScore.get();
            if (merchant != null) {
                score(context, merchant, reported.getCount());
            }
        }

        if (input instanceof MerchantScore) {
            MerchantScore reportedScore = (MerchantScore) input;
            merchantScore.set(reportedScore);

            Integer count = recentFraudCount.get();
            if (count != null) {
                score(context, reportedScore, count);
            }
        }

        if (input instanceof Any) {
            final FraudScore fraudScore;
            try {
                fraudScore = (((Any) input).unpack(FraudScore.class));
            } catch (InvalidProtocolBufferException e) {
                throw new RuntimeException("Unexpected type", e);
            }
            if (fraudScore.getScore() > THRESHOLD) {
                context.send(ALERT, transactionState.get());
            }

            transactionState.clear();
            recentFraudCount.clear();
            merchantScore.clear();
        }
    }

    private void score(Context context, MerchantScore merchant, Integer count) {
        FeatureVector.Builder vector = FeatureVector.newBuilder().setFraudCount(count);

        if (!merchant.getError()) {
            vector.setMerchantScore(merchant.getScore());
        }

        Any message = Any.pack(vector.build());
        context.send(MODEL_FN, transactionState.get().getAccount(), message);
    }
}
