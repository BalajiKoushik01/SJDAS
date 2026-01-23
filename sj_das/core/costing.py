from sj_das.utils.logger import logger


class CostingEngine:
    """
    Competitive Feature: Yarn Costing Estimator (NedGraphics Competitor).
    Calculates precise yarn consumption and cost for a design.
    """

    def calculate_cost(self,
                       design_width_hooks: int,
                       design_height_picks: int,
                       specs: dict) -> dict:
        """
        Calculate total cost and consumption.

        Args:
            design_width_hooks: Number of warp ends (hooks)
            design_height_picks: Number of weft insertions (picks)
            specs: Dict containing:
                   - 'width_inches': Fabric width
                   - 'epi': Ends Per Inch (Warp Density)
                   - 'ppi': Picks Per Inch (Weft Density)
                   - 'warp_denier': Thickness of warp yarn
                   - 'weft_denier': Thickness of weft yarn
                   - 'warp_price': Price/kg
                   - 'weft_price': Price/kg
                   - 'waste_pct': Percentage waste (default 5%)

        Returns:
            Dict detailed report.
        """
        try:
            # Defaults
            width_in = specs.get('width_inches', 45)
            ppi = specs.get('ppi', 60)
            epi = specs.get('epi', 60)

            # 1. Calculate Physical Dimensions
            # Total design length in meters (Picks / PPI) / 39.37 (inches to
            # meters)
            length_meters = (design_height_picks / ppi) / 39.37

            # 2. Warp Consumption (Vertical Length)
            # Warp runs the full length.
            # Total Ends = design_width_hooks (or Width_Inches * EPI)
            # Generally use Total Ends.
            total_ends = design_width_hooks
            total_warp_length = total_ends * length_meters

            # Warp Weight (Kg) = (Length(m) * Denier) / 9,000,000  (Formula:
            # Denier is g/9000m)
            warp_den = specs.get('warp_denier', 20)  # 20D Silk
            warp_weight_kg = (total_warp_length * warp_den) / 9000000

            # 3. Weft Consumption (Horizontal Length)
            # Each pick traverses the full width
            width_meters = width_in / 39.37
            total_weft_length = design_height_picks * width_meters

            weft_den = specs.get('weft_denier', 40)  # 40D Silk/Zari
            weft_weight_kg = (total_weft_length * weft_den) / 9000000

            # 4. Waste
            waste_pct = specs.get('waste_pct', 5.0) / 100.0
            warp_weight_kg *= (1 + waste_pct)
            weft_weight_kg *= (1 + waste_pct)

            # 5. Cost
            warp_cost = warp_weight_kg * \
                specs.get('warp_price', 6000)  # Rs 6000/kg Silk
            weft_cost = weft_weight_kg * \
                specs.get('weft_price', 4000)  # Rs 4000/kg Zari/Silk

            return {
                "dimensions": {
                    "width_inch": width_in,
                    "length_meter": f"{length_meters:.2f}",
                    "total_picks": design_height_picks
                },
                "consumption": {
                    "warp_kg": f"{warp_weight_kg:.3f}",
                    "weft_kg": f"{weft_weight_kg:.3f}",
                    "total_kg": f"{(warp_weight_kg + weft_weight_kg):.3f}"
                },
                "cost": {
                    "warp_cost": f"₹{warp_cost:.2f}",
                    "weft_cost": f"₹{weft_cost:.2f}",
                    "total_cost": f"₹{(warp_cost + weft_cost):.2f}"
                },
                "success": True
            }

        except Exception as e:
            logger.error(f"Cost Calculation Failed: {e}")
            return {"success": False, "error": str(e)}
