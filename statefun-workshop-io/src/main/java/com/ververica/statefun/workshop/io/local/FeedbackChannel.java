package com.ververica.statefun.workshop.io.local;

import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

class FeedbackChannel {
    static final BlockingQueue<String> queue = new ArrayBlockingQueue<>(1024);
}
