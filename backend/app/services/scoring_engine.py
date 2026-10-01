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
        "short_circuit": "Hubungan singkat (short circuit) terdeteksi antar jalur/kaki komponen. Bersihkan jembatan timah solder menggunakan solder wick (pita tembaga desoldering) atau pompa atraktor timah.",
        "short": "Hubungan singkat (short circuit) terdeteksi pada jalur PCB. Periksa jarak isolasi antar jalur dan serap kelebihan timah dengan solder wick.",
        "miss_welding": "Titik solder tidak tersambung sempurna (miss welding / dry joint). Panaskan ulang kaki komponen dan tambahkan timah berinti fluks secara merata.",
        "spillover": "Timah solder meluber keluar batas pad (solder spillover). Bersihkan kelebihan timah menggunakan solder wick / atraktor agar tidak menyentuh jalur lain.",
        "damged": "Kerusakan fisik / jalur terputus terdeteksi pada PCB. Periksa kontinuitas jalur menggunakan multimeter dan lakukan pemasangan jumper bila terputus.",
        "damaged": "Kerusakan fisik pada papan PCB. Lakukan penambalan jalur tembaga atau perbaikan pad solder yang terangkat.",
        "lack_of_part": "Komponen belum terpasang pada pad PCB (lack of part). Pasang komponen yang sesuai dengan diagram skematik rangkaian.",
        "slug": "Terdapat gumpalan timah sisa (solder slug / blob). Bersihkan residu timah menggunakan kuas pembersih dan alkohol isopropil (IPA).",
        "redundant": "Sisa tembaga atau serpihan timah berlebih pada area isolasi PCB. Bersihkan permukaan menggunakan pisau presisi atau solder wick.",
        "open_circuit": "Jalur rangkaian terputus (open circuit). Sambungkan kembali jalur menggunakan kawat jumper tembaga halus atau solder ulang.",
        "open": "Jalur tembaga terputus. Hubungkan titik yang putus menggunakan kawat jumper tembaga.",
        "missing_component": "Komponen belum terpasang pada pad PCB. Pasang komponen yang tepat sesuai petunjuk modul praktik dan solder dengan kokoh.",
        "missing": "Komponen hilang atau belum tersolder. Pasang komponen yang sesuai pada posisi pad rangkaian.",
        "spur": "Tonjolan tembaga berlebih (spur) pada tepi jalur PCB. Rapikan tepi jalur dengan pisau cutter presisi untuk mencegah korsleting mikro.",
        "mousebite": "Cacat gigitan (mousebite / retakan) pada tepi jalur. Periksa kontinuitas jalur dan perkuat dengan lapisan timah solder tipis bila perlu.",
        "mouse_bite": "Retakan pada tepi jalur tembaga PCB. Perkuat lebar jalur menggunakan lapisan solder tipis.",
        "pin_hole": "Lubang jarum (pin hole) pada permukaan sambungan timah. Panaskan kembali pad dan tambahkan sedikit timah fluks untuk menutup rongga.",
        "hole": "Rongga atau lubang jarum pada solderan. Panaskan kembali titik solder dan tambahkan timah segar.",
        "copper_residue": "Residu tembaga liar terdeteksi di antara jalur PCB. Bersihkan papan rangkaian secara menyeluruh dengan alkohol IPA.",
        "copper": "Residu tembaga atau serbuk logam tak diinginkan. Periksa celah isolasi antar jalur PCB.",
        "bridge": "Jembatan solder (solder bridge) antar pin kaki komponen. Berikan fluks dan panaskan kaki komponen dengan mata solder untuk memutus jembatan timah.",
        "solder_bridge": "Jembatan solder terdeteksi antar pin. Bersihkan kelebihan timah menggunakan solder wick / atraktor dan oleskan fluks pembersih.",
        "void": "Rongga udara (void / rongga kosong) pada timah solder. Panaskan kembali sambungan sampai timah mencair rata dan mengisi pad secara menyeluruh.",
        "cold_joint": "Sambungan solder dingin (cold joint / buram berbutir). Panaskan ulang sambungan dengan solder panas hingga timah mengkilap dan berbentuk kerucut cekung.",
        "insufficient_solder": "Jumlah timah solder kurang pada pad komponen. Tambahkan timah solder berinti fluks sampai membentuk fillet cekung yang mengikat kuat.",
        "excess_solder": "Timah solder terlalu tebal / menggumpal. Sedot kelebihan timah menggunakan desoldering pump atau solder wick.",
        "polarity_error": "Polaritas orientasi komponen terbalik (misal: elco, dioda, IC). Lepas solderan komponen dan pasang kembali sesuai orientasi pin 1 yang tepat.",
        "component_misplacement": "Posisi komponen bergeser / miring dari pusat pad. Panaskan pad dan luruskan posisi komponen menggunakan pinset presisi.",
        "bad_soldering": "Kualitas penyolderan kurang baik. Lakukan reflow pemanasan ulang dengan bantuan sedikit fluks solder.",
        "defect": "Cacat hardware / solderan terdeteksi. Periksa kembali sambungan pada area yang ditandai dan lakukan touch-up penyolderan."
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
            recommendations.append("Sempurna! Kualitas perakitan dan penyolderan PCB telah memenuhi standar lab vokasi. Tidak ada cacat terdeteksi.")
        elif preprocessor_warning:
            recommendations.insert(0, f"Perhatian: {preprocessor_warning}")

        return round(final_score, 1), parsed_defects, recommendations
