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

package com.ververica.statefun.workshop.messages;

import com.ververica.statefun.workshop.functions.solutions.MerchantFunction;
import org.apache.flink.statefun.sdk.Address;

/**
 * The metadata stored along with each async request in the {@link MerchantFunction}.
 *
 * <p>It tracks the {@link Address} where the final result should be sent along with the number of
 * remaining attempts in case of failure.
 */
public final class MerchantMetadata {

    private final Address address;

    private final int remainingAttempts;

    public MerchantMetadata(Address address, int remainingAttempts) {
        this.address = address;
        this.remainingAttempts = remainingAttempts;
    }

    public Address getAddress() {
        return address;
    }

    public int getRemainingAttempts() {
        return remainingAttempts;
    }
}
