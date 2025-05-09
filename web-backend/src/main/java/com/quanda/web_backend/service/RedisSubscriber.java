package com.quanda.web_backend.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.connection.MessageListener;
import org.springframework.data.redis.connection.RedisConnection;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.connection.Message;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;

@Service
public class RedisSubscriber {
    private final SimpMessagingTemplate messagingTemplate;
    private final RedisConnectionFactory redisConnectionFactory;

    @Autowired
    public RedisSubscriber(SimpMessagingTemplate messagingTemplate, 
                          RedisConnectionFactory redisConnectionFactory) {
        this.messagingTemplate = messagingTemplate;
        this.redisConnectionFactory = redisConnectionFactory;
        subscribeToChannels();
    }

    private void subscribeToChannels() {
        new Thread(() -> {
            RedisConnection redisConnection = redisConnectionFactory.getConnection();
            redisConnection.subscribe(
                    new MessageListener() {
                        @Override
                        public void onMessage(Message message, byte[] pattern) {
                            String channel = new String(message.getChannel(), StandardCharsets.UTF_8);
                            String payload = new String(message.getBody(), StandardCharsets.UTF_8);

                            if (channel.equals("pickup-stats-channel")) {
                                messagingTemplate.convertAndSend("/topic/pickup-stats", payload);
                            } else if (channel.equals("dropoff-stats-channel")) {
                                messagingTemplate.convertAndSend("/topic/dropoff-stats", payload);
                            }
                        }
                    },
                    "pickup-stats-channel".getBytes(StandardCharsets.UTF_8), // Channel 1
                    "dropoff-stats-channel".getBytes(StandardCharsets.UTF_8)  // Channel 2
            );
        }).start();
    }
}