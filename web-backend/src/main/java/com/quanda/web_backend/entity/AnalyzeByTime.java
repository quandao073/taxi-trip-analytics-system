package com.quanda.web_backend.entity;

import jakarta.persistence.*;
import com.quanda.web_backend.entity.AnalyzeByTimeId;
import java.math.BigDecimal;

@Entity
@Table(name = "analyze_by_time")
@IdClass(AnalyzeByTimeId.class)
public class AnalyzeByTime {

    @Id
    @Column(name = "year")
    private Integer year;
    
    @Id
    @Column(name = "month")
    private Integer month;
    
    @Column(name = "trip_count")
    private Long tripCount;
    
    @Column(name = "total_revenue")
    private BigDecimal totalRevenue;
    
    @Column(name = "avg_distance_km")
    private BigDecimal avgDistanceKm;
    
    @Column(name = "avg_duration_minutes")
    private BigDecimal avgDurationMinutes;
    
    @Column(name = "avg_speed_kph")
    private BigDecimal avgSpeedKph;
    
    public AnalyzeByTime() {}
    
    public Integer getYear() { return year; }
    public void setYear(Integer year) { this.year = year; }
    
    public Integer getMonth() { return month; }
    public void setMonth(Integer month) { this.month = month; }
    
    public Long getTripCount() { return tripCount; }
    public void setTripCount(Long tripCount) { this.tripCount = tripCount; }
    
    public BigDecimal getTotalRevenue() { return totalRevenue; }
    public void setTotalRevenue(BigDecimal totalRevenue) { this.totalRevenue = totalRevenue; }
    
    public BigDecimal getAvgDistanceKm() { return avgDistanceKm; }
    public void setAvgDistanceKm(BigDecimal avgDistanceKm) { this.avgDistanceKm = avgDistanceKm; }
    
    public BigDecimal getAvgDurationMinutes() { return avgDurationMinutes; }
    public void setAvgDurationMinutes(BigDecimal avgDurationMinutes) { this.avgDurationMinutes = avgDurationMinutes; }
    
    public BigDecimal getAvgSpeedKph() { return avgSpeedKph; }
    public void setAvgSpeedKph(BigDecimal avgSpeedKph) { this.avgSpeedKph = avgSpeedKph; }
    
}