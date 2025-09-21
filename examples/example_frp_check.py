from kan_epe.materials import Concrete, Steel, FRP
from kan_epe.sections import RectangularSection, ReinforcedConcreteSection
from kan_epe.checks import FRPCheck

# --- Δημιουργία αντικειμένου σκυροδέματος ---
concrete = Concrete(fck=30, gamma_c=1.5, name="C30/37")  # fck σε MPa, συντελεστής γc, όνομα

# --- Δημιουργία αντικειμένου χάλυβα ---
steel = Steel(fyk=313, gamma_s=1.15, E=200000, name="B500")  # fyk, συντελεστής γs, μέτρο ελαστικότητας, όνομα

# --- Δημιουργία ορθογωνικής διατομής ---
section = RectangularSection(
    width=0.25,   # πλάτος σε m
    height=0.25,  # ύψος σε m
    H=3.2,        # συνολικό ύψος m
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
    n_db=2,      # αριθμός ράβδων / ανά παρειά
    dbw=8,       # διάμετρος εγκάρσιων οπλισμών (mm)
    sw=0.2,      # βήμα εγκάρσιων οπλισνών (m)
    name="Beam_RC"
)

# --- Δημιουργία αντικειμένου FRP ---
frp = FRP(
    type='CFRP',  # τύπος FRP
    wj=3,         # πλάτος (cm)
    t_frp=0.26,   # πάχος (mm)
    E_frp=230000, # μέτρο ελαστικότητας (MPa)
    eju=0.015     # παραμόρφωση θραύσης
)

# --- Δημιουργία ελεγκτή FRP ---
check = FRPCheck(rc_section, frp, n_layers=1)  # n_layers = αριθμός στρώσεων FRP

# --- Υπολογισμός περίσφιγξης ---
results, fig = check.perisfiksi(
    bp=30,  # mm, απόσταση κατά μήκος της γωνίας
    dp=30,  # mm, απόσταση κατά μήκος της γωνίας
    r=10,   # mm, ακτίνα καμπυλότητας
    show_plot=True  # εμφανίζει το διάγραμμα σ-ε
)

# --- Εκτύπωση αποτελεσμάτων ---
print("Αποτελέσματα περίσφιγξης FRP:", results)
