package com.quanda.web_backend.entity;

import java.io.Serializable;
import java.util.Objects;

public class AnalyzeByTimeId implements Serializable {
    private Integer year;
    private Integer month;

    public AnalyzeByTimeId() {}

    public AnalyzeByTimeId(Integer year, Integer month) {
        this.year = year;
        this.month = month;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof AnalyzeByTimeId)) return false;
        AnalyzeByTimeId that = (AnalyzeByTimeId) o;
        return Objects.equals(year, that.year) && Objects.equals(month, that.month);
    }

    @Override
    public int hashCode() {
        return Objects.hash(year, month);
    }
}
