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

import com.google.protobuf.Timestamp;
import com.ververica.statefun.workshop.generated.Transaction;
import com.ververica.statefun.workshop.merchants.Merchants;

import java.time.Instant;
import java.util.SplittableRandom;
import org.apache.flink.api.common.state.ListState;
import org.apache.flink.api.common.state.ListStateDescriptor;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.runtime.state.FunctionInitializationContext;
import org.apache.flink.runtime.state.FunctionSnapshotContext;
import org.apache.flink.streaming.api.checkpoint.CheckpointedFunction;
import org.apache.flink.streaming.api.functions.source.RichSourceFunction;
import org.apache.flink.util.Preconditions;

/** A simple random data generator with data rate throttling logic (max parallelism: 1). */
public class TransactionSource
        extends RichSourceFunction<Transaction>
        implements CheckpointedFunction {

    private static final long serialVersionUID = 1L;

    private final int maxRecordsPerSecond;

    private volatile boolean running = true;

    private long id = -1;

    private transient ListState<Long> idState;

    TransactionSource(int maxRecordsPerSecond) {
        Preconditions.checkArgument(
                maxRecordsPerSecond == -1 || maxRecordsPerSecond > 0,
                "maxRecordsPerSecond must be positive or -1 (infinite)");

        this.maxRecordsPerSecond = maxRecordsPerSecond;
    }

    @Override
    public void open(Configuration parameters) throws Exception {
        if (id == -1) {
            id = getRuntimeContext().getIndexOfThisSubtask();
        }
    }

    @Override
    @SuppressWarnings("SynchronizationOnLocalVariableOrMethodParameter")
    public final void run(SourceContext<Transaction> ctx) throws Exception {
        final int numberOfParallelSubtasks = getRuntimeContext().getNumberOfParallelSubtasks();
        final Throttler throttler = new Throttler(maxRecordsPerSecond, numberOfParallelSubtasks);
        final SplittableRandom rnd = new SplittableRandom();

        final Object lock = ctx.getCheckpointLock();

        while (running) {
            Transaction event = randomEvent(rnd, id);

            synchronized (lock) {
                ctx.collect(event);
                id += numberOfParallelSubtasks;
            }

            try {
                throttler.throttle();
            } catch (InterruptedException e) {
                running = false;
            }
        }
    }

    @Override
    public final void cancel() {
        running = false;
    }

    @Override
    public final void snapshotState(FunctionSnapshotContext context) throws Exception {
        idState.clear();
        idState.add(id);
    }

    @Override
    public void initializeState(FunctionInitializationContext context) throws Exception {
        idState = context
                .getOperatorStateStore()
                .getUnionListState(new ListStateDescriptor<>("ids", Types.LONG));

        if (context.isRestored()) {
            long max = Long.MIN_VALUE;
            for (Long value : idState.get()) {
                max = Math.max(max, value);
            }

            id = max + getRuntimeContext().getIndexOfThisSubtask();
        }
    }

    private Transaction randomEvent(SplittableRandom rnd, long id) {
        Instant time = Instant.now();
        return Transaction.newBuilder()
            .setMerchant(Merchants.MERCHANTS[((int) id) % Merchants.MERCHANTS.length])
            .setAccount(String.format("0x%08X", rnd.nextInt(0x100000, 0x1000000)))
            .setAmount(rnd.nextInt(100000))
            .setTimestamp(Timestamp.newBuilder()
                    .setSeconds(time.getEpochSecond())
                    .setNanos(time.getNano()).build())
            .build();
    }
}
