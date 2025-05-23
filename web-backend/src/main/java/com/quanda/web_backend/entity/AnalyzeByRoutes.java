package com.quanda.web_backend.entity;

import jakarta.persistence.*;
import com.quanda.web_backend.entity.AnalyzeByRoutesId;
import java.math.BigDecimal;

@Entity
@Table(name = "analyze_by_routes")
@IdClass(AnalyzeByRoutesId.class)
public class AnalyzeByRoutes {
    @Id
    @Column(name = "year")
    private Integer year;
    
    @Id
    @Column(name = "month")
    private Integer month;
    
    @Id
    @Column(name = "pickup_zone")
    private String pickupZone;
    
    @Id
    @Column(name = "dropoff_zone")
    private String dropoffZone;
    
    @Column(name = "trip_count")
    private Long tripCount;
    
    @Column(name = "avg_distance_km")
    private BigDecimal avgDistanceKm;
    
    @Column(name = "avg_duration_minutes")
    private BigDecimal avgDurationMinutes;
    
    @Column(name = "avg_fare")
    private BigDecimal avgFare;
    
    @Column(name = "total_revenue")
    private BigDecimal totalRevenue;

    
    public AnalyzeByRoutes() {}
    
    public Integer getYear() { return year; }
    public void setYear(Integer year) { this.year = year; }
    
    public Integer getMonth() { return month; }
    public void setMonth(Integer month) { this.month = month; }
    
    public String getPickupZone() { return pickupZone; }
    public void setPickupZone(String pickupZone) { this.pickupZone = pickupZone; }

    public String getDropoffZone() { return dropoffZone; }
    public void setDropoffZone(String dropoffZone) { this.dropoffZone = dropoffZone; }
    
    public Long getTripCount() { return tripCount; }
    public void setTripCount(Long tripCount) { this.tripCount = tripCount; }
    
    public BigDecimal getAvgDistanceKm() { return avgDistanceKm; }
    public void setAvgDistanceKm(BigDecimal avgDistanceKm) { this.avgDistanceKm = avgDistanceKm; }
    
    public BigDecimal getAvgDurationMinutes() { return avgDurationMinutes; }
    public void setAvgDurationMinutes(BigDecimal avgDurationMinutes) { this.avgDurationMinutes = avgDurationMinutes; }
    
    public BigDecimal getAvgFare() { return avgFare; }
    public void setAvgFare(BigDecimal avgFare) { this.avgFare = avgFare; }
    
    public BigDecimal getTotalRevenue() { return totalRevenue; }
    public void setTotalRevenue(BigDecimal totalRevenue) { this.totalRevenue = totalRevenue; }
}