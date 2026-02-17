class SoilRecoveryEngine:
    def __init__(self, crop_db):
        self.crop_db = crop_db

    def calculate_soil_impact(self, current_soil, selected_crop):
        crop_needs = self.crop_db.get(selected_crop)
        if not crop_needs:
            return None

        # Calculate post-harvest nutrients
        n_after = current_soil["n"] - crop_needs["n_demand"]
        p_after = current_soil["p"] - crop_needs["p_demand"]
        k_after = current_soil["k"] - crop_needs["k_demand"]

        # If it's a legume (like Soybeans), it actually adds Nitrogen
        if crop_needs["family"] == "Legume":
            n_after = current_soil["n"] + abs(crop_needs["n_demand"])

        result = {
            "nitrogen": n_after,
            "phosphorus": p_after,
            "potassium": k_after,
            "is_depleted": n_after < 20 or p_after < 15 or k_after < 20
        }
        return result

    def suggest_recovery_crop(self, analysis):
        if analysis["nitrogen"] < 30:
            return "Legumes (Beans/Peas) to restore Nitrogen levels."
        if analysis["phosphorus"] < 20:
            return "Bone meal enrichment or Phosphorus-efficient cover crops."
        return "Standard Clover Cover Crop."