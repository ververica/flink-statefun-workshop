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

package com.ververica.statefun.workshop.functions.exercises;

import com.ververica.statefun.workshop.messages.ExpireFraud;
import com.ververica.statefun.workshop.messages.QueryFraud;
import com.ververica.statefun.workshop.messages.ReportedFraud;
import org.apache.flink.statefun.sdk.Context;
import org.apache.flink.statefun.sdk.StatefulFunction;

/**
 * This function tracks the total number of reported fraudulent transactions made against an account
 * on a rolling 30 day period. It supports three three message types:
 *
 * <p>1) {@code ConfirmFraud}: When a customer reports a fraudulent transaction the function will
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

    @Override
    public void invoke(Context context, Object input) {}
}
