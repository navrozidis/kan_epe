from kane_pe.materials import Concrete

# Δημιουργία αντικειμένου σκυροδέματος
concrete = Concrete(fck=30, gamma_c=1.5, name="C30/37")

print("Σχεδιαστική αντοχή σε θλίψη (fcd):", concrete.design_strength(), "MPa")
print("Σχεδιαστική αντοχή σε εφελκυσμό (fctd):", concrete.fctd, "MPa")
print("Μέτρο ελαστικότητας (E):", concrete.E, "MPa")

# Υπολογισμός βάρους
volume = 2  # m³
weight = concrete.weight(volume)
print(f"Βάρος σκυροδέματος για όγκο {volume} m³: {weight} kg")
