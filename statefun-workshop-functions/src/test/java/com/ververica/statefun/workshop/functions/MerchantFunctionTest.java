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

import static com.ververica.statefun.workshop.identifiers.MERCHANT_FN;
import static org.apache.flink.statefun.testutils.matchers.StatefulFunctionMatchers.*;
import static org.hamcrest.core.IsEqual.equalTo;

import com.ververica.statefun.workshop.functions.exercises.MerchantFunction;
import com.ververica.statefun.workshop.generated.MerchantScore;
import com.ververica.statefun.workshop.generated.QueryMerchantScore;
import com.ververica.statefun.workshop.utils.MerchantScoreService;
import org.apache.flink.statefun.sdk.Address;
import org.apache.flink.statefun.sdk.FunctionType;
import org.apache.flink.statefun.sdk.StatefulFunction;
import org.apache.flink.statefun.sdk.StatefulFunctionProvider;
import org.apache.flink.statefun.testutils.function.FunctionTestHarness;
import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;

@Ignore
public class MerchantFunctionTest {

    private static String SELF_ID = "my-id";

    private static Address CALLER = new Address(new FunctionType("ververica", "caller"), "id");

     @Test
    public void testAsyncOperation() {
        FunctionTestHarness harness = FunctionTestHarness.test(new TestProvider(), MERCHANT_FN, SELF_ID);

        Assert.assertThat(
                harness.invoke(CALLER, QueryMerchantScore.getDefaultInstance()),
                sent(messagesTo(CALLER, equalTo(MerchantScore.newBuilder().setScore(1).build()))));
    }

    @Test
    public void testSingleFailureOperation() {
         FunctionTestHarness harness = FunctionTestHarness.test(new TestProviderWithSingleFailure(), MERCHANT_FN, SELF_ID);

        Assert.assertThat(
                harness.invoke(CALLER, QueryMerchantScore.getDefaultInstance()),
                sent(messagesTo(CALLER, equalTo(MerchantScore.newBuilder().setScore(1).build()))));
    }

    @Test
    public void testAsyncFailure() {
        FunctionTestHarness harness = FunctionTestHarness.test(new TestProviderWithMultipleFailures(), MERCHANT_FN, SELF_ID);

        Assert.assertThat(
                harness.invoke(CALLER, QueryMerchantScore.getDefaultInstance()),
                sent(messagesTo(CALLER, equalTo(MerchantScore.newBuilder().setError(true).build()))));
    }

    private static class TestProvider implements StatefulFunctionProvider {

         @Override
        public StatefulFunction functionOfType(FunctionType type) {
            MerchantScoreService client = MockMerchantScoreService.builder().withResponse(1).build();

            return new MerchantFunction(client);
        }
    }

    private static class TestProviderWithSingleFailure implements StatefulFunctionProvider {

        @Override
        public StatefulFunction functionOfType(FunctionType type) {
            MerchantScoreService client = MockMerchantScoreService.builder()
                    .withResponse(new Throwable("error"))
                    .withResponse(1)
                    .build();

            return new MerchantFunction(client);
        }
    }

    private static class TestProviderWithMultipleFailures implements StatefulFunctionProvider {

        @Override
        public StatefulFunction functionOfType(FunctionType type) {
            MerchantScoreService client = MockMerchantScoreService.builder()
                    .withResponse(new Throwable("error"))
                    .withResponse(new Throwable("error"))
                    .withResponse(new Throwable("error"))
                    .build();

            return new MerchantFunction(client);
        }
    }
}
