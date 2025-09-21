import matplotlib.pyplot as plt

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

# Παράδειγμα χρήσης
My = 50
thita_y = 0.01
thita_um = 0.03
plot_m_theta(My, thita_y, thita_um, damage_levels=["medium", "severe"])
