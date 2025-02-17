import opengate as gate
import opengate.contrib.phantoms.nemaiec as gate_iec

if __name__ == "__main__":
    # CrÃ©ation de la simulation
    sim = gate.Simulation()
    
    # Configuration globale
    sim.verbose_level = gate.logger.DEBUG
    sim.running_verbose_level = gate.logger.RUN
    sim.g4_verbose = False
    sim.visu = True
    sim.visu_type = "vrml"
    sim.random_engine = "MersenneTwister"
    sim.random_seed = "auto"
    sim.output_dir = "./output"
    
    # DÃ©finition des unitÃ©s
    cm = gate.g4_units.cm
    mm = gate.g4_units.mm
    keV = gate.g4_units.keV
    gcm3 = gate.g4_units.g / cm**3
    
    # DÃ©finition du monde
    world = sim.world
    world.size = [50 * cm, 50 * cm, 50 * cm]
    world.material = "G4_AIR"
    
    # Ajout des matÃ©riaux
    sim.volume_manager.material_database.add_material_nb_atoms("Lead", ["Pb"], [1], 11.4 * gcm3)
    sim.volume_manager.material_database.add_material_nb_atoms("NaI", ["Na", "I"], [1, 1], 3.67 * gcm3)
    
    # Ajout du collimateur en plomb
    collimator = sim.add_volume("Box", "collimator")
    collimator.material = "Lead"
    collimator.size = [10 * cm, 10 * cm, 5 * cm]
    collimator.translation = [0, 0, 10 * cm]
    collimator.color = [0.5, 0.5, 0.5, 1]  # Gris
    
    # Ajout du cristal scintillant NaI
    crystal = sim.add_volume("Box", "crystal")
    crystal.material = "NaI"
    crystal.size = [10 * cm, 10 * cm, 1 * cm]
    crystal.translation = [0, 0, 16 * cm]
    crystal.color = [1, 0, 0, 1]  # Rouge
    
    
    
    '''
    #Ajout de l'unitÃ© Becquerel/mL
    Bq = gate.g4_units.Bq
    mL = gate.g4_units.cm3  # 1 mL = 1 cmÂ³
    BqmL = Bq / mL
    
    #Ajout du phantom    
    iec_phantom = gate_iec.add_iec_phantom(sim, 'iec_phantom')
    iec_phantom.translation = [0, 0, -8 * cm]
    activities = [0.1 * BqmL, 0.2 * BqmL, 0.3 * BqmL, 0.4 * BqmL, 0.5 * BqmL, 0.6 * BqmL]
    iec_source = gate_iec.add_spheres_sources(sim, 'iec_phantom', 'iec_source', 'all', activities)
    iec_bg_source = gate_iec.add_background_source(sim, 'iec_phantom', 'iec_bg_source', 0.01 * BqmL)
    '''
    
    
    # Source gamma Tc-99m
    source = sim.add_source("GenericSource", "gamma_source")
    source.particle = "gamma"
    source.energy.mono = 140 * keV
    source.position.type = "sphere"
    source.position.radius = 5 * mm
    source.position.translation = [0, 0, 0]
    source.direction.type = "iso"
    source.n = 1000
    
    
    # Ajout d'un acteur pour collecter les hits dans le cristal
    hits_actor = sim.add_actor("DigitizerHitsCollectionActor", "hits")
    hits_actor.attached_to = "crystal"
    hits_actor.output_filename = "gamma_hits.root"
    hits_actor.attributes = ["TotalEnergyDeposit", "PostPosition"]
    
    # Configuration de la physique
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"
    sim.physics_manager.set_production_cut("world", "gamma", 1 * mm)

    
    # Lancement de la simulation
    sim.number_of_events = 5  # RÃ©duit le nombre total d'Ã©vÃ©nements

    sim.run()
    
    # Affichage des rÃ©sultats
    print(hits_actor)
