import os
import time
import json
import random
import logging.config

from yafs.topology import Topology
from yafs.application import create_applications_from_json
from yafs.path_routing import DeviceSpeedAwareRouting
from yafs.distribution import deterministic_distribution
from yafs.placement import JSONPlacement
from yafs.core import Sim

import networkx as nx

def main(stop_time, it):

    '''
        TOPOLOGY DEFINITION (from JSON file)
    '''
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    topology_json = json.load(open(THIS_FOLDER + '/data/topology_definition.json'))
    
    t = Topology()
    t.load_all_node_attr(topology_json)
    nx.write_gexf(t.G,THIS_FOLDER + "/results/topology.gexf") # exported .gexf file for visualizing it with Gephi

    print(t.G.nodes())

    '''
        APPLICATION DEFINITION (from JSON file)
    '''
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    app_json = json.load(open(THIS_FOLDER + '/data/app_definition.json'))
    apps = create_applications_from_json(app_json) # this array will consist of only one app

    '''
        MODULE PLACEMENT (from JSON file)
    '''
    placement_json = json.load(open(THIS_FOLDER + '/data/alloc_definition.json'))
    placement = JSONPlacement(name="Placement", json=placement_json)

    '''
        ROUTING ALGORITHM (of messages along the topology) 
    '''
    selector_path = DeviceSpeedAwareRouting()

    '''
        SIMULATION ENGINE
    '''
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    s = Sim(t, default_results_path=THIS_FOLDER+"/results/s_trace")

    '''
        DEPLOY OF THE APP'S MODULES (from JSON file)
    '''
    for app in apps.keys():
        s.deploy_app(apps[app], placement, selector_path)

    print(apps["water_pipe_control"])
    '''
        DEPLOY INITIAL WORKLOAD (from JSON file)
    '''
    population_json = json.load(open(THIS_FOLDER + '/data/population_definition.json'))
    for source in population_json["sources"]:
        app_name = source["app"]
        app = s.apps[app_name]
        msg = app.get_message(source["message"])
        node = source["id_resource"]
        dist = deterministic_distribution(100, name="Deterministic")
        idDES = s.deploy_source(app_name, id_node=node, msg=msg, distribution=dist)

    '''
        RUNNING - last step
    '''
    s.run(stop_time)  # To test deployments put test_initial_deploy a TRUE

if __name__ == '__main__':
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.ini')
    logging.config.fileConfig(log_file_path)
    #logging.config.fileConfig(os.getcwd() + '/logging.ini')

    nIterations = 1  # iteration for each experiment
    sulationDuration = 5000

    # Iteration for each experiment changing the seed of randoms
    for iteration in range(nIterations):
        random.seed(iteration)
        logging.info("Running experiment: %i" % iteration)

        start_time = time.time()
        main(stop_time=sulationDuration, it=iteration)

        print("\n--- %s seconds ---" % (time.time() - start_time))

    print("sulation Done!")
