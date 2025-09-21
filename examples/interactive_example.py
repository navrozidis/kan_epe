from kane_pe.materials import Concrete, Steel, FRP
from kane_pe.sections import RectangularSection, ReinforcedConcreteSection
from kane_pe.checks import SectionCheck, FRPCheck
import matplotlib.pyplot as plt

# -------------------------------
# 1️ Εισαγωγή παραμέτρων από χρήστη
# -------------------------------
fck = float(input("Δώσε fck σκυροδέματος [MPa]: "))
fyk = float(input("Δώσε fyk χάλυβα [MPa]: "))
bw = float(input("Πλάτος δοκού [m]: "))
h = float(input("Ύψος δοκού [m]: "))
t_frp = float(input("Πάχος FRP [mm]: "))
n_layers = int(input("Αριθμός στρώσεων FRP: "))
bp = float(input("Δώσε bp [mm]: "))
dp = float(input("Δώσε dp [mm]: "))
r = float(input("Δώσε ακτίνα καμπυλότητας FRP [mm]: "))

# -------------------------------
# 2️ Δημιουργία Υλικών & Διατομής
# -------------------------------
concrete = Concrete(fck=fck, name="UserConcrete")
steel = Steel(fyk=fyk, name="UserSteel")
frp = FRP(type='CFRP', wj=3, t_frp=t_frp, E_frp=230000, eju=0.015)

section = RectangularSection(width=bw, height=h, H=3.0, material=concrete, name="UserSection")
rc_section = ReinforcedConcreteSection(
    section=section, concrete=concrete, steel=steel,
    cnom=0.015, db=14, n_db=2, dbw=8, sw=0.2, name="UserRC"
)

# -------------------------------
# 3️ Υπολογισμοί Section
# -------------------------------
checker = SectionCheck(rc_section)
res = checker.calc_yield_strain(N=750)
My = checker.calc_yield_moment(res['ry'], res['jy'])
VMy = checker.calc_yield_shear(My)
thita_y = checker.thita_y(res['ry'])
K = checker.calc_stiffness(My, thita_y)
thita_um, m = checker.calc_failure_rotation(N=750, thita_y=thita_y, building_year=1985, lb=3, ravdos_type='leios')

print(f"\nΑποτελέσματα Section:")
print(f"My = {My:.2f} kNm, VMy = {VMy:.2f} kN")
print(f"θy = {thita_y:.4f} rad, θu = {thita_um:.4f} rad, K = {K:.2f} kNm/rad")

# -------------------------------
# 4️ Υπολογισμοί FRP
# -------------------------------
check_frp = FRPCheck(rc_section, frp, n_layers=n_layers)
frp_results, fig = check_frp.perisfiksi(bp=bp, dp=dp, r=r, show_plot=True)
print("\nΑποτελέσματα FRP:")
for key, val in frp_results.items():
    print(f"{key}: {val}")

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

plot_m_theta(My, thita_y, thita_um, damage_levels=["medium","severe"])
