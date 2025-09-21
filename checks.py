# kane_pe/checks.py
from .sections import Section, RectangularSection, ReinforcedConcreteSection
from .materials import Concrete, Steel, FRP, Material
import math
import matplotlib.pyplot as plt


# === Βασική κλάση ελέγχων ===
class SectionCheck:
    """Βασική κλάση για ελέγχους διατομών"""
    
    def __init__(self,  rcsection: ReinforcedConcreteSection):
        self.rcsection = rcsection

    # ---------------------------------
    # 7.2.1 Έλεγχος παράθεσης (lap length)
    # ---------------------------------
    def check_lap_length(self, lb: float, ravdos_type: str = "nevroseis") -> tuple[float, float, str]:
        """
        Parameters:
            lb (float): Παρεχόμενο μήκος παράθεσης (mm)
            ravdos_type (str): "nevroseis" ή "loipa"
        
        Returns:
            tuple: (πραγματική αντοχή χάλυβα fy_eff, ελάχιστο απαιτούμενο μήκος lbmin, μήνυμα αξιολόγησης)
        """
        fy = self.rcsection.steel.fyk  # Αντοχή χάλυβα
        db = self.rcsection.db         # Διάμετρος ράβδου
        fck = self.rcsection.concrete.fck  # Αντοχή σκυροδέματος

        # Ελάχιστο απαιτούμενο μήκος (ΚΑΝΕΠΕ 7.2.1)
        lbmin = 0.3 * db * fy / fck
        message = "✔ Καμία παρατήρηση"

        if ravdos_type == "nevroseis":
            if lb < lbmin:
                fy_eff = fy * lb / lbmin  # μείωση αντοχής
                message = "⚠️ Ανεπαρκής υπερκάλυψη (ΚΑΝΕΠΕ 7.2.1δ)"
            else:
                fy_eff = fy
        else:
            fy_eff = fy
            if lb >= 15 * db:
                message = "✔ Επαρκής υπερκάλυψη με ≥15db"

        return fy_eff, lbmin, message

    # ---------------------------------
    # 7.2.2 Παραμόρφωση διαρροής
    # ---------------------------------
    def calc_yield_strain(self,N:float) -> dict:
        """
        Υπολογισμός παραμόρφωσης διαρροής χάλυβα (ΚΑΝΕΠΕ 7.2.2)
        Parameters:
            N (float): Φορτίο αξονικής δύναμης (kN)
        Returns:
            dict: Περιέχει d, d_tonos, delta_tonos, ry, jy, Ec, alfa, Acc, r, r_tonos, rv, rl
        """
        fc = self.rcsection.concrete.fck  # MPa
        fy = self.rcsection.steel.fyk      # MPa
        Es = self.rcsection.steel.E        # MPa
        Ec = self.rcsection.concrete.E      # MPa
        bw = self.rcsection.section.width   # m
        r = self.rcsection.r          # ποσοστό οπλισμού
        r_tonos = r     # ποσοστό οπλισμού τόνου
        rv = self.rcsection.rv          # ποσοστό οπλισμού εγκάρσι
        N = N  # kN
        # Γεωμετρία
        d = self.rcsection.d 
        
        
        d_tonos = self.rcsection.d_tonos  # mm
        delta_tonos = self.rcsection.delta_tonos  # mm
        alfa = self.rcsection.alfa  # m
        Acc = self.rcsection.section.area()  # m²

        # Διαρροή χάλυβα
        As = r + r_tonos + rv + N / (1000 * bw * d * fy)
        Bs = r + r_tonos * delta_tonos + 0.5 * rv * (1 + delta_tonos) + N / (1000 * bw * d * fy)
        jy_s = math.sqrt((alfa ** 2) * (As ** 2) + (2 * alfa * Bs)) - alfa * As
        rys = fy / (Es * (1 - jy_s) * d)

        # Διαρροή σκυροδέματος
        Ac = r + r_tonos + rv - N / (1000 * 1.8 * alfa * bw * d * fc)
        Bc = r + r_tonos * delta_tonos + 0.5 * rv * (1 + delta_tonos)
        jy_c = math.sqrt((alfa ** 2) * (Ac ** 2) + (2 * alfa * Bc)) - alfa * Ac
        ryc = (1.8 * fc) / (Ec  * jy_c * d)

        ry = min(rys, ryc)
        jy = jy_s if ry == rys else jy_c

        
        return {
            "d": d,
            "d_tonos": d_tonos,
            "delta_tonos": delta_tonos,
            "ry": ry,
            "jy": jy,
            "Ec": Ec,
            "alfa": alfa,
            "Acc": Acc,
            "r": r,
            "r_tonos": r_tonos,
            "rv": rv,
            "rl": As
        }
    # ---------------------------------
    # 7.2.3 Υπολογισμός ροπής & δυσκαμψίας
    # ---------------------------------
    def calc_yield_moment(self, ry, jy) -> float:
        
        bw = self.rcsection.section.width   # m
        d = self.rcsection.d
        ry = ry
        Ec = self.rcsection.concrete.E      # MPa
        jy = jy
        delta_tonos = self.rcsection.delta_tonos  # mm
        r = self.rcsection.r          # ποσοστό οπλισμού
        r_tonos = r     # ποσοστό οπλισμού τόνου
        rv = self.rcsection.rv          # ποσοστό οπλισμού εγκάρσι
        Es = self.rcsection.steel.E        # MPa
        
        My = (1000 * bw * (d ** 3) * ry) * (
            (0.5 * Ec * jy ** 2) * (0.5 * (1 + delta_tonos) - jy / 3)
            + ((1 - jy) * r + (jy - delta_tonos) * r_tonos + rv * (1 - delta_tonos) / 6)
            * (1 - delta_tonos) * Es  / 2
        )
        return My
    
    def calc_yield_shear(self, My:float) -> float:
        
        VMy = My / self.rcsection.Ls
        return VMy
    
    def thita_y(self, ry:float) -> float:
        """Υπολογισμός γωνίας διαρροής"""
        Ls = self.rcsection.Ls  # m
        hw = self.rcsection.section.height  # m
        
        thita_y = ry  * ((Ls + 1) / 3) + 0.0014 * (1 + 1.5 * hw / Ls)
        return thita_y

    def calc_stiffness(self, My:float, thita_y:float) -> float:
        return My * self.rcsection.Ls / (3 * thita_y)


    def __repr__(self):
        return f"<SectionCheck section={self.rcsection.section.name}>"

    
    # ---------------------------------
    # 7.2.4 Παραμορφώσεις αστοχίας
    # ---------------------------------
    def calc_failure_rotation(self, N, thita_y, building_year:int, lb:int , ravdos_type:str) -> tuple[float, float]:

        Asw = self.rcsection.Asw  # m²/m
        print("AAAAAAAAAAAAAA",Asw)
        rs = self.rcsection.rw  # ποσοστό οπλισμού
        print("KKKKKKKKKKKKKKKKK",rs)
        alfa = self.rcsection.alfa  # m
        omega = self.rcsection.omega  # ποσοστό οπλισμού
        omega_tonos = self.rcsection.omega_tonos  # ποσοστό οπλισμού τ
        bw = self.rcsection.section.width   # m
        hw = self.rcsection.section.height  # m
        fc = self.rcsection.concrete.fck  # MPa
        db = self.rcsection.db         # Διάμετρος ράβδου
        fyw = self.rcsection.steel.fyk      # MPa
        v = N/ (bw * hw * fc * 1000)
        rd = 0
        

        thita_um = 0.016 * (0.3 ** v) * (
            ((max(0.01, omega_tonos) * fc) / max(0.01, (omega - omega_tonos))) ** 0.225
        ) * (alfa ** 0.35) * (25 ** (alfa * rs * fyw / fc)) * (1.25 ** (100 * rd))

        if building_year < 1985:
            if ravdos_type == "nevroseis":
                thita_um = thita_um / 1.2
            else:
                if lb >= 15 * db:
                    thita_um *= (60 + min(40, lb / db)) / 120

        m_thita = thita_um / thita_y
        return thita_um, m_thita


class FRPCheck:
    """
    Έλεγχοι περίσφιγξης σκυροδέματος με FRP σύμφωνα με ΚΑΝΕΠΕ 6.2.3
    """

    def __init__(self, rcsection: ReinforcedConcreteSection, frp: FRP, n_layers: int = 1):
        """
        Parameters:
            rcsection (ReinforcedConcreteSection): Η διατομή οπλισμένου σκυροδέματος
            frp (FRP): Το υλικό FRP
            n_layers (int): Αριθμός στρώσεων FRP (default = 1)
        """
        self.rcsection = rcsection
        self.frp = frp
        self.n_layers = n_layers

    def perisfiksi(self, bp: float, dp: float, r: float, show_plot: bool = True) -> dict:
        """
        Υπολογισμός του συντελεστή K και των παραμέτρων περίσφιγξης
        """

        # --- Δεδομένα FRP ---
        t = self.frp.t_frp  /1000    # πάχος FRP (m)
        E = self.frp.E_frp          # μέτρο ελαστικότητας FRP (MPa)
        eju = self.frp.eju      # παραμόρφωση θραύσης FRP

        # --- Δεδομένα διατομής ---
        fc = self.rcsection.concrete.fck    # MPa

        # --- Μετατροπή σε m ---
        bw_m = self.rcsection.section.width #m 
        h_m = self.rcsection.section.height #m
        bp_m = bp / 1000 #m
        dp_m = dp / 1000 #m
        r = r / 1000 #m

        # --- Συντελεστής αποδοτικότητας λόγω στρογγύλευσης ---
        A_C = bw_m * h_m
        beta = (2 * bp_m) / bw_m
        gamma = (2 * dp_m) / h_m
        alpha_n = 1 - (1 / (3 * A_C)) * ((bw_m**2) * (1 - beta)**2 + (h_m**2) * (1 - gamma)**2)
        alpha_s = 1.0
        alpha_eff = alpha_n  * alpha_s

        # --- Συντελεστής μεγάλου πλήθους στρώσεων ---
        if self.n_layers >= 4:
            psi = max(self.n_layers ** (-0.25), 3 / self.n_layers)
        else:
            psi = 1.0

        # --- Μείωση παραμόρφωσης λόγω ακμών ---
        eo = t / (2 * r)
        ejures = eju - eo
        fjures = E * ejures
        fju = fjures * psi
        print(f"fju: {fju}")
        print(f"ejures: {ejures}")
        print(f"psi: {psi}")
        print(f"eo: {eo}")
        # --- Γεωμετρικό ποσοστό εγκάρσιου οπλισμού ---
        rho_sx = 2 * t / bw_m
        L = alpha_eff * rho_sx * fju / fc
        K = 3.5 * L ** 0.75

        fcc_new = fc * (1 + K)
        Lc = alpha_eff * rho_sx * fju / fcc_new

        # --- Δημιουργία διαγράμματος ---
        fig, ax = self.plot_FRP_stress_strain(Lc, fcc_new, K, fc, show=show_plot)

        results = {
            "K": K,
            "alpha_eff": alpha_eff,
            "psi": psi,
            "ejures": ejures,
            "fju": fju,
            "rho_sx": rho_sx,
            "fcc": fcc_new,
            "Lc": Lc,
            "fc": fc,
            "beta": beta,
            "gamma": gamma,
        }

        return results, fig

    def plot_FRP_stress_strain(self, Lc: float, fcc: float, K: float, fc: float, show: bool = False):
        """
        Παραβολικό-ορθογωνικό διάγραμμα σ-ε για FRP + καμπύλη απερίσφιγκτου σκυροδέματος
        """
        fig, ax = plt.subplots()

        n_points = 50
        ecc = 0.002 * (1 + 5 * K)
        ecu_c = ecc + 0.4 * Lc

        # --- Καμπύλη περισφιγμένου ---
        eps_parab = [ecc * i / (n_points - 1) for i in range(n_points)]
        sig_parab = [fcc * (e / ecc) * (2 - e / ecc) for e in eps_parab]

        eps_rect = [ecc + (ecu_c - ecc) * i / (n_points - 1) for i in range(n_points)]
        sig_rect = [fcc for _ in eps_rect]

        eps_conf = eps_parab + eps_rect
        sig_conf = sig_parab + sig_rect

        ax.plot(eps_conf, sig_conf, label=f"Περισφιγμένο (fcc={fcc:.1f} MPa)")

        # --- Απερίσφικτο σκυρόδεμα (χωρίς FRP) ---
        if fc is not None:
            ecc_unconf = 0.002  # τυπική παραμόρφωση στο fc
            ecu_unconf = 0.0035 # τελική παραμόρφωση για μη περισφιγμένο

            eps_parab_u = [ecc_unconf * i / (n_points - 1) for i in range(n_points)]
            sig_parab_u = [fc * (e / ecc_unconf) * (2 - e / ecc_unconf) for e in eps_parab_u]

            eps_rect_u = [ecc_unconf + (ecu_unconf - ecc_unconf) * i / (n_points - 1) for i in range(n_points)]
            sig_rect_u = [fc for _ in eps_rect_u]

            eps_unconf = eps_parab_u + eps_rect_u
            sig_unconf = sig_parab_u + sig_rect_u

            ax.plot(eps_unconf, sig_unconf, '--', label='Απερίσφικτο σκυρόδεμα σ-ε', color='red')

        # --- Format ---
        ax.set_xlabel("Παραμόρφωση ε")
        ax.set_ylabel("Τάση σ (MPa)")
        ax.set_title("Διάγραμμα σ-ε Σκυροδέματος")
        ax.grid(True)
        ax.legend()

        if show:
            plt.show()

        return fig, ax
    
    # === Βοηθητικές συναρτήσεις ===
    def cot(self,x):
        """Επιστρέφει την cotangent της γωνίας x σε radians"""
        if math.isclose(math.tan(x), 0.0):
            return float('inf')  # αποφυγή διαίρεσης με 0
        return 1 / math.tan(x)

    def bhta_factor(self,frp_type, wj, sj, a):
        """Υπολογισμός του bhta_w ανάλογα με τον τύπο FRP"""
        if frp_type == "synexes":
            return math.sqrt(2)/2
        else:
            return math.sqrt((2 - wj/(sj*math.sin(a))) / (1 + wj / (sj*math.sin(a))))

    def psi_factor(self,n_FRP):
        """Συντελεστής μεγάλου πλήθους στρώσεων"""
        if n_FRP >= 4:
            return max(n_FRP ** (-0.25), 3 / n_FRP)
        else:
            return 1.0

    def kv_factor(self,l):
        """Συντελεστής kv"""
        kv = 0.4 + 0.25 * l
        return min(kv, 0.65)

    def bl_factor(self,l):
        """Συντελεστής bl"""
        return l * (2 - l) if l <= 1 else 1

    def active_height(self,d):
        """Ενεργό ύψος της ενίσχυσης για τέμνουσα"""
        return 2/3 * d * 1000  # σε mm

    def compute_shear(self, sj: float, thita: float = math.radians(45), 
                  a: float = math.radians(90), giop: float = 1.2, n_FRP: int = None) -> dict:
    
        """
        Υπολογισμός σχεδιαστικής τέμνουσας και κρίσιμων παραμέτρων FRP για περίσφιγξη.

        Returns:
            dict: περιέχει όλα τα ενδιάμεσα αποτελέσματα και την τελική σχεδιαστική τέμνουσα VRds_tot
        """
        # Δεδομένα FRP
        tj = self.frp.t_frp    # mm
        wj = self.frp.wj    # mm
        
        Ej = self.frp.E_frp    # MPa
        eju = self.frp.eju
        frp_type = self.frp.type
        if n_FRP is None:
            n_FRP = self.n_layers
        # Δεδομένα διατομής
        bw = self.rcsection.section.width    # m
        d = self.rcsection.d    # m
        fctm = self.rcsection.concrete.fctm  # MPa

        results = {}

        # Επιφάνεια εξωτερικού οπλισμού (cm^2)
        Aj = tj * wj * 10
        results['Aj'] = Aj

        # Ενεργό ύψος ενίσχυσης (mm)
        hjef = 2/3 * d * 1000
        results['hjef'] = hjef

        # Συντελεστής μεγάλου πλήθους στρώσεων
        psi = self.psi_factor(n_FRP)
        results['psi'] = psi

        # Μέγιστη παραμόρφωση
        ejmax = min(eju * psi, 0.015)
        results['ejmax'] = ejmax

        # Υπολογισμοί σχετικοί με μήκος και kv
        Le = math.sqrt(Ej * tj / (2 * fctm))
        l = hjef / Le
        kv = self.kv_factor(l)
        results['l'] = l
        results['kv'] = kv

        ejcrit = kv * ejmax
        results['ejcrit'] = ejcrit

        # Τάση FRP
        fjk = Ej * ejcrit
        results['fjk'] = fjk

        sjd_same = fjk / giop
        results['sjd_same'] = sjd_same

        # Διόρθωση tj αν n_FRP > 1
        tj_adj = psi * n_FRP * tj if n_FRP > 1 else tj
        results['tj_adj'] = tj_adj

        # Συντελεστής bhta
        bhta_w = self.bhta_factor(frp_type, wj, sj, a)
        results['bhta_w'] = bhta_w

        # Συντελεστής bl
        bl = self.bl_factor(l)
        results['bl'] = bl

        # Τελικός συντελεστής b
        b = bhta_w * bl
        results['b'] = b

        # Μέγιστη απόσταση FRP
        sjmax = b * fctm * Le / tj_adj
        results['sjmax'] = sjmax

        sjcrit = kv * sjmax
        results['sjcrit'] = sjcrit

        sjd_apokollisi = sjcrit / giop
        results['sjd_apokollisi'] = sjd_apokollisi

        sjd = min(sjd_same, sjcrit)
        results['sjd'] = sjd

        # Γεωμετρικό ποσοστό οπλισμού
        rj = 2 * Aj / (10000 * sj * bw * math.sin(a))
        results['rj'] = rj

        # Τέμνουσα
        if math.isclose(thita, math.radians(45)) and math.isclose(a, math.radians(90)):
            Vjd = sjd * rj * bw * hjef
        else:
            Vjd = sjd * rj * bw * hjef * (self.cot(thita) + self.cot(a)) * math.sin(a)**2
        results['Vjd'] = Vjd

        # Τέμνουσα από συνδετήρες
        VRds_o = 2
        results['VRds_o'] = VRds_o

        # Συνολική σχεδιαστική τέμνουσα
        VRds_tot = VRds_o + Vjd
        results['VRds_tot'] = VRds_tot

        return results



    def __repr__(self):
        return f"<FRPCheck section={self.rcsection.section.name}, frp={self.frp.name}, n_layers={self.n_layers}>"

