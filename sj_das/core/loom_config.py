from dataclasses import dataclass


@dataclass
class LoomProfile:
    name: str
    format_ext: str  # .bmp, .jc5, .ep
    min_hooks: int
    max_hooks: int
    default_hooks: int
    default_ppi: int
    description: str


class LoomConfigEngine:
    """
    Manages Manufacturer Profiles for Loom Export.
    """

    PROFILES = {
        "udayravi": LoomProfile(
            name="Udayravi Creations (Generic)",
            format_ext=".bmp",
            min_hooks=400,
            max_hooks=2400,
            default_hooks=480,
            default_ppi=72,
            description="Standard 8-bit BMP for Electronic Jacquard Controllers (Indian Powerlooms)."
        ),
        "staubli_jc5": LoomProfile(
            name="Stäubli JC5",
            format_ext=".jc5",
            min_hooks=1344,
            max_hooks=6144,
            default_hooks=2688,
            default_ppi=96,
            description="European Standard for High-Speed Jacquards. Binary format."
        ),
        "bonas_ep": LoomProfile(
            name="Bonas EP",
            format_ext=".ep",
            min_hooks=1344,
            max_hooks=2688,
            default_hooks=1344,
            default_ppi=80,
            description="Electronic Jacquard Controller Format (Bonas)."
        ),
        "generic_bmp": LoomProfile(
            name="Generic BMP",
            format_ext=".bmp",
            min_hooks=100,
            max_hooks=10000,
            default_hooks=1200,
            default_ppi=60,
            description="Universal Image Output."
        )
    }

    def get_profile_names(self) -> list[str]:
        return list(self.PROFILES.keys())

    def get_profile(self, key: str) -> LoomProfile:
        return self.PROFILES.get(key, self.PROFILES["generic_bmp"])

    def get_formatted_names(self) -> list[str]:
        return [p.name for p in self.PROFILES.values()]

    def get_key_from_name(self, name: str) -> str:
        for k, v in self.PROFILES.items():
            if v.name == name:
                return k
        return "generic_bmp"
