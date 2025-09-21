"""
materials.py
-------------
Ορισμός υλικών (σκυρόδεμα, χάλυβας, FRP) για χρήση σε ελέγχους ΚΑΝ.ΕΠΕ.
Χρησιμοποιεί αρχές OOP (inheritance, polymorphism).
"""

from abc import ABC, abstractmethod


# === Βασική Αφηρημένη Κλάση Υλικού ===
class Material(ABC):
    """Αφηρημένη κλάση για όλα τα υλικά"""

    def __init__(self, name: str, gamma: float = 1.0):
        """
        Parameters:
            name (str): Όνομα υλικού
            gamma (float): Συντελεστής μερικής ασφάλειας
        """
        self.name = name
        self.gamma = gamma

    @abstractmethod
    def design_strength(self) -> float:
        """Υπολογισμός αντοχής σχεδιασμού"""
        pass

    def __repr__(self):
        return f"<Material {self.name}, γ={self.gamma}>"


# === Σκυρόδεμα ===
class Concrete(Material):
    def __init__(self, fck: float, gamma_c: float = 1.5, name: str = "Concrete"):
        """
        Parameters:
            fck (float): Χαρακτηριστική αντοχή σε θλίψη (MPa)
            gamma_c (float): Συντελεστής μερικής ασφάλειας σκυροδέματος
            name (str): Όνομα υλικού
        """
        super().__init__(name, gamma_c)
        self.fck = fck

    # --- Σχεδιαστικές αντοχές ---
    @property
    def fcd(self) -> float:
        """Σχεδιαστική αντοχή σε θλίψη (MPa)"""
        return self.fck / self.gamma

    @property
    def fctm(self) -> float:
        """Μέση αντοχή σε εφελκυσμό (MPa)"""
        return 0.3 * self.fck ** (2/3)

    @property
    def fctd(self) -> float:
        """Σχεδιαστική αντοχή σε εφελκυσμό (MPa)"""
        return self.fctm / self.gamma

    @property
    def fcb(self) -> float:
        """Αντοχή σε κάμψη (MPa)"""
        return 0.7 * self.fck ** (2/3)

    @property
    def fcm(self) -> float:
        """Μέση αντοχή σε θλίψη (MPa)"""
        return self.fck + 8  # Τυπική σχέση

    # --- Μέτρο ελαστικότητας ---
    @property
    def E(self) -> float:
        """
        Μέτρο ελαστικότητας σκυροδέματος (MPa)
        Υπολογισμός σύμφωνα με EC2: Ecm = 22*(fck/10)^0.3 GPa
        """
        Ecm = 22 * (self.fck / 10) ** 0.3  # GPa
        return Ecm * 1000  # Μετατροπή σε MPa

    # --- Φυσικές ιδιότητες ---
    @property
    def density(self) -> float:
        """Πυκνότητα σκυροδέματος (kg/m³)"""
        return 2500  # Τυπική τιμή

    @property
    def thermal_conductivity(self) -> float:
        """Συντελεστής θερμικής αγωγιμότητας (W/mK)"""
        return 1.7  # Τυπική τιμή

    # --- Μέθοδοι ---
    def design_strength(self) -> float:
        return self.fcd

    def weight(self, volume: float) -> float:
        """Υπολογισμός βάρους σκυροδέματος (kg)"""
        return self.density * volume

    @staticmethod
    def concrete_class(fck: float) -> str:
        """Κατηγορία σκυροδέματος βάσει fck"""
        if fck <= 20:
            return "C20/25"
        elif fck <= 25:
            return "C25/30"
        elif fck <= 30:
            return "C30/37"
        elif fck <= 35:
            return "C35/45"
        else:
            return "C40/50"

    # --- Αναπαράσταση αντικειμένου ---
    def __repr__(self):
        return (f"<Concrete {self.concrete_class(self.fck)}: fck={self.fck} MPa, "
                f"fcd={self.fcd:.2f} MPa, fctd={self.fctd:.2f} MPa, "
                f"fcb={self.fcb:.2f} MPa, E={self.E:.0f} MPa, density={self.density} kg/m³>")


# === Χάλυβας ===
class Steel(Material):
    def __init__(self, fyk: float, gamma_s: float = 1.15, E: float = 210000, name: str = "Steel"):
        """
        Parameters:
            fyk (float): Χαρακτηριστική αντοχή διαρροής (MPa)
            gamma_s (float): Συντελεστής μερικής ασφάλειας χάλυβα
            E (float): Μέτρο ελαστικότητας χάλυβα (MPa)
            name (str): Όνομα υλικού
        """
        super().__init__(name, gamma_s)
        self.fyk = fyk
        self.E = E  # Μέτρο ελαστικότητας σε MPa

    # --- Σχεδιαστική αντοχή ---
    @property
    def fyd(self) -> float:
        """Σχεδιαστική αντοχή χάλυβα (MPa)"""
        return self.fyk / self.gamma

    # --- Υπολογισμός ορίου διαρροής σε εφελκυσμό ---
    def yield_stress(self, strain: float) -> float:
        """
        Εκτιμά την τάση χάλυβα για δοσμένο strain
        (γραμμική περιοχή: stress = E * strain)
        Parameters:
            strain (float): παραμόρφωση (π.χ. 0.002)
        """
        stress = self.E * strain
        return min(stress, self.fyd)

    # --- Μέθοδος σχεδιαστικής αντοχής ---
    def design_strength(self) -> float:
        return self.fyd

    # --- Αναπαράσταση αντικειμένου ---
    def __repr__(self):
        return (f"<Steel fyk={self.fyk} MPa, fyd={self.fyd:.2f} MPa, "
                f"E={self.E} MPa>")



# === FRP (Ινοπλισμένα Πολυμερή) ===
class FRP(Material):
    def __init__(self, type:str, wj:float ,t_frp: float, E_frp: float, eju:float,  gamma_frp: float = 1.2, name: str = "FRP"):
        """
        Parameters:
            f_frp (float): Αντοχή FRP (MPa)
            t_frp (float): Πάχος ελάσματος (mm)
            gamma_frp (float): Συντελεστής μερικής ασφάλειας FRP
        """
        super().__init__(name, gamma_frp)
        self.type= type
        self.wj= wj
        self.t_frp = t_frp
        self.E_frp = E_frp
        self.eju = eju
    # --- Σχεδιαστική αντοχή ---
    @property
    def design_strength(self) -> float:
        return self.E_frp / self.gamma

    def __repr__(self):
        return f"<FRP {self.type}: t_frp={self.t_frp} mm, E_frp={self.E_frp} MPa, eju={self.eju}, γ={self.gamma}>"


