package com.quanda.web_backend.service;

import com.quanda.web_backend.entity.*;
import com.quanda.web_backend.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

@Service
public class TaxiAnalyticsService {

    @Autowired
    private AnalyzeByTimeRepository timeRepository;

    // @Autowired
    // private AnalyzeByRoutesRepository routesRepository;

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
    // public List<AnalyzeByRoutes> getRouteAnalytics(Integer year, Integer month, String zone) {
    //     if (year != null && month != null && zone != null) {
    //         return routesRepository.findByYearMonthAndZone(year, month, zone);
    //     }
    //     if (year != null && month != null) {
    //         return routesRepository.findTopRoutesByYearMonth(year, month);
    //     }
    //     if (zone != null) {
    //         // Trả về tất cả các chuyến có zone là điểm đón hoặc trả
    //         List<AnalyzeByRoutes> byPickup = routesRepository.findByPickupZone(zone);
    //         List<AnalyzeByRoutes> byDropoff = routesRepository.findByDropoffZone(zone);
    //         byDropoff.removeAll(byPickup);
    //         byPickup.addAll(byDropoff);
    //         return byPickup;
    //     }
    //     return routesRepository.findAll();
    // }

    // public Map<String, List<AnalyzeByRoutes>> getTopRoutesByZone(String zone) {
    //     List<AnalyzeByRoutes> dropoffs = routesRepository.findTopDropoffsFromZone(zone);
    //     List<AnalyzeByRoutes> pickups = routesRepository.findTopPickupsToZone(zone);

    //     Map<String, List<AnalyzeByRoutes>> result = new HashMap<>();
    //     result.put("dropoffs", dropoffs.stream().limit(5).toList());
    //     result.put("pickups", pickups.stream().limit(5).toList());
    //     return result;
    // }

}
