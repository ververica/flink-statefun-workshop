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
import java.util.Objects;

/**
 * This message is sent from a {@link MerchantFunction} instance when reporting the trustworthiness
 * of a merchant.
 */
public final class MerchantScore {
    public static MerchantScore score(int score) {
        return new MerchantScore(score, true);
    }

    public static MerchantScore error() {
        return new MerchantScore(-1, false);
    }

    private final int score;

    private final boolean success;

    private MerchantScore(int score, boolean success) {
        this.score = score;
        this.success = success;
    }

    public int getScore() {
    return score;
  }

    public boolean isSuccess() {
    return success;
  }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        MerchantScore that = (MerchantScore) o;
        return score == that.score && success == that.success;
    }

    @Override
    public int hashCode() {
    return Objects.hash(score, success);
  }

    @Override
    public String toString() {
        StringBuilder builder = new StringBuilder("MerchantScore{");
        if (success) {
            builder.append("score=").append(score);
        } else {
            builder.append("error");
        }

        return builder.append("}").toString();
    }
}
