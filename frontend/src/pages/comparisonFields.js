// Defines the fields to compare, how to extract them, and how to determine the "best" value.
export const comparisonFields = [
  {
    label: "Quality Score",
    path: "comparison_ready.academics.quality_score_100",
    best: "max",
    format: (v) => v !== null && v !== undefined ? `${v}/100` : "N/A"
  },
  {
    label: "ROI",
    path: "comparison_ready.roi.roi_score_100",
    best: "max",
    format: (v) => v !== null && v !== undefined ? `${v}/100` : "N/A"
  },
  {
    label: "Match Score",
    path: "comparison_ready.recommendation.student_match_score_100",
    best: "max",
    format: (v) => v !== null && v !== undefined ? `${v}/100` : "N/A"
  },
  {
    label: "Fees (Per Year)",
    path: "comparison_ready.roi.tuition_fee",
    best: "min",
    format: (v) => v ? `₹${v.toLocaleString()}` : "N/A"
  },
  {
    label: "Hostel Available",
    path: "comparison_ready.campus.hostel_available",
    best: "none",
    format: (v) => v ? "✔" : "✖"
  },
  {
    label: "Placement %",
    path: "comparison_ready.placements.placement_percentage",
    best: "max",
    format: (v) => v ? `${v}%` : "N/A"
  },
  {
    label: "Average Package",
    path: "comparison_ready.placements.average_package",
    best: "max",
    format: (v) => v ? `₹${v} LPA` : "N/A"
  },
  {
    label: "Highest Package",
    path: "comparison_ready.placements.highest_package",
    best: "max",
    format: (v) => v ? `₹${v} LPA` : "N/A"
  },
  {
    label: "NAAC Grade",
    path: "comparison_ready.academics.naac_grade",
    best: "none", // Could be A++, hard to write simple min/max
    format: (v) => v || "N/A"
  },
  {
    label: "NIRF Rank",
    path: "comparison_ready.academics.nirf_rank",
    best: "min",
    format: (v) => v && v !== "N/A" ? `#${v}` : "N/A"
  },
  {
    label: "Recruiters",
    path: "comparison_ready.placements.top_recruiters",
    best: "none",
    format: (v) => Array.isArray(v) && v.length ? v.slice(0, 3).join(", ") + (v.length > 3 ? "..." : "") : "N/A"
  },
  {
    label: "Campus Rating",
    path: "comparison_ready.campus.campus_rating_stars",
    best: "max",
    format: (v) => v ? "⭐".repeat(Math.round(v)) : "N/A"
  }
];
