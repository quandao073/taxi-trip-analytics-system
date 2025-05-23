package com.quanda.web_backend.controller;

import com.quanda.web_backend.entity.*;
import com.quanda.web_backend.service.TaxiAnalyticsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/analytics")
@CrossOrigin(origins = "*")
public class TaxiAnalyticsController {

    @Autowired
    private TaxiAnalyticsService analyticsService;

    // Get time-based analytics
    @GetMapping("/time")
    public ResponseEntity<List<AnalyzeByTime>> getTimeAnalytics(
            @RequestParam(required = false) Integer year,
            @RequestParam(required = false) Integer month) {

        List<AnalyzeByTime> result = analyticsService.getTimeAnalytics(year, month);
        return ResponseEntity.ok(result);
    }

    // Get time analytics by range
    @GetMapping("/time/range")
    public ResponseEntity<List<AnalyzeByTime>> getTimeAnalyticsByRange(
            @RequestParam Integer startYear,
            @RequestParam Integer startMonth,
            @RequestParam Integer endYear,
            @RequestParam Integer endMonth) {

        List<AnalyzeByTime> result = analyticsService.getTimeAnalyticsByRange(startYear, startMonth, endYear, endMonth);
        return ResponseEntity.ok(result);
    }

    // // Get route-based analytics
    // @GetMapping("/routes")
    // public ResponseEntity<List<AnalyzeByRoutes>> getRouteAnalytics(
    //         @RequestParam(required = false) Integer year,
    //         @RequestParam(required = false) Integer month,
    //         @RequestParam(required = false) String zone) {

    //     List<AnalyzeByRoutes> result = analyticsService.getRouteAnalytics(year, month, zone);
    //     return ResponseEntity.ok(result);
    // }


}
