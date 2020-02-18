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

import org.apache.flink.statefun.sdk.FunctionType;

public class identifiers {

  public static final FunctionType MANAGER_FN = new FunctionType("ververica", "transaction-manager");

  public static final FunctionType FRAUD_FN = new FunctionType("ververica", "fraud-count");

  public static final FunctionType MERCHANT_FN = new FunctionType("ververica", "merchant");

  public static final FunctionType MODEL_FN = new FunctionType("ververica", "model");
}
