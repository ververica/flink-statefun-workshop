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

import com.ververica.statefun.workshop.generated.ConfirmFraud;
import com.ververica.statefun.workshop.generated.Transaction;
import org.apache.flink.statefun.sdk.io.EgressIdentifier;
import org.apache.flink.statefun.sdk.io.IngressIdentifier;

@SuppressWarnings("WeakerAccess")
public class identifiers {

    public static final IngressIdentifier<ConfirmFraud> CONFIRM_FRAUD =
            new IngressIdentifier<>(ConfirmFraud.class, "ververica", "confim-fraud");

    public static final IngressIdentifier<Transaction> TRANSACTIONS =
            new IngressIdentifier<>(Transaction.class, "ververica", "transactions");

    public static final EgressIdentifier<Transaction> ALERT =
            new EgressIdentifier<>("ververica", "alert", Transaction.class);
}
