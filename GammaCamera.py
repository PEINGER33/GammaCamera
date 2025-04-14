import opengate as gate
import math
import opengate.contrib.phantoms.nemaiec as gate_iec
import numpy as np

import sys


# Définition des unités
cm = gate.g4_units.cm
mm = gate.g4_units.mm
keV = gate.g4_units.keV
gcm3 = gate.g4_units.g / cm**3
Bq = gate.g4_units.Bq
mL = gate.g4_units.cm3
BqmL = Bq / mL

# Physique de la camera

def newCamera(nbTete):
    camera = []
    for i in range(nbTete):
        camera.append(newTete(i+1))
    for i in range(nbTete):
        RotCircOy(camera[i], i*360/nbTete)
    return camera

def newTete(index):
    
    tete = []

    # Création du collimateur (en plomb)
    tete.append(newCollimator(index))


    # Création du cristal scintillant (NaI)
    tete.append(newCrystal(index))

    # Création du guide de lumière (Quartz)
    tete.append(newLightGuide(index))
    
    # Création des tubes photomultiplicateurs (PMT)
    tete.append(newPMTs(index))

    return tete

def newCollimator(index):
    name = f"collimator_{index}"  # Nom unique
    # Création du collimateur (en plomb)
    collimator = sim.add_volume("Box", name)
    #collimator.material = "G4_AIR"
    collimator.material = "Lead"
    collimator.size = [54 * cm, 40 * cm, 5.8 * cm]
    collimator.translation = [0, 0, distanceCam]  # Position du collimateur
    collimator.color = [0.5, 0.5, 0.5, 1]  # Gris
    addCollimatorHoles(collimator)
    return collimator

def addCollimatorHoles(collimator):
    hole_length = 58 * mm
    hole_diameter = 3.0 * mm
    hole_radius = hole_diameter / 2
    septal_thickness = 1.05 * mm
    spacing = hole_diameter + septal_thickness

    # Taille du collimateur
    colli_x, colli_y, _ = collimator.size

    # On laisse une marge pour éviter les overlaps sur les bords (2 * spacing)
    margin = 2 * spacing
    usable_x = colli_x - margin
    usable_y = colli_y - margin

    # Nombre de trous calculé avec marge
    n_holes_x = int(usable_x / spacing)
    n_holes_y = int(usable_y / spacing)

    for i in range(n_holes_x):
        for j in range(n_holes_y):
            offset = 0.5 * spacing if j % 2 == 1 else 0.0
            x = (i - n_holes_x / 2) * spacing + offset
            y = (j - n_holes_y / 2) * spacing
            z = 0

            # Vérification que le trou reste à l’intérieur
            if abs(x) + hole_radius >= colli_x / 2 or abs(y) + hole_radius >= colli_y / 2:
                continue  # Ne pas créer le trou trop proche du bord

            hole = sim.add_volume("Tubs", f"hole_{collimator.name}_{i}_{j}")
            hole.mother = collimator.name
            hole.rmin = 0
            hole.rmax = hole_radius
            hole.dz = hole_length / 2
            hole.translation = [x, y, z]
            hole.material = "G4_AIR"
            hole.color = [0.8, 0.8, 1, 0.3]

def newCrystal(index):
    name = f"crystal_{index}"  # Nom unique
    # Création du cristal scintillant (NaI)
    crystal = sim.add_volume("Box", name)
    crystal.material = "NaI"
    crystal.size = [54 * cm, 40 * cm, 1.59 * cm]
    crystal.translation = [0, 0, distanceCam + 3.695 * cm]  # derrière le colimateur
    crystal.color = [1, 0, 0, 1]  # Rouge
    return crystal

def newLightGuide(index):
    name = f"lightGuide_{index}"  # Nom unique
    # Création du guide de lumière (Quartz)
    light_guide = sim.add_volume("Box", name)
    light_guide.material = "Quartz"
    light_guide.size = [54 * cm, 40 * cm, 0.5 * cm]
    light_guide.translation = [0, 0, distanceCam + 4.74 * cm]  # Derrière le cristal
    light_guide.color = [0, 1, 1, 0.5]  # Cyan transparent
    return light_guide

def newPMTs(index):
    pmts = []
    pmt_positions = [
        [-18 * cm, -12 * cm],  # PMT_1 coin bas gauche
        [18 * cm, 12 * cm],    # PMT_2 coin haut droit
        [-18 * cm, 12 * cm],   # PMT_3 coin haut gauche
        [18 * cm, -12 * cm]    # PMT_4 coin bas droit
        ]
    z_pmt = distanceCam + 6.49 * cm
    for i, (x, y) in enumerate(pmt_positions, start=1):
        trans_local = [x, y, z_pmt]
        pmt = sim.add_volume("Box", f"PMT_{i+4*(index-1)}")
        pmt.material = "G4_AIR"
        pmt.size = [8 * cm, 8 * cm, 3 * cm]
        pmt.translation = trans_local  # Derrière le guide
        pmt.color = [1, 1, 0, 1]
        pmts.append(pmt)
    return pmts

# Physique source (phantom)

def phantom():
    # Ajout du phantom
    iec_phantom = gate_iec.add_iec_phantom(sim, 'iec_phantom')
    
    # Configuration sphères chaudes & background froid
    # activities = [100 * BqmL, 100 * BqmL, 100 * BqmL, 100 * BqmL, 100 * BqmL, 100 * BqmL]
    # iec_source = gate_iec.add_spheres_sources(sim, 'iec_phantom', 'iec_source', 'all', activities)
    # iec_bg_source = gate_iec.add_background_source(sim, 'iec_phantom', 'iec_bg_source', 0.01 * BqmL)
    
    # Aucune activité dans les sphères = sphères froides
    activities = [0.0 * BqmL] * 6
    iec_source = gate_iec.add_spheres_sources(sim, 'iec_phantom', 'iec_source', 'all', activities)
    iec_bg_source = gate_iec.add_background_source(sim, 'iec_phantom', 'iec_bg_source', 1000 * BqmL)
    return iec_phantom    

# Mise en mouvement

def translatVol(volume, x, y, z):
    if isinstance(volume, list): # Si volume est un parent
        for elt in volume:
            translatVol(elt, x, y, z)
    else:
        volume.translation = [volume.translation[0] + x, volume.translation[1] + y, volume.translation[2] + z]
        
def SymVolOxy(volume):
    if isinstance(volume, list): # Si volume est un parent
        for elt in volume:
            SymVolOxy(elt)
    else:
        volume.translation = [volume.translation[0] , volume.translation[1] , -volume.translation[2]]

def RotCircOy(volume, angle): # angle en degre
    if isinstance(volume, list): # Si volume est un parent
        for elt in volume:
            RotCircOy(elt, angle)
    else:
        teta = angle * math.pi / 180
        rotation_matrix = np.array([
            [ math.cos(teta), 0, math.sin(teta)],
            [ 0             , 1,              0],
            [-math.sin(teta), 0, math.cos(teta)]
            ])
        
        # Récupération des coordonnées actuelles
        x_old, y_old, z_old = volume.translation

        # Application correcte de la rotation en 2D sur (x, z)
        x_new = z_old * math.sin(teta) - x_old * math.cos(teta)
        y_new = - y_old  # Pas de changement sur l'axe Y
        z_new = x_old * math.sin(teta) + z_old * math.cos(teta)
        
        
        # Appliquer transformation
        volume.translation = [x_new, y_new, z_new]
        volume.rotation = rotation_matrix
        
# Simulation

def InitSim():
    # Création de la simulation
    sim = gate.Simulation()
    sim.number_of_threads = 14

    # Configuration globale
    sim.verbose_level = gate.logger.DEBUG
    sim.running_verbose_level = gate.logger.RUN
    sim.g4_verbose = False
    sim.visu = False
    sim.visu_type = "vrml"  # Visualisation en 3D
    sim.random_engine = "MersenneTwister"
    sim.random_seed = "auto"
    sim.output_dir = "./output"

    # Définition du monde
    world = sim.world
    world.size = [100 * cm, 100 * cm, 100 * cm]
    world.material = "G4_AIR"

    # Ajout des matériaux
    sim.volume_manager.material_database.add_material_nb_atoms("Lead", ["Pb"], [1], 11.4 * gcm3)
    sim.volume_manager.material_database.add_material_nb_atoms("NaI", ["Na", "I"], [1, 1], 3.67 * gcm3)
    sim.volume_manager.material_database.add_material_nb_atoms("Quartz", ["Si", "O"], [1, 2], 2.2 * gcm3)
    
    # Configuration de la physique
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"
    sim.physics_manager.set_production_cut("world", "gamma", 1 * mm)
    
    sim.expected_number_of_events = 10**7
    
    # # Lancer la simulation de manière réaliste
    # sec = gate.g4_units.second
    # sim.run_timing_intervals = [[0 * sec, 7.5 * sec]]
    
    return sim    

def hitProjImage(camId, teta):
    # Attacher l'acteur de hits au cristal
    hits = sim.add_actor("DigitizerHitsCollectionActor", f"hits{camId}")
    hits.attached_to = f"crystal_{camId}"
    hits.attributes = ["TotalEnergyDeposit", "PostPosition"]
    
    # Ajouter une image de projection simple
    proj = sim.add_actor("DigitizerProjectionActor", f"proj{camId}")
    proj.attached_to = f"crystal_{camId}"
    proj.input_digi_collections = [f"hits{camId}"]
    proj.size = [128, 128]
    proj.spacing = [4.2 * mm, 4.2 * mm]
    
    # Enregistrer les fichiers .raw et .mhd
    hits.output_filename = f"output/hits_crystal_{camId}_{teta}deg.root"
    proj.output_filename = f"output/projection_crystal_{camId}_{teta}deg.mhd"

if __name__ == "__main__":
    
    #Initialisation de la simu
    sim = InitSim()

    distanceCam = 20.8 * cm
    
    # Création d'une camera
    camera = newCamera(2)
    
    teta = int(sys.argv[1])
    # teta = 30
    RotCircOy(camera, teta)
        
    # Ajout du phantom
    iec_phantom = phantom()
    
    # Recuperation des images
    hitProjImage(1, teta)
    hitProjImage(2, teta + 180)
    
    # Lancer la simulation
    
    sim.run()
    
    # Affichage des résultats
    print("Simulation terminée.")