from kane_pe.materials import Concrete, Steel
from kane_pe.sections import RectangularSection, ReinforcedConcreteSection
from kane_pe.checks import SectionCheck

# --- Δημιουργία αντικειμένου σκυροδέματος ---
concrete = Concrete(fck=30)  # fck σε MPa

# --- Δημιουργία αντικειμένου χάλυβα ---
steel = Steel(fyk=313, E=200000)  # fyk σε MPa, E σε MPa

# --- Δημιουργία ορθογωνικής διατομής ---
section = RectangularSection(
    width=0.25,    # πλάτος σε m
    height=0.25,   # ύψος σε m
    H=3.2,         # συνολικό ύψος σε m
    material=concrete,
    name="BeamSection"
)

# --- Δημιουργία διατομής οπλισμένου σκυροδέματος ---
rc_section = ReinforcedConcreteSection(
    section=section,
    concrete=concrete,
    steel=steel,
    cnom=0.015,  # επικάλυψη σκυροδέματος (m)
    db=14,       # διάμετρος ράβδων (mm)
    n_db=2,      # αριθμός ράβδων
    dbw=8,       # διάμετρος εγκάρσιων (mm)
    sw=0.2,      # βήμα εγκάρσιων (m)
    name="Beam_RC"
)

# --- Δημιουργία αντικειμένου ελέγχου διατομής ---
checker = SectionCheck(rc_section)

# --- Υπολογισμός παραμόρφωσης διαρροής χάλυβα ---
res = checker.calc_yield_strain(N=750)  # N = αξονική δύναμη σε kN
print(res)

# --- Υπολογισμός ροπής διαρροής ---
My = checker.calc_yield_moment(res['ry'], res['jy'])
print("Ροπή διαρροής My:", My)

# --- Υπολογισμός Τέμνουσας κατά την διαρροή ---
VMy = checker.calc_yield_shear(My)
print("Δύναμη διαρροής VMy:", VMy)

# --- Υπολογισμός γωνίας διαρροής θy ---
thita_y = checker.thita_y(res['ry'])

# --- Υπολογισμός δυσκαμψίας K ---
K = checker.calc_stiffness(My, thita_y)
print("Δυσκαμψία K:", K)
