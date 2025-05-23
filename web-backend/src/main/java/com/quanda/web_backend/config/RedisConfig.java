package com.quanda.web_backend.config;

import com.quanda.web_backend.service.RedisSubscriber;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.*;
import org.springframework.data.redis.connection.*;
import org.springframework.data.redis.connection.lettuce.*;
import org.springframework.data.redis.listener.*;
import org.springframework.data.redis.listener.adapter.MessageListenerAdapter;

import java.util.Arrays;
import java.time.Duration;

@Configuration
public class RedisConfig {

    @Value("${spring.redis.sentinel.master}")
    private String master;

    @Value("${spring.redis.sentinel.nodes}")
    private String nodes;

    @Value("${spring.redis.password}")
    private String password;

    @Bean
    public RedisConnectionFactory redisConnectionFactory() {
        RedisSentinelConfiguration sentinelConfig = new RedisSentinelConfiguration();
        sentinelConfig.master(master);
        Arrays.stream(nodes.split(","))
                .map(String::trim)
                .map(n -> n.split(":"))
                .forEach(p -> sentinelConfig.addSentinel(new RedisNode(p[0], Integer.parseInt(p[1]))));
                
        sentinelConfig.setSentinelPassword(RedisPassword.of(password));
        sentinelConfig.setPassword(RedisPassword.of(password));
        
        LettuceClientConfiguration clientConfig = LettuceClientConfiguration.builder()
                .commandTimeout(Duration.ofMillis(60000))
                .shutdownTimeout(Duration.ZERO)
                .build();
                
        return new LettuceConnectionFactory(sentinelConfig, clientConfig);
    }

    @Bean
    public RedisMessageListenerContainer redisMessageListenerContainer(
            RedisConnectionFactory factory,
            MessageListenerAdapter adapter) {
        RedisMessageListenerContainer container = new RedisMessageListenerContainer();
        container.setConnectionFactory(factory);
        container.addMessageListener(adapter, new ChannelTopic("realtime-trip-channel"));
        return container;
    }

    @Bean
    public MessageListenerAdapter listenerAdapter(RedisSubscriber subscriber) {
        return new MessageListenerAdapter(subscriber, "onMessage");
    }
}


//  import com.quanda.web_backend.service.RedisSubscriber;
//  import org.springframework.beans.factory.annotation.Value;
//  import org.springframework.context.annotation.*;
//  import org.springframework.data.redis.connection.*;
//  import org.springframework.data.redis.connection.lettuce.*;
//  import org.springframework.data.redis.listener.*;
//  import org.springframework.data.redis.listener.adapter.MessageListenerAdapter;
//  import java.time.Duration;
 
// @Configuration
// public class RedisConfig {

//     @Value("${spring.redis.host}")
//     private String host;

//     @Value("${spring.redis.port}")
//     private int port;

//     @Bean
//     public RedisConnectionFactory redisConnectionFactory() {
//         RedisStandaloneConfiguration standaloneConfig = new RedisStandaloneConfiguration();
//         standaloneConfig.setHostName(host);
//         standaloneConfig.setPort(port);

//         LettuceClientConfiguration clientConfig = LettuceClientConfiguration.builder()
//                 .commandTimeout(Duration.ofMillis(60000))
//                 .shutdownTimeout(Duration.ZERO)
//                 .build();

//         return new LettuceConnectionFactory(standaloneConfig, clientConfig);
//     }

//     @Bean
//     public RedisMessageListenerContainer redisMessageListenerContainer(
//             RedisConnectionFactory factory,
//             MessageListenerAdapter adapter) {
//         RedisMessageListenerContainer container = new RedisMessageListenerContainer();
//         container.setConnectionFactory(factory);
//         container.addMessageListener(adapter, new ChannelTopic("realtime-trip-channel"));
//         System.out.println("✅ Redis listener container initialized and subscribed to channel: realtime-trip-channel");
//         return container;
//     }

//     @Bean
//     public MessageListenerAdapter listenerAdapter(RedisSubscriber subscriber) {
//         return new MessageListenerAdapter(subscriber, "onMessage");
//     }
// }