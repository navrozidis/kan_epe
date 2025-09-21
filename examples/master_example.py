from kan_epe.materials import Concrete, Steel, FRP
from kan_epe.sections import RectangularSection, ReinforcedConcreteSection
from kan_epe.checks import SectionCheck, FRPCheck
import matplotlib.pyplot as plt

# -------------------------------
# 1️ Δημιουργία Υλικών
# -------------------------------
concrete = Concrete(fck=30, gamma_c=1.5, name="C30/37")
steel = Steel(fyk=313, gamma_s=1.15, E=200000 , name="B500")
frp = FRP(type='CFRP', wj=3, t_frp=0.26, E_frp=230000, eju=0.015)

# -------------------------------
# 2️ Δημιουργία Διατομών
# -------------------------------
section = RectangularSection(width=0.25, height=0.25, H=3.2, material=concrete, name="BeamSection")

rc_section = ReinforcedConcreteSection(
    section=section, concrete=concrete, steel=steel,
    cnom=0.015, db=14, n_db=2, dbw=8, sw=0.2, name="Beam_RC"
)

print(rc_section)
print("Εμβαδόν σκυροδέματος:", rc_section.Acc, "m²")

# -------------------------------
# 3️ Έλεγχος Διατομής
# -------------------------------
checker = SectionCheck(rc_section)

res = checker.calc_yield_strain(N=750)
print("Παραμόρφωση διαρροής:", res)

My = checker.calc_yield_moment(res['ry'], res['jy'])
VMy = checker.calc_yield_shear(My)
thita_y = checker.thita_y(res['ry'])
K = checker.calc_stiffness(My, thita_y)

print("Ροπή διαρροής My:", My)
print("Δύναμη διαρροής VMy:", VMy)
print("Γωνία διαρροής θy:", thita_y)
print("Δυσκαμψία K:", K)

thita_um , m = checker.calc_failure_rotation(N=750, thita_y=thita_y, building_year=1985, lb=3 , ravdos_type='leios')
print("Θέση αστοχίας θu:", thita_um)
print("Συντελεστής μορφής m:", m)

# ------------------------------
# 4️ Έλεγχος FRP
# -------------------------------
check_frp = FRPCheck(rc_section, frp, n_layers=2)
frp_results, fig = check_frp.perisfiksi(bp=30, dp=30, r=10, show_plot=True)
print("Αποτελέσματα περίσφιγξης FRP:", frp_results)

# -------------------------------
# 5️ Διάγραμμα ροπής – στροφής
# -------------------------------
def plot_m_theta(My, thita_y, thita_um, damage_levels=None):
    plt.figure(figsize=(7,5))
    plt.plot([0, thita_y, thita_um], [0, My, My], label="Χωρίς βλάβη", linewidth=2)

    if damage_levels:
        factors = {"medium":0.75, "severe":0.5}
        colors = {"medium":"orange", "severe":"red"}
        for dmg in damage_levels:
            thita_um_red = thita_um * factors[dmg]
            plt.plot([0, thita_y, thita_um_red], [0, My, My],
                     label=f"Βλάβη: {dmg}", linestyle="--", color=colors[dmg])

    plt.xlabel("Στροφή χορδής θ (rad)")
    plt.ylabel("Ροπή M (kNm)")
    plt.title("Διάγραμμα Ροπής – Στροφής")
    plt.legend()
    plt.grid(True)
    plt.show()

plot_m_theta(My, thita_y, thita_um, damage_levels=["medium", "severe"])
