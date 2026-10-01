from typing import List, Dict, Any, Tuple

class ScoringEngine:
    """
    Evaluates hardware & PCB defect detections and computes automated inspection score (0-100)
    along with actionable repair recommendations for vocational students.
    """

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
        "miss_welding": 20.0,
        "spillover": 15.0,
        "damged": 25.0,
        "damaged": 25.0,
        "lack_of_part": 20.0,
        "slug": 15.0,
        "redundant": 15.0,
        "defect": 15.0
    }

    RECOMMENDATIONS_MAP = {
        "short_circuit": "Short circuit detected between adjacent copper traces/pads. Scrape excess copper or remove solder bridge using solder wick.",
        "short": "Short circuit detected on PCB trace. Clean unwanted connection with solder braid or precision knife.",
        "miss_welding": "Titik solder tidak tersambung sempurna (miss welding / dry joint). Panaskan ulang kaki komponen dan tambahkan timah secara merata.",
        "spillover": "Timah solder meluber keluar batas pad (solder spillover). Bersihkan kelebihan timah menggunakan solder wick / atraktor.",
        "damged": "Kerusakan fisik terdeteksi pada jalur PCB atau pad tembaga. Periksa kontinuitas jalur menggunakan multimeter dan lakukan jumper bila terputus.",
        "damaged": "Kerusakan fisik pada papan PCB. Lakukan penambalan jalur tembaga atau perbaikan pad yang terangkat.",
        "lack_of_part": "Komponen belum terpasang pada pad PCB (lack of part). Pasang komponen yang sesuai dengan diagram skematik rangkaian.",
        "slug": "Terdapat gumpalan timah sisa (solder slug / blob). Bersihkan residu timah menggunakan kuas pembersih dan alkohol IPA.",
        "redundant": "Sisa tembaga atau serpihan timah berlebih pada area isolasi PCB. Bersihkan permukaan menggunakan pisau presisi atau solder wick.",
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

    def evaluate(
        self,
        detections: List[Dict[str, Any]],
        preprocessor_warning: str = None,
        is_pcb: bool = True
    ) -> Tuple[float, List[Dict[str, Any]], List[str]]:
        
        # Non-PCB validation failure state (PRD 2 Section 9)
        if not is_pcb and not detections:
            recommendations = [
                "Objek PCB / Hardware tidak terdeteksi. Pastikan foto memperlihatkan papan rangkaian yang jelas (bukan objek acak)."
            ]
            parsed_defects = [{
                "class_name": "non_pcb_object",
                "confidence": 1.0,
                "penalty": 100.0,
                "bbox": []
            }]
            return 0.0, parsed_defects, recommendations

        base_score = 100.0
        parsed_defects = []
        recommendations = []
        seen_recommendation_keys = set()

        for det in detections:
            raw_class = str(det.get("class_name", "")).lower().replace(" ", "_")
            confidence = float(det.get("confidence", 0.0))
            bbox = det.get("bbox", [])

            if "good" in raw_class or "ok" in raw_class or "normal" in raw_class:
                continue

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
