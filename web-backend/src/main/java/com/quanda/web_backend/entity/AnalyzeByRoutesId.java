package com.quanda.web_backend.entity;

import java.io.Serializable;
import java.util.Objects;

public class AnalyzeByRoutesId implements Serializable {
    private Integer year;
    private Integer month;
    private String pickupZone;
    private String dropoffZone;

    public AnalyzeByRoutesId() {}

    public AnalyzeByRoutesId(Integer year, Integer month, String pickupZone, String dropoffZone) {
        this.year = year;
        this.month = month;
        this.pickupZone = pickupZone;
        this.dropoffZone = dropoffZone;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof AnalyzeByRoutesId)) return false;
        AnalyzeByRoutesId that = (AnalyzeByRoutesId) o;
        return Objects.equals(year, that.year) &&
               Objects.equals(month, that.month) &&
               Objects.equals(pickupZone, that.pickupZone) &&
               Objects.equals(dropoffZone, that.dropoffZone);
    }

    @Override
    public int hashCode() {
        return Objects.hash(year, month, pickupZone, dropoffZone);
    }
}
