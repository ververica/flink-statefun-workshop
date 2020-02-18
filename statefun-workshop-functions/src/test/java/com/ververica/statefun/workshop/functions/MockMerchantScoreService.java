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

import com.ververica.statefun.workshop.utils.MerchantScoreService;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

public class MockMerchantScoreService implements MerchantScoreService {

    private final List<CompletableFuture<Integer>> responses;

    public static Builder builder() {
    return new Builder();
  }

    private MockMerchantScoreService(List<CompletableFuture<Integer>> responses) {
    this.responses = responses;
  }

    @Override
    public CompletableFuture<Integer> query(String merchantId) {
        if (responses.isEmpty()) {
            throw new IllegalStateException("The mock query service has been called more times then expected");
        }

        return responses.remove(0);
    }

    public static class Builder {
        private final List<CompletableFuture<Integer>> responses = new ArrayList<>();

        private Builder() {}

        public Builder withResponse(int score) {
            responses.add(CompletableFuture.completedFuture(score));
            return this;
        }

        public Builder withResponse(Throwable error) {
            CompletableFuture<Integer> future = new CompletableFuture<>();
            future.completeExceptionally(error);

            responses.add(future);
            return this;
        }

        public MockMerchantScoreService build() {
            return new MockMerchantScoreService(responses);
        }
    }
}
