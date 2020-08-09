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

package com.ververica.statefun.workshop.harness;

import static com.ververica.statefun.workshop.io.identifiers.ALERT;
import static com.ververica.statefun.workshop.io.identifiers.CONFIRM_FRAUD;
import static com.ververica.statefun.workshop.io.identifiers.TRANSACTIONS;

import com.ververica.statefun.workshop.generated.Transaction;
import com.ververica.statefun.workshop.io.local.ConfirmedTransactionSource;
import com.ververica.statefun.workshop.io.local.TransactionSource;
import com.ververica.statefun.workshop.io.local.FeedbackChannel;

import org.apache.flink.statefun.flink.harness.Harness;
import org.apache.flink.statefun.flink.harness.io.SerializableConsumer;

import org.junit.Ignore;
import org.junit.Test;


public class RunnerTest {

	@Ignore("This would never complete; un-ignore to execute in the IDE")
	@Test
	public void run() throws Exception {

		Harness harness =
				new Harness()
					.withGlobalConfiguration("io-type", "local")
					.withGlobalConfiguration("local.transaction-rate", "10s")
					.withFlinkSourceFunction(CONFIRM_FRAUD, new ConfirmedTransactionSource(10))
					.withFlinkSourceFunction(TRANSACTIONS, new TransactionSource(10))
					.withConsumingEgress(ALERT, new TransactionConsumer());

		harness.start();
	}

	private static final class TransactionConsumer implements SerializableConsumer<Transaction> {

		private static final long serialVersionUID = 1;

		@Override
		public void accept(Transaction t) {
			FeedbackChannel.confirmSomeAsFraud(t);
			String msg = String.format("Suspected Fraud for account id %s at %s", t.getAccount(), t.getMerchant());
			System.out.println(msg);
		}
	}
}
