from typing import List, Dict, Any, Tuple

class ScoringEngine:
    """
    Evaluates hardware defect detections and computes automated inspection score (0-100)
    along with actionable repair recommendations for vocational students.
    """

    # Defect penalty weights
    DEFECT_PENALTIES = {
        "short_circuit": 25.0,
        "bridge": 25.0,
        "solder_bridge": 25.0,
        "void": 15.0,
        "cold_joint": 15.0,
        "insufficient_solder": 10.0,
        "excess_solder": 10.0,
        "polarity_error": 20.0,
        "component_misplacement": 20.0,
        "bad_soldering": 15.0,
        "defect": 15.0
    }

    # Actionable repair recommendations
    RECOMMENDATIONS_MAP = {
        "short_circuit": "Short circuit / solder bridge detected between adjacent pins. Apply soldering flux and use a copper solder wick to remove excess solder.",
        "bridge": "Solder bridge detected between pins. Apply flux and reheat joint with soldering iron tip to break unwanted connection.",
        "solder_bridge": "Solder bridge detected. Clean excess solder using solder braid / wick and re-apply flux.",
        "void": "Void / cavity detected in solder joint. Reheat the pad and feed a small amount of rosin-core solder to fill the joint completely.",
        "cold_joint": "Cold solder joint detected (dull/grainy surface). Reheat joint until solder flows smoothly and forms a shiny concave fillet.",
        "insufficient_solder": "Insufficient solder on pad. Add rosin-core solder until a smooth concave cone shape is formed around the pin.",
        "excess_solder": "Excess solder blob detected. Remove surplus solder using solder pump or wick.",
        "polarity_error": "Component polarity misaligned (e.g. electrolytic capacitor / diode / IC pin 1). Desolder component and orient correctly before resoldering.",
        "component_misplacement": "Component misaligned or shifted from pad center. Reheat pads and adjust alignment using precision tweezers.",
        "bad_soldering": "Defective soldering joint detected. Re-flow joint with soldering iron and fresh flux.",
        "defect": "Soldering defect detected. Re-inspect pad and touch up with soldering iron."
    }

    def evaluate(self, detections: List[Dict[str, Any]], preprocessor_warning: str = None) -> Tuple[float, List[Dict[str, Any]], List[str]]:
        """
        Calculates score (0-100) and formats defect report + recommendations.

        :param detections: List of dicts, e.g. [{"class_name": "bridge", "confidence": 0.88, "bbox": [x1, y1, x2, y2]}]
        :param preprocessor_warning: Optional lighting/quality warning message.
        :return: (score, parsed_defects, recommendations)
        """
        base_score = 100.0
        parsed_defects = []
        recommendations = []
        seen_recommendation_keys = set()

        for det in detections:
            raw_class = str(det.get("class_name", "")).lower().replace(" ", "_")
            confidence = float(det.get("confidence", 0.0))
            bbox = det.get("bbox", [])

            # Match penalty key
            penalty = 15.0  # default penalty
            matched_key = "defect"
            for key, p_val in self.DEFECT_PENALTIES.items():
                if key in raw_class:
                    penalty = p_val
                    matched_key = key
                    break

            base_score -= penalty

            # Get recommendation
            rec = self.RECOMMENDATIONS_MAP.get(matched_key, "Soldering defect detected. Re-inspect pad and touch up with soldering iron.")
            if matched_key not in seen_recommendation_keys:
                recommendations.append(rec)
                seen_recommendation_keys.add(matched_key)

            parsed_defects.append({
                "class_name": det.get("class_name"),
                "confidence": round(confidence, 4),
                "penalty": penalty,
                "bbox": bbox
            })

        # Cap score between 0 and 100
        final_score = max(0.0, min(100.0, base_score))

        if not parsed_defects and not preprocessor_warning:
            recommendations.append("Excellent work! No physical soldering defects detected. Hardware assembly meets quality standards.")
        elif preprocessor_warning:
            recommendations.insert(0, f"Warning: {preprocessor_warning}")

        return round(final_score, 1), parsed_defects, recommendations
