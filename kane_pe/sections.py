import math
from .materials import Concrete, Steel,FRP, Material


# === Βασική κλάση Section ===
class Section:
    def __init__(self, name: str):
        self.name = name

    def area(self) -> float:
        raise NotImplementedError

    def inertia(self) -> float:
        raise NotImplementedError

    @property
    def section_modulus(self) -> float:
        raise NotImplementedError

    def __repr__(self):
        return f"<Section {self.name}>"


# === RectangularSection με Material ===
class RectangularSection(Section):
    def __init__(self, width: float, height: float,H:float, material: Material, name: str = "RectSection"):
        super().__init__(name)
        self.width = width
        self.height = height
        self.H=H
        self.material = material

    def area(self) -> float:
        return self.width * self.height
    
    def volume(self) -> float:
        return self.width * self.height*self.H

    def inertia(self) -> float:
        return (self.width * self.height ** 3) / 12

    @property
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    @property
    def centroid(self) -> tuple[float, float]:
        return (self.width / 2, self.height / 2)

    @property
    def aspect_ratio(self) -> float:
        return self.height / self.width

    @property
    def section_modulus(self) -> float:
        return self.inertia() / (self.height / 2)

    def bending_capacity(self) -> float:
        if hasattr(self.material, "fcd"):
            fcd = self.material.fcd
        elif hasattr(self.material, "fyd"):
            fcd = self.material.fyd
        else:
            raise ValueError("Το υλικό δεν έχει fcd ή fyd")
        return fcd * self.section_modulus

    def __repr__(self):
        return (f"<{self.name}: width={self.width} m, height={self.height} m, "
                f"area={self.area():.3f} m², inertia={self.inertia():.3f} m⁴, "
                f"W={self.section_modulus:.3f} m³, aspect_ratio={self.aspect_ratio:.2f}, "
                f"material={self.material.name}>")


# === ReinforcedConcreteSection γενικής μορφής ===
class ReinforcedConcreteSection:
    def __init__(self, section: RectangularSection, concrete: Concrete, steel: Steel,
                 cnom: float, db: float, n_db: int,
                 dbw: float, sw: float,
                 dbx: float, dby: float, n_dbx: int, n_dby: int,
                 name: str = "ReinfConcreteSection"):
        self.section = section
        self.concrete = concrete
        self.steel = steel
        self.cnom = cnom
        self.db = db          # διάμετρος κύριου οπλισμού
        self.n_db = n_db      # αριθμός κύριου οπλισμού
        self.dbw = dbw        # διάμετρος διαγώνιου οπλισμού
        self.sw = sw          # διάκενο εγκάρσιου οπλισμού
        self.dbx = dbx        # διάμετρος διαμήκων ράβδων Χ
        self.dby = dby        # διάμετρος διαμήκων ράβδων Υ
        self.n_dbx = n_dbx
        self.n_dby = n_dby
        self.name = name

    @property
    def As(self) -> float:
        """Συνολικό εμβαδόν κύριου οπλισμού (m²)"""
        return self.n_db * math.pi * (self.db / 2) ** 2

    @property
    def Asx(self) -> float:
        """Συνολικό εμβαδόν διαμήκων ράβδων (m²)"""
        return self.n_dbx * math.pi * (self.dbx / 2) ** 2 + self.n_dby * math.pi * (self.dby / 2) ** 2

    @property
    def Asw(self) -> float:
        """Εμβαδόν εγκάρσιου οπλισμού ανά μήκος (m²/m)"""
        return (self.dbw/2)**2  *math.pi 

    @property 
    def d1(self) -> float:
        """Αποτελεσματικό βάθος οπλισμού στην κορυφή (m)"""
        return self.cnom + (self.db / 2 + self.dbw ) / 1000
    
    @property 
    def d(self) -> float: 
        """Αποτελεσματικό βάθος οπλισμού στη βάση (m)""" 
        return self.section.height - self.d1 
    
    @property 
    def d_tonos(self) -> float: 
        """Υπολογισμός του ύψους του τόνου""" 
        return self.section.height - self.d 
    
    @property 
    def delta_tonos(self) -> float: 
        """Υπολογισμός της απόστασης του τόνου από την βάση"""
        return self.d_tonos / self.d
    
    @property 
    def r(self) -> float: 
        """Ποσοστό οπλισμού""" 
        return (self.As / (10000 * self.section.width * self.d) ) /100
    
    @property 
    def z(self) -> float: 
        """Υπολογισμός του μοχλοβραχίονα z""" 
        return self.d - self.d_tonos 
    
    @property 
    def rw(self) -> float: 
        """Υπολογισμός του συντελεστή rw""" 
        return ( self.Asw / (10000 * self.section.width * self.sw) ) /100
    
    @property
    def omega(self) -> float:
        """Υπολογισμός του συντελεστή ω"""
        return (self.As * self.steel.fyk) / (10000 * self.section.width * self.section.height * self.concrete.fck * 100)
    
    @property
    def omega_tonos(self) -> float:
        """Υπολογισμός του συντελεστή ω_τόνος"""
        return self.omega / 2
    
    @property 
    def rv(self) -> float: 
        """Ποσοστό οπλισμού""" 
        return self.Asx / (self.section.width * self.d)
    
    @property  
    def Ls(self) -> float: 
        """Υπολογισμός του μήκους Ls""" 
        return 0.5 * self.section.H
    
    @property
    def alfa(self) -> float:
        """Υπολογισμός του συντελεστή α"""
        return self.steel.E / self.concrete.E
    
    @property
    def Acc(self) -> float:
        """Υπολογισμός της επιφάνειας του σκυροδέματος"""
        return self.section.area()
    
    @property
    def Acc_netto(self) -> float:
        """Υπολογισμός της επιφάνειας του σκυροδέματος χωρίς οπλισμό"""
        return self.Acc() - self.As - self.Asx - self.Asw * self.Ls

    def __repr__(self):
        return (f"<{self.name}: section={self.section.name}, concrete={self.concrete.name}, "
                f"steel={self.steel.name}, As={self.As:.4f} m², Asw={self.Asw:.4f} m²/m, "
                f"cover={self.cnom} m, db={self.db} m, n_db={self.n_db}, "
                f"dbw={self.dbw} m, sw={self.sw} m, "
                f"dbx={self.dbx} m, dby={self.dby} m, n_dbx={self.n_dbx}, n_dby={self.n_dby}>"
                f", d1={self.d1:.3f} m, d={self.d:.3f} m, d_tonos={self.d_tonos:.3f} m, delta_tonos={self.delta_tonos:.3f}, z={self.z:.3f} m, steel_per={self.r:.4f}, rw={self.rw:.4f}, rv={self.rv:.4f}, Ls={self.Ls:.3f} m>"
                f", alfa={self.alfa:.3f}, E_s={self.steel.E} MPa, E_c={self.concrete.E} MPa>"
                )
