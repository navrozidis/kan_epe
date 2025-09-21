from kane_pe.materials import Concrete, Steel
from kane_pe.sections import RectangularSection, ReinforcedConcreteSection

concrete = Concrete(fck=30, gamma_c=1.5, name="C30/37")
steel = Steel(fyk=313, gamma_s=1.15, E=200000 , name="B500")

section = RectangularSection(width=0.25, height=0.25, H=3.2, material=concrete, name="BeamSection")

rc_section = ReinforcedConcreteSection(
    section=section,
    concrete=concrete,
    steel=steel,
    cnom=0.015,
    db=14,
    n_db=2,
    dbw=8,
    sw=0.2,
    name="Beam_RC"
)

print(rc_section)
print("Εμβαδον σκυροδέματος:", rc_section.Acc, "m²")
