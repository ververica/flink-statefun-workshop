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

import org.apache.flink.configuration.ConfigOption;
import org.apache.flink.configuration.ConfigOptions;
import org.apache.flink.configuration.Configuration;

import java.time.Duration;
import java.util.Map;

final class IOConfig {

    private static final ConfigOption<IOType> IO_TYPE = ConfigOptions
            .key("io-type")
            .enumType(IOType.class)
            .noDefaultValue();

    static IOConfig fromGlobalConfig(Map<String, String> globalConfig) {
        Configuration config = new Configuration();
        globalConfig.forEach(config::setString);

        IOType type = config.get(IO_TYPE);

        return new IOConfig(
                type,
                type == IOType.LOCAL ? LocalConfig.fromConfig(config) : null,
                type == IOType.KAFKA ? KafkaConfig.fromConfig(config) : null);
    }

    private final IOType ioType;

    private final LocalConfig localConfig;

    private final KafkaConfig kafkaConfig;

    IOConfig(
            IOType ioType,
            LocalConfig localConfig,
            KafkaConfig kafkaConfig) {
        this.ioType = ioType;
        this.localConfig = localConfig;
        this.kafkaConfig = kafkaConfig;
    }

    IOType getIOType() {
        return ioType;
    }

    LocalConfig getLocalConfig() {
        return localConfig;
    }

    KafkaConfig getKafkaConfig() {
        return kafkaConfig;
    }

    static class LocalConfig {

        private static final ConfigOption<Duration> TRANSACTION_RATE = ConfigOptions
                .key("local.transaction-rate")
                .durationType()
                .defaultValue(Duration.ofSeconds(10));

        static LocalConfig fromConfig(Configuration config) {
            return new LocalConfig(config.get(TRANSACTION_RATE));
        }

        private Duration transactionRate;

        LocalConfig(Duration transactionRate) {
            this.transactionRate = transactionRate;
        }

        Duration getTransactionRate() {
            return transactionRate;
        }
    }

    static class KafkaConfig {

        private static final ConfigOption<String> KAFKA_ADDRESS = ConfigOptions
                .key("kafka.address")
                .stringType()
                .noDefaultValue();

        private static final ConfigOption<String> TRANSACTION_TOPIC = ConfigOptions
                .key("kafka.transaction-topic")
                .stringType()
                .noDefaultValue();

        private static final ConfigOption<String> FRAUD_TOPIC = ConfigOptions
                .key("kafka.confirmed-fraud-topic")
                .stringType()
                .noDefaultValue();

        static KafkaConfig fromConfig(Configuration config) {
            return new KafkaConfig(
                    config.get(KAFKA_ADDRESS),
                    config.get(TRANSACTION_TOPIC),
                    config.get(FRAUD_TOPIC));
        }

        private final String kafkaAddress;

        private final String transactionTopic;

        private final String confirmFraudTopic;

        KafkaConfig(String kafkaAddress, String transactionTopic, String confirmFraudTopic) {
            this.kafkaAddress = kafkaAddress;
            this.transactionTopic = transactionTopic;
            this.confirmFraudTopic = confirmFraudTopic;
        }

        String getKafkaAddress() {
            return kafkaAddress;
        }

        String getTransactionTopic() {
            return transactionTopic;
        }

        String getConfirmFraudTopic() {
            return confirmFraudTopic;
        }
    }

    enum IOType {
        LOCAL,
        KAFKA;

        static IOType fromString(String name) {
            if ("local".equalsIgnoreCase(name)) {
                return LOCAL;
            } else if ("kafka".equalsIgnoreCase(name)) {
                return KAFKA;
            }

            throw new IllegalStateException("Unknown IOType " + name);
        }
    }
}
