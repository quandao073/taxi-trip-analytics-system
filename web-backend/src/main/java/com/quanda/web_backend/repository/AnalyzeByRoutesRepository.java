package com.quanda.web_backend.repository;

import com.quanda.web_backend.entity.AnalyzeByRoutes;
import com.quanda.web_backend.entity.AnalyzeByRoutesId;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AnalyzeByRoutesRepository extends JpaRepository<AnalyzeByRoutes, AnalyzeByRoutesId> {

    List<AnalyzeByRoutes> findByYearAndMonth(Integer year, Integer month);

    List<AnalyzeByRoutes> findByPickupZone(String pickupZone);

    List<AnalyzeByRoutes> findByDropoffZone(String dropoffZone);

    @Query("SELECT a FROM AnalyzeByRoutes a " +
           "WHERE a.year = :year AND a.month = :month AND a.pickupZone = :zone " +
           "ORDER BY a.tripCount DESC")
    List<AnalyzeByRoutes> findTop5ByPickupZone(@Param("year") Integer year,
                                               @Param("month") Integer month,
                                               @Param("zone") String zone,
                                               Pageable pageable);

    @Query("SELECT a FROM AnalyzeByRoutes a " +
           "WHERE a.year = :year AND a.month = :month AND a.dropoffZone = :zone " +
           "ORDER BY a.tripCount DESC")
    List<AnalyzeByRoutes> findTop5ByDropoffZone(@Param("year") Integer year,
                                                @Param("month") Integer month,
                                                @Param("zone") String zone,
                                                Pageable pageable);
}