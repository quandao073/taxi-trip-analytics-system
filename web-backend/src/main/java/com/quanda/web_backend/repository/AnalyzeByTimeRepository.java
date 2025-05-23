package com.quanda.web_backend.repository;

import com.quanda.web_backend.entity.AnalyzeByTime;
import com.quanda.web_backend.entity.AnalyzeByTimeId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AnalyzeByTimeRepository extends JpaRepository<AnalyzeByTime, AnalyzeByTimeId> {

    List<AnalyzeByTime> findByYearAndMonth(Integer year, Integer month);

    List<AnalyzeByTime> findByYearBetween(Integer startYear, Integer endYear);

    @Query("SELECT a FROM AnalyzeByTime a ORDER BY a.year DESC, a.month DESC")
    List<AnalyzeByTime> findAllOrderByYearMonthDesc();

    @Query("SELECT a FROM AnalyzeByTime a WHERE " +
            "((:startYear != :endYear) AND " +
            "((a.year > :startYear AND a.year < :endYear) OR " +
            "(a.year = :startYear AND a.month >= :startMonth) OR " +
            "(a.year = :endYear AND a.month <= :endMonth))) OR " +
            "(:startYear = :endYear AND a.year = :startYear AND a.month BETWEEN :startMonth AND :endMonth) " +
            "ORDER BY a.year, a.month")
    List<AnalyzeByTime> findByFullRange(
        @Param("startYear") Integer startYear,
        @Param("startMonth") Integer startMonth,
        @Param("endYear") Integer endYear,
        @Param("endMonth") Integer endMonth
    );

}
