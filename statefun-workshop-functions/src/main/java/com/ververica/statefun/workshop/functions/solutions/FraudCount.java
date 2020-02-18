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

import com.ververica.statefun.workshop.generated.ConfirmFraud;
import com.ververica.statefun.workshop.messages.ExpireFraud;
import com.ververica.statefun.workshop.messages.QueryFraud;
import com.ververica.statefun.workshop.messages.ReportedFraud;
import java.time.Duration;
import org.apache.flink.statefun.sdk.Context;
import org.apache.flink.statefun.sdk.StatefulFunction;
import org.apache.flink.statefun.sdk.annotations.Persisted;
import org.apache.flink.statefun.sdk.state.PersistedValue;

/**
 * This function tracks the total number of reported fraudulent transactions made against an account
 * on a rolling 30 day period. It supports three three message types:
 *
 * <p>1) {@link ConfirmFraud}: When a customer reports a fraudulent transaction the function will
 * receive this message. It will increment it's internal count and set a 30 day expiration timer.
 *
 * <p>2) {@link ExpireFraud}: After 30 days, the function will receive an expiration message. At
 * this time, it will decrement its internal count.
 *
 * <p>3) {@link QueryFraud}: Any other entity in the system may query the current count by sending
 * this message. The function will reply with the current count wrapped in a {@link ReportedFraud}
 * message.
 */
public class FraudCount implements StatefulFunction {

    @Persisted
    private final PersistedValue<Integer> count = PersistedValue.of("count", Integer.class);

    @Override
    public void invoke(Context context, Object input) {
        if (input instanceof ConfirmFraud) {
            int current = count.getOrDefault(0);
            count.set(current + 1);

            context.sendAfter(Duration.ofDays(30), context.self(), new ExpireFraud());
        }

        if (input instanceof ExpireFraud) {
            int current = count.getOrDefault(0);
            if (current == 0 || current == 1) {
                count.clear();
            }

            count.set(current - 1);
        }

        if (input instanceof QueryFraud) {
            int current = count.getOrDefault(0);
            ReportedFraud response = new ReportedFraud(current);
            context.reply(response);
        }
    }
}
