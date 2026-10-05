from dataclasses import dataclass, field

@dataclass
class SafetyReport:
    passed: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

def validate_analysis(data: dict) -> SafetyReport:
    blockers = []
    warnings = []

    if not data:
        blockers.append("No structured drawing analysis was produced.")

    if not data.get("units"):
        blockers.append("Drawing units are not confidently identified.")

    if not data.get("overall_dimensions"):
        warnings.append("Overall dimensions were not confidently extracted.")

    if not data.get("datum"):
        blockers.append("Machining datum/WCS is not defined. Programming must stop.")

    if not data.get("material"):
        warnings.append("Material is not confirmed.")

    return SafetyReport(
        passed=(len(blockers) == 0),
        blockers=blockers,
        warnings=warnings,
    )
