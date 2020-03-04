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

package com.ververica.statefun.workshop.merchants;

import java.util.Arrays;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.stream.Stream;

public class Merchants {

    private Merchants() {}

    private static String[] PREFIXES = {
        "active", "arc", "auto", "app", "avi", "base", "co", "con", "core", "clear", "en", "echo",
        "even", "ever", "fair", "go", "high", "hyper", "in", "inter", "iso", "jump", "live", "make",
        "mass", "meta", "matter", "omni", "on", "one", "open", "over", "out", "re", "real", "peak",
        "pure", "shift", "silver", "solid", "spark", "start", "true", "up", "vibe"
    };

    private static String[] WORD_SUFFIXES = {
        "arc", "atlas", "base", "bay", "boost", "capsule", "case", "center", "cast", "click", "dash",
        "deck", "dock", "dot", "drop", "engine", "flow", "glow", "grid", "gram", "graph", "hub",
        "focus", "kit", "lab", "level", "layer", "light", "line", "logic", "load", "loop", "ment",
        "method", "mode", "mark", "ness", "now", "pass", "port", "post", "press", "prime", "push",
        "rise", "scape", "scale", "scan", "scout", "sense", "set", "shift", "ship", "side", "signal",
        "snap", "scope", "space", "span", "spark", "spot", "start", "storm", "stripe", "sync", "tap",
        "tilt", "ture", "type", "view", "verge", "vibe", "ware", "yard", "up"
    };

    private static final String[] MERCHANTS =
        Arrays.stream(PREFIXES)
            .flatMap(prefix -> Arrays.stream(WORD_SUFFIXES).map(suffix -> prefix + suffix))
            .map(Merchants::capitalize)
            .toArray(String[]::new);

    private static String capitalize(String word) {
    return word.substring(0, 1).toUpperCase() + word.substring(1);
  }

    private static Stream<String> shuffle(String[] items) {
        List<String> list = Arrays.asList(items);
        Collections.shuffle(list);
        return list.stream();
    }

    public static Iterator<String> iterator() {
        return Stream
                .generate(() -> Merchants.MERCHANTS)
                .flatMap(Merchants::shuffle)
                .iterator();
    }
}
