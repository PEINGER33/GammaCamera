import opengate as gate
import math
import opengate.contrib.phantoms.nemaiec as gate_iec

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

    # Position de la gamma caméra
    camera_distance = 0 * cm  # Distance de la caméra par rapport à la source
    x_position = camera_distance  # Position de la caméra sur l'axe X
    y_position = 0  # Alignée sur l'axe Y
    z_position = 22 * cm  # Hauteur de la caméra
    
    # Parametre de translation circulaire
    translations_circle, rotations_circle = gate.geometry.utility.get_circular_repetition(number_of_repetitions=2, first_translation=[ 0, 0, z_position], axis=[0, 1, 0])
    translations_circle_2, rotations_circle_2 = gate.geometry.utility.get_circular_repetition(number_of_repetitions=2, first_translation=[ 0, 0, z_position + 3.*cm], axis=[0, 1, 0])
    translations_circle_3, rotations_circle_3 = gate.geometry.utility.get_circular_repetition(number_of_repetitions=2, first_translation=[ 0, 0, z_position + 3.75*cm], axis=[0, 1, 0])
    translations_circle_4, rotations_circle_4 = gate.geometry.utility.get_circular_repetition(number_of_repetitions=2, first_translation=[ -3*cm, -3*cm, z_position + 5*cm], axis=[0, 1, 0])
    translations_circle_5, rotations_circle_5 = gate.geometry.utility.get_circular_repetition(number_of_repetitions=2, first_translation=[ 3*cm, 3*cm, z_position + 5*cm], axis=[0, 1, 0])
    translations_circle_6, rotations_circle_6 = gate.geometry.utility.get_circular_repetition(number_of_repetitions=2, first_translation=[ -3*cm, 3*cm, z_position + 5*cm], axis=[0, 1, 0])
    translations_circle_7, rotations_circle_7 = gate.geometry.utility.get_circular_repetition(number_of_repetitions=2, first_translation=[ 3*cm, -3*cm, z_position + 5*cm], axis=[0, 1, 0])
    
    # Création du collimateur (en plomb)
    collimator = sim.add_volume("Box", "collimator")
    collimator.material = "G4_AIR"
    #collimator.material = "Lead"
    collimator.size = [54 * cm, 40 * cm, 5.8 * cm]
    collimator.translation = [x_position, y_position, z_position]  # Position du collimateur
    collimator.color = [0.5, 0.5, 0.5, 1]  # Gris
    collimator.translation = translations_circle
    collimator.rotation = rotations_circle

    # Création du cristal scintillant (NaI)
    crystal = sim.add_volume("Box", "crystal")
    crystal.material = "NaI"
    crystal.size = [54 * cm, 40 * cm, 1.59 * cm]
    crystal.translation = [x_position, y_position, z_position + 3 * cm]  # Position du cristal
    crystal.color = [1, 0, 0, 1]  # Rouge
    crystal.translation = translations_circle_2
    crystal.rotation = rotations_circle_2

    # Création du guide de lumière (Quartz)
    light_guide = sim.add_volume("Box", "light_guide")
    light_guide.material = "Quartz"
    light_guide.size = [54 * cm, 40 * cm, 0.5 * cm]
    light_guide.translation = [x_position, y_position, z_position + 1.59 * cm + 0.25 * cm]  # Derrière le cristal
    light_guide.color = [0, 1, 1, 0.5]  # Cyan transparent
    light_guide.translation = translations_circle_3
    light_guide.rotation = rotations_circle_3

    pmt_size = [6 * cm, 6 * cm, 2 * cm]
    x_range = [-24, -12, 0, 12, 24]
    y_range = [-18, -6, 6, 18]
    
    # Position centrale Z des PMT (derrière cristal et light guide)
    local_z = 1.59 * cm + 0.5 * cm + 1 * cm
    base_translation = [0, 0, z_position + local_z]
    
    # Création des tubes photomultiplicateurs (PMT)
    pmt_size = [8 * cm, 8 * cm, 3 * cm]  # Taille d'un PMT


    # Coordonnées locales des PMTs (sur XY)
    pmt_positions = [
        [-18 * cm, -12 * cm],  # PMT_1 coin bas gauche
        [18 * cm, 12 * cm],    # PMT_2 coin haut droit
        [-18 * cm, 12 * cm],   # PMT_3 coin haut gauche
        [18 * cm, -12 * cm]    # PMT_4 coin bas droit
        ]
    
    # Z position cohérente derrière crystal + guide
    z_pmt = z_position + 5.5 * cm
    
    # Boucle sur les positions locales
    for i, (x, y) in enumerate(pmt_positions, start=1):
        trans_local = [x, y, z_pmt]
        translations, rotations = gate.geometry.utility.get_circular_repetition(
            number_of_repetitions=2,
            first_translation=trans_local,
            axis=[0, 1, 0]
            )
        pmt = sim.add_volume("Box", f"PMT_{i}")
        pmt.material = "G4_AIR"
        pmt.size = pmt_size
        pmt.color = [1, 1, 0, 1]
        pmt.translation = translations
        pmt.rotation = rotations
    

    # Attacher l'acteur de hits au cristal
    hits_actor = sim.add_actor("DigitizerHitsCollectionActor", "hits")
    hits_actor.attached_to = "crystal"  # Attaché au cristal
    hits_actor.output_filename = "gamma_hits.root"
    hits_actor.attributes = ["TotalEnergyDeposit", "PostPosition"]
    
    # Ajouter une image de projection simple
    proj = sim.add_actor("DigitizerProjectionActor", "projection")
    proj.attached_to = "crystal"
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

