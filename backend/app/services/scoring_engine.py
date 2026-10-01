from typing import List, Dict, Any, Tuple

class ScoringEngine:
    """
    Evaluates hardware & PCB defect detections and computes automated inspection score (0-100)
    along with actionable repair recommendations for vocational students.
    """

    # Defect penalty weights
    DEFECT_PENALTIES = {
        "short_circuit": 25.0,
        "short": 25.0,
        "open_circuit": 25.0,
        "open": 25.0,
        "bridge": 25.0,
        "solder_bridge": 25.0,
        "missing_component": 20.0,
        "missing": 20.0,
        "spur": 15.0,
        "mousebite": 15.0,
        "mouse_bite": 15.0,
        "pin_hole": 15.0,
        "hole": 15.0,
        "copper_residue": 15.0,
        "copper": 15.0,
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
        "short_circuit": "Short circuit detected between adjacent copper traces/pads. Scrape excess copper or remove solder bridge using solder wick.",
        "short": "Short circuit detected on PCB trace. Clean unwanted connection with solder braid or precision knife.",
        "open_circuit": "Open circuit / broken trace detected. Bridge the broken copper trace using a jumper wire or feed fresh solder across the gap.",
        "open": "Open circuit / trace break detected. Solder a thin jumper wire across the broken trace.",
        "missing_component": "Missing component detected at pad location. Place the correct component according to schematic diagram and solder securely.",
        "missing": "Component missing from PCB pad. Solder required component onto designated pad.",
        "spur": "Copper spur defect detected on trace edge. Trim unwanted copper protrusion to prevent micro-shorts.",
        "mousebite": "Mousebite / nick defect detected on PCB trace edge. Check trace width continuity and reinforce trace with solder if necessary.",
        "mouse_bite": "Nick / mousebite defect on trace edge. Reinforce copper trace width using thin solder layer.",
        "pin_hole": "Pin hole defect detected in copper pad/joint. Reheat pad and feed fresh rosin-core solder to seal cavity.",
        "hole": "Pin hole / cavity defect detected. Reheat joint and feed fresh solder to fill pinhole.",
        "copper_residue": "Copper residue defect detected between traces. Clean PCB board thoroughly with IPA alcohol or etch away excess copper.",
        "copper": "Unwanted copper residue detected. Inspect isolation gap between adjacent traces.",
        "bridge": "Solder bridge detected between pins. Apply flux and reheat joint with soldering iron tip to break unwanted connection.",
        "solder_bridge": "Solder bridge detected. Clean excess solder using solder braid / wick and re-apply flux.",
        "void": "Void / cavity detected in solder joint. Reheat pad and feed small amount of rosin-core solder to fill joint completely.",
        "cold_joint": "Cold solder joint detected (dull/grainy surface). Reheat joint until solder flows smoothly and forms shiny concave fillet.",
        "insufficient_solder": "Insufficient solder on pad. Add rosin-core solder until smooth concave cone shape is formed around pin.",
        "excess_solder": "Excess solder blob detected. Remove surplus solder using solder pump or wick.",
        "polarity_error": "Component polarity misaligned (e.g. electrolytic capacitor / diode / IC pin 1). Desolder component and orient correctly before resoldering.",
        "component_misplacement": "Component misaligned or shifted from pad center. Reheat pads and adjust alignment using precision tweezers.",
        "bad_soldering": "Defective soldering joint detected. Re-flow joint with soldering iron and fresh flux.",
        "defect": "PCB / soldering defect detected. Re-inspect pad connection and touch up assembly."
    }

    def evaluate(self, detections: List[Dict[str, Any]], preprocessor_warning: str = None) -> Tuple[float, List[Dict[str, Any]], List[str]]:
        base_score = 100.0
        parsed_defects = []
        recommendations = []
        seen_recommendation_keys = set()

        for det in detections:
            raw_class = str(det.get("class_name", "")).lower().replace(" ", "_")
            confidence = float(det.get("confidence", 0.0))
            bbox = det.get("bbox", [])

            # Ignore good joints/traces from penalties
            if "good" in raw_class or "ok" in raw_class or "normal" in raw_class:
                continue

            # Match penalty key
            penalty = 15.0
            matched_key = "defect"
            for key, p_val in self.DEFECT_PENALTIES.items():
                if key in raw_class:
                    penalty = p_val
                    matched_key = key
                    break

            base_score -= penalty

            rec = self.RECOMMENDATIONS_MAP.get(matched_key, "PCB defect detected. Re-inspect pad/trace and touch up assembly.")
            if matched_key not in seen_recommendation_keys:
                recommendations.append(rec)
                seen_recommendation_keys.add(matched_key)

            parsed_defects.append({
                "class_name": det.get("class_name"),
                "confidence": round(confidence, 4),
                "penalty": penalty,
                "bbox": bbox
            })

        final_score = max(0.0, min(100.0, base_score))

        if not parsed_defects and not preprocessor_warning:
            recommendations.append("Excellent work! PCB assembly meets quality standards. No physical defects detected.")
        elif preprocessor_warning:
            recommendations.insert(0, f"Warning: {preprocessor_warning}")

        return round(final_score, 1), parsed_defects, recommendations
