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

package com.ververica.statefun.workshop;

import static com.ververica.statefun.workshop.identifiers.*;
import static com.ververica.statefun.workshop.io.identifiers.CONFIRM_FRAUD;
import static com.ververica.statefun.workshop.io.identifiers.TRANSACTIONS;

import com.ververica.statefun.workshop.functions.FraudCount;
import com.ververica.statefun.workshop.functions.TransactionManager;
import com.ververica.statefun.workshop.provider.MerchantProvider;
import com.ververica.statefun.workshop.routers.ConfirmFraudRouter;
import com.ververica.statefun.workshop.routers.TransactionRouter;
import java.util.Map;
import org.apache.flink.statefun.sdk.spi.StatefulFunctionModule;

public class ModelScoreModule implements StatefulFunctionModule {

    @Override
    public void configure(Map<String, String> globalConfiguration, Binder binder) {
        binder.bindIngressRouter(TRANSACTIONS, new TransactionRouter());
        binder.bindIngressRouter(CONFIRM_FRAUD, new ConfirmFraudRouter());

        binder.bindFunctionProvider(MANAGER_FN, ignore -> new TransactionManager());
        binder.bindFunctionProvider(FRAUD_FN, ignore -> new FraudCount());
        binder.bindFunctionProvider(MERCHANT_FN, new MerchantProvider());
    }
}
