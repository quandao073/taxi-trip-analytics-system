package com.quanda.web_backend.service;

import com.quanda.web_backend.entity.*;
import com.quanda.web_backend.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class TaxiAnalyticsService {

    @Autowired
    private AnalyzeByTimeRepository timeRepository;

    @Autowired
    private AnalyzeByRoutesRepository routesRepository;

    // Time-based analytics
    public List<AnalyzeByTime> getTimeAnalytics(Integer year, Integer month) {
        if (year != null && month != null) {
            return timeRepository.findByYearAndMonth(year, month);
        }
        return timeRepository.findAllOrderByYearMonthDesc();
    }

    public List<AnalyzeByTime> getTimeAnalyticsByRange(int startYear, int startMonth, int endYear, int endMonth) {
        return timeRepository.findByFullRange(startYear, startMonth, endYear, endMonth);
    }

    // Route-based analytics
    public List<AnalyzeByRoutes> getRouteAnalytics(Integer year, Integer month, String zone) {
        if (year != null && month != null) {
            return routesRepository.findByYearAndMonth(year, month);
        }
        if (zone != null) {
            List<AnalyzeByRoutes> byPickup = routesRepository.findByPickupZone(zone);
            List<AnalyzeByRoutes> byDropoff = routesRepository.findByDropoffZone(zone);
            byDropoff.removeAll(byPickup);
            byPickup.addAll(byDropoff);
            return byPickup;
        }
        return routesRepository.findAll();
    }

    public Map<String, List<AnalyzeByRoutes>> getTopRoutesByZone(Integer year, Integer month, String zone) {
        PageRequest top5 = PageRequest.of(0, 5);

        List<AnalyzeByRoutes> pickups = routesRepository.findTop5ByPickupZone(year, month, zone, top5);
        List<AnalyzeByRoutes> dropoffs = routesRepository.findTop5ByDropoffZone(year, month, zone, top5);

        Map<String, List<AnalyzeByRoutes>> result = new HashMap<>();
        result.put("dropoffs", dropoffs);
        result.put("pickups", pickups);
        return result;
    }
}
