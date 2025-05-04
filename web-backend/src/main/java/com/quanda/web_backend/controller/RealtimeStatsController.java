package com.quanda.web_backend.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.HashOperations;
import org.springframework.data.redis.core.ZSetOperations;

import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/realtime")
public class RealtimeStatsController {

    private final StringRedisTemplate redisTemplate;
    private final HashOperations<String, String, String> hashOps;
    private final ZSetOperations<String, String> zSetOps;

    public RealtimeStatsController(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
        this.hashOps = redisTemplate.opsForHash();
        this.zSetOps = redisTemplate.opsForZSet();
    }

    // API: Top 10 pickup zones
    @GetMapping("/zone/top")
    public List<Map<String, Object>> getTopPickupZones() {
        Set<String> topZones = zSetOps.reverseRange("top_zones", 0, 9);
        if (topZones == null) return Collections.emptyList();

        return topZones.stream()
                .map(zone -> {
                    String tripCountStr = hashOps.get("pickup:trip_count:zone", zone);
                    String revenueStr = hashOps.get("pickup:revenue:zone", zone);
                    Map<String, Object> map = new HashMap<>();
                    map.put("zone", zone);
                    map.put("trip_count", tripCountStr != null ? Integer.parseInt(tripCountStr) : 0);
                    map.put("total_revenue", revenueStr != null ? Double.parseDouble(revenueStr) : 0.0);
                    return map;
                })
                .collect(Collectors.toList());
    }

    // API: Top 5 pickup boroughs
    @GetMapping("/borough/top")
    public List<Map<String, Object>> getTopPickupBoroughs() {
        Set<String> topBoroughs = zSetOps.reverseRange("top_boroughs", 0, 4);
        if (topBoroughs == null) return Collections.emptyList();

        return topBoroughs.stream()
                .map(borough -> {
                    String tripCountStr = hashOps.get("pickup:trip_count:borough", borough);
                    String revenueStr = hashOps.get("pickup:revenue:borough", borough);
                    Map<String, Object> map = new HashMap<>();
                    map.put("borough", borough);
                    map.put("trip_count", tripCountStr != null ? Integer.parseInt(tripCountStr) : 0);
                    map.put("total_revenue", revenueStr != null ? Double.parseDouble(revenueStr) : 0.0);
                    return map;
                })
                .collect(Collectors.toList());
    }

    // API: Top 10 dropoff zones by avg speed
    @GetMapping("/dropoff/avg_speed/top")
    public List<Map<String, Object>> getTopDropoffZonesBySpeed() {
        Set<ZSetOperations.TypedTuple<String>> topZones = zSetOps.reverseRangeWithScores("top_avg_speed_dropoff_zones", 0, 9);
        if (topZones == null) return Collections.emptyList();

        return topZones.stream()
                .map(tuple -> {
                    Map<String, Object> map = new HashMap<>();
                    map.put("dropoff_zone", tuple.getValue());
                    map.put("avg_speed", tuple.getScore());
                    return map;
                })
                .collect(Collectors.toList());
    }
}
