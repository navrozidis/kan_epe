import tkinter as tk
from tkinter import ttk
from kane_pe.materials import Concrete, Steel, FRP
from kane_pe.sections import RectangularSection, ReinforcedConcreteSection
from kane_pe.checks import SectionCheck, FRPCheck
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

matplotlib.style.use('seaborn-darkgrid')

class FRPGUIStyled(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KANEPE FRP & Section Check GUI")
        self.geometry("1000x700")
        self.configure(bg="#f5f5f5")

        # -------------------------
        # Παράμετροι με Default
        # -------------------------
        self.params = {
            "fck (MPa)": tk.DoubleVar(value=30),
            "fyk (MPa)": tk.DoubleVar(value=313),
            "bw (m)": tk.DoubleVar(value=0.25),
            "h (m)": tk.DoubleVar(value=0.25),
            "t_frp (mm)": tk.DoubleVar(value=0.26),
            "n_layers": tk.IntVar(value=1),
            "bp (mm)": tk.DoubleVar(value=30),
            "dp (mm)": tk.DoubleVar(value=30),
            "r (mm)": tk.DoubleVar(value=10),
        }

        # -------------------------
        # Frame για sliders
        # -------------------------
        slider_frame = tk.Frame(self, bg="#f5f5f5")
        slider_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        row = 0
        for key, var in self.params.items():
            label = tk.Label(slider_frame, text=key, bg="#f5f5f5", fg="#333", font=("Arial", 10, "bold"))
            label.grid(row=row, column=0, sticky="w", pady=4)
            if isinstance(var, tk.IntVar):
                slider = tk.Scale(slider_frame, from_=1, to=10, orient="horizontal", variable=var,
                                  command=self.update_plot, length=200, resolution=1, bg="#f5f5f5", troughcolor="#a2cffe")
            else:
                slider = tk.Scale(slider_frame, from_=0.1, to=500,  orient="horizontal", variable=var,
                                  command=self.update_plot, length=200, resolution=0.1, bg="#f5f5f5", troughcolor="#a2cffe")
            slider.grid(row=row, column=1, sticky="w", pady=4)
            row += 1

        # -------------------------
        # Canvas για Matplotlib
        # -------------------------
        self.fig, self.axs = plt.subplots(2, 1, figsize=(7,7))
        self.fig.tight_layout(pad=4.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=row, padx=10, pady=10)

        # Αρχικό plot
        self.update_plot()

    def update_plot(self, event=None):
        # ---- Ανάγνωση παραμέτρων ----
        vals = {k: v.get() for k, v in self.params.items()}
        fck = vals["fck (MPa)"]
        fyk = vals["fyk (MPa)"]
        bw = vals["bw (m)"]
        h = vals["h (m)"]
        t_frp = vals["t_frp (mm)"]
        n_layers = vals["n_layers"]
        bp = vals["bp (mm)"]
        dp = vals["dp (mm)"]
        r = vals["r (mm)"]

        # ---- Υλικά & Διατομή ----
        concrete = Concrete(fck=fck)
        steel = Steel(fyk=fyk)
        frp = FRP(type='CFRP', wj=3, t_frp=t_frp, E_frp=230000, eju=0.015)
        section = RectangularSection(width=bw, height=h, H=3.0, material=concrete)
        rc_section = ReinforcedConcreteSection(section=section, concrete=concrete, steel=steel,
                                               cnom=0.015, db=14, n_db=2, dbw=8, sw=0.2, name="Beam_RC",dbx=0, dby=0, n_dbx=0, n_dby=0  )

        # ---- Section Check ----
        checker = SectionCheck(rc_section)
        res = checker.calc_yield_strain(N=750)
        My = checker.calc_yield_moment(res['ry'], res['jy'])
        thita_y = checker.thita_y(res['ry'])
        thita_um, _ = checker.calc_failure_rotation(N=750, thita_y=thita_y, building_year=1985, lb=3, ravdos_type='leios')

        # ---- FRP Check ----
        check_frp = FRPCheck(rc_section, frp, n_layers=n_layers)
        frp_results, _ = check_frp.perisfiksi(bp=bp, dp=dp, r=r, show_plot=False)

        # ---- Καθαρισμός γραφημάτων ----
        for ax in self.axs:
            ax.clear()

        # ---- Σχεδίαση FRP σ-ε ----
        n_points = 50
        K = frp_results['K']
        fcc = frp_results['fcc']
        Lc = frp_results['Lc']

        ecc = 0.002 * (1 + 5*K)
        ecu_c = ecc + 0.4*Lc
        eps_parab = [ecc * i / (n_points - 1) for i in range(n_points)]
        sig_parab = [fcc * (e / ecc) * (2 - e / ecc) for e in eps_parab]
        eps_rect = [ecc + (ecu_c - ecc) * i / (n_points - 1) for i in range(n_points)]
        sig_rect = [fcc for _ in eps_rect]
        self.axs[0].plot(eps_parab + eps_rect, sig_parab + sig_rect, label='FRP', color='#1f77b4', linewidth=2)
        self.axs[0].set_title('Διάγραμμα σ-ε Σκυροδέματος', fontsize=12, fontweight='bold')
        self.axs[0].set_xlabel('Παραμόρφωση ε')
        self.axs[0].set_ylabel('Τάση σ (MPa)')
        self.axs[0].legend()
        self.axs[0].grid(True, linestyle='--', alpha=0.7)

        # ---- Σχεδίαση Ροπής – Στροφής ----
        self.axs[1].plot([0, thita_y, thita_um], [0, My, My], label='Χωρίς βλάβη', color='#ff7f0e', linewidth=2)
        self.axs[1].set_title('Διάγραμμα Ροπής – Στροφής', fontsize=12, fontweight='bold')
        self.axs[1].set_xlabel('Στροφή χορδής θ (rad)')
        self.axs[1].set_ylabel('Ροπή M (kNm)')
        self.axs[1].legend()
        self.axs[1].grid(True, linestyle='--', alpha=0.7)

        self.canvas.draw()


if __name__ == "__main__":
    app = FRPGUIStyled()
    app.mainloop()
