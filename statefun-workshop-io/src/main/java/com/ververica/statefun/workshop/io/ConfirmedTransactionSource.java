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
import org.apache.flink.streaming.api.functions.source.RichSourceFunction;
import org.apache.flink.util.Preconditions;

import java.util.concurrent.TimeUnit;

public class ConfirmedTransactionSource extends RichSourceFunction<ConfirmFraud> {

    private final int maxRecordsPerSecond;

    private volatile boolean running = true;

    ConfirmedTransactionSource(int maxRecordsPerSecond) {
        Preconditions.checkArgument(
                maxRecordsPerSecond == -1 || maxRecordsPerSecond > 0,
                "maxRecordsPerSecond must be positive or -1 (infinite)");

        this.maxRecordsPerSecond = maxRecordsPerSecond;
    }

    @Override
    public void run(SourceContext<ConfirmFraud> ctx) throws Exception {
        final Throttler throttler = new Throttler(maxRecordsPerSecond, 1);

        while (running) {
            try {
                String id = FeedbackChannel.queue.poll(1, TimeUnit.SECONDS);

                if (id != null) {
                    ctx.collect(ConfirmFraud.newBuilder().setAccount(id).build());
                }

                throttler.throttle();
            } catch (InterruptedException e) {
                running = false;
            }
        }
    }

    @Override
    public void cancel() {
        running = false;
    }
}
