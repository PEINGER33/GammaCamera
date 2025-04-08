import opengate as gate
import math
import opengate.contrib.phantoms.nemaiec as gate_iec
import numpy as np

def newCamera(nbTete):
    camera = []
    for i in range(nbTete):
        camera.append(newTete(i))
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
    collimator.material = "G4_AIR"
    #collimator.material = "Lead"
    collimator.size = [54 * cm, 40 * cm, 5.8 * cm]
    collimator.translation = [0, 0, distanceCam]  # Position du collimateur
    collimator.color = [0.5, 0.5, 0.5, 1]  # Gris
    return collimator

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
        pmt = sim.add_volume("Box", f"PMT_{i+4*index}")
        pmt.material = "G4_AIR"
        pmt.size = [8 * cm, 8 * cm, 3 * cm]
        pmt.translation = trans_local  # Derrière le guide
        pmt.color = [1, 1, 0, 1]
        pmts.append(pmt)
    return pmts

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

if __name__ == "__main__":
    # Création de la simulation
    sim = gate.Simulation()

    # Configuration globale
    sim.verbose_level = gate.logger.DEBUG
    sim.running_verbose_level = gate.logger.RUN
    sim.g4_verbose = False
    sim.visu = True
    sim.visu_type = "vrml"  # Visualisation en 3D
    sim.random_engine = "MersenneTwister"
    sim.random_seed = "auto"
    sim.output_dir = "./output"

    # Définition des unités
    cm = gate.g4_units.cm
    mm = gate.g4_units.mm
    keV = gate.g4_units.keV
    gcm3 = gate.g4_units.g / cm**3
    Bq = gate.g4_units.Bq
    mL = gate.g4_units.cm3
    BqmL = Bq / mL

    # Définition du monde
    world = sim.world
    world.size = [100 * cm, 100 * cm, 100 * cm]
    world.material = "G4_AIR"

    # Ajout des matériaux
    sim.volume_manager.material_database.add_material_nb_atoms("Lead", ["Pb"], [1], 11.4 * gcm3)
    sim.volume_manager.material_database.add_material_nb_atoms("NaI", ["Na", "I"], [1, 1], 3.67 * gcm3)
    sim.volume_manager.material_database.add_material_nb_atoms("Quartz", ["Si", "O"], [1, 2], 2.2 * gcm3)
    
    distanceCam = 22 * cm
    
    # Création d'une camera
    camera = newCamera(2)
    RotCircOy(camera, 0)
    
    # Attacher l'acteur de hits au cristal
    hits_actor = sim.add_actor("DigitizerHitsCollectionActor", "hits")
    hits_actor.attached_to = "crystal_1"  # Attaché au cristal
    hits_actor.output_filename = "gamma_hits.root"
    hits_actor.attributes = ["TotalEnergyDeposit", "PostPosition"]
    
    # Ajouter une image de projection simple
    proj = sim.add_actor("DigitizerProjectionActor", "projection")
    proj.attached_to = "crystal_1"
    proj.physical_volume_index = 0  # ou 1 pour la 2e caméra
    proj.input_digi_collections = ["hits"]
    proj.size = [128, 128]  # pixels (x, y)
    proj.spacing = [4.2 * mm, 4.2 * mm]  # taille pixel
    proj.output_filename = "output/projection_spect.mhd"


    # Ajout du phantom
    iec_phantom = gate_iec.add_iec_phantom(sim, 'iec_phantom')
    #iec_phantom.translation = [0, 0, -8 * cm]
    activities = [0.1 * BqmL, 0.2 * BqmL, 0.3 * BqmL, 0.4 * BqmL, 0.5 * BqmL, 0.6 * BqmL]
    iec_source = gate_iec.add_spheres_sources(sim, 'iec_phantom', 'iec_source', 'all', activities)
    iec_bg_source = gate_iec.add_background_source(sim, 'iec_phantom', 'iec_bg_source', 0.01 * BqmL)

    # Configuration de la physique
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"
    sim.physics_manager.set_production_cut("world", "gamma", 1 * mm)

    # Lancer la simulation
    sim.number_of_events = 1000  # Nombre d'événements
    sim.run()

    # Affichage des résultats
    print("Simulation terminée.")

