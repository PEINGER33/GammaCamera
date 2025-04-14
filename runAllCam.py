import subprocess


# Chemin du script enfant (celui qui gère la simulation pour chaque angle)
script_enfant = "GammaCamera.py"
nbImages = 4

# Lancer la simulation pour chaque angle
for i in range(nbImages//2):
    angle = i*180/(nbImages//2)
    print(f"Lancement de la simulation pour l'angle {angle}° et {angle + 180}°")
    
    # Exécuter le script enfant en utilisant subprocess
    subprocess.run(["python", script_enfant, str(int(angle))])

print("Simulation terminée pour tous les angles.")

