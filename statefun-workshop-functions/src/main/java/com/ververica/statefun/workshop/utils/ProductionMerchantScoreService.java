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

package com.ververica.statefun.workshop.utils;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;

public class ProductionMerchantScoreService implements MerchantScoreService {

    /**
     * used to complete the futures after an artificial random delay, that simulates network latency,
     * service busyness etc'
     */
    private final ScheduledExecutorService executor = newScheduledExecutorService();

    @Override
    public CompletableFuture<Integer> query(String merchantId) {
        CompletableFuture<Integer> result = new CompletableFuture<>();

        final long randomCompletionDelay = ThreadLocalRandom.current().nextLong(5_000);
        executor.schedule(completeRandomly(merchantId, result), randomCompletionDelay, TimeUnit.MILLISECONDS);

        return result;
    }

    /**
     * returns a {@link Runnable}, that when runs, it completes the supplied future {@code result}
     * with a number that might be either done or still running. If done, then the task status would
     * have a completion time.
     */
    private static Runnable completeRandomly(String merchantId, CompletableFuture<Integer> result) {
        return () -> {
            boolean fail = ThreadLocalRandom.current().nextBoolean();

            if (fail) {
                result.completeExceptionally(new Throwable());
            } else {
                result.complete(ThreadLocalRandom.current().nextInt(100));
            }
        };
    }

    /** A scheduled executor service with daemon threads. */
    private static ScheduledExecutorService newScheduledExecutorService() {
        return Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r);
            t.setDaemon(true);
            return t;
        });
    }
}
