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

package com.ververica.statefun.workshop.provider;

import com.ververica.statefun.workshop.functions.solutions.MerchantFunction;
import com.ververica.statefun.workshop.utils.MerchantScoreService;
import com.ververica.statefun.workshop.utils.ProductionMerchantScoreService;
import org.apache.flink.statefun.sdk.FunctionType;
import org.apache.flink.statefun.sdk.StatefulFunction;
import org.apache.flink.statefun.sdk.StatefulFunctionProvider;

public class MerchantProvider implements StatefulFunctionProvider {

    @Override
    public StatefulFunction functionOfType(FunctionType type) {
        MerchantScoreService client = new ProductionMerchantScoreService();
        return new MerchantFunction(client);
    }
}
