import json
import sys
import os
import numpy as np
sys.path.append('/home/ndorn/Documents/Stanford/PhD/Simvascular/svZeroDPlus/structured_trees/src')
# print(sys.path)
from svzerodtrees.structuredtreebc import StructuredTreeOutlet
from pathlib import Path
from svzerodtrees.post_processing.stree_visualization import *
import matplotlib.pyplot as plt
from svzerodtrees.utils import *
from scipy.optimize import minimize
from svzerodtrees.adaptation import *
from svzerodtrees import operation, preop, interface, postop
from svzerodtrees._config_handler import ConfigHandler
from svzerodtrees._result_handler import ResultHandler
import pickle


def build_tree(config, result):
    simparams = config["simulation_parameters"]
    # get the outlet flowrate
    q_outs = get_outlet_data(config, result, "flow_out", steady=True)
    outlet_trees = []
    outlet_idx = 0 # need this when iterating through outlets 
    # get the outlet vessel
    for vessel_config in config["vessels"]:
        if "boundary_conditions" in vessel_config:
            if "outlet" in vessel_config["boundary_conditions"]:
                for bc_config in config["boundary_conditions"]:
                    if vessel_config["boundary_conditions"]["outlet"] in bc_config["bc_name"]:
                        outlet_stree = StructuredTreeOutlet.from_outlet_vessel(vessel_config, simparams, bc_config, Q_outlet=[np.mean(q_outs[outlet_idx])])
                        R = bc_config["bc_values"]["R"]
                # outlet_stree.optimize_tree_radius(R)
                outlet_stree.build_tree()
                outlet_idx += 1 # track the outlet idx for more than one outlet
                outlet_trees.append(outlet_stree)
    
    return outlet_trees

def test_preop():
    '''
    test the preop optimization scheme
    '''
    input_file = 'tests/cases/LPA_RPA_0d_steady/LPA_RPA_0d_steady.json'
    log_file = 'tests/cases/LPA_RPA_0d_steady/LPA_RPA_0d_steady.log'
    clinical_targets = 'tests/cases/LPA_RPA_0d_steady/clinical_targets.csv'
    working_dir = 'tests/cases/LPA_RPA_0d_steady'

    config_handler, result_handler = preop.optimize_outlet_bcs(
        input_file,
        clinical_targets,
        log_file,
        show_optimization=False,
        
    )

    result_handler.to_file('tests/cases/LPA_RPA_0d_steady/result_handler.out')
    config_handler.to_file('tests/cases/LPA_RPA_0d_steady/preop_config.in')
        


def test_cwss_tree_construction():
    '''
    test the tree construction algorithm

    '''
    
    config_handler = ConfigHandler.from_file('tests/cases/LPA_RPA_0d_steady/preop_config.in')

    with open('tests/cases/LPA_RPA_0d_steady/result_handler.out', 'rb') as ff:
        result_handler = pickle.load(ff)
    
    log_file = 'tests/cases/LPA_RPA_0d_steady/LPA_RPA_0d_steady.log'

    write_to_log(log_file, 'testing tree construction', write=True)

    preop.construct_cwss_trees(config_handler, result_handler, log_file, d_min=0.049)

    # print the number of vessels in the tree
    print("n_vessels = " + str([tree.count_vessels() for tree in config_handler.trees]))

    R_bc = []
    for bc_config in config_handler.config["boundary_conditions"]:
        if 'RESISTANCE' in bc_config["bc_type"]:
            R_bc.append(bc_config["bc_values"]["R"])
    
    np.array(R_bc)
    R_opt = np.array([tree.root.R_eq for tree in config_handler.trees])

    SSE = sum((R_bc - R_opt) ** 2)

    print(SSE)
    print(config_handler.trees)


def test_pries_tree_construction():
    # test pries and secomb tree building
    config_handler = ConfigHandler.from_file('tests/cases/LPA_RPA_0d_steady/preop_config.in')

    with open('tests/cases/LPA_RPA_0d_steady/result_handler.out', 'rb') as ff:
        result_handler = pickle.load(ff)

    preop.construct_pries_trees(config_handler, result_handler, d_min=0.5, tol=0.1)


def test_repair_stenosis():
    '''
    test the virtual 0d stenosis repair algorithm for the proximal, extensive and custom cases
    '''
    with open('tests/cases/LPA_RPA_0d_steady/preop_config.in') as ff:
        preop_config = json.load(ff)
    
    with open('tests/cases/repair.json') as ff:
        repair_dict = json.load(ff)
    
    with open('tests/cases/LPA_RPA_0d_steady/result_handler.out', 'rb') as ff:
        result_handler = pickle.load(ff)

    # proximal repair case
    postop_config_prox, result_handler_prox = operation.repair_stenosis_coefficient(preop_config, result_handler, repair_dict['proximal'])

    # extensive repair case
    postop_config_ext, result_handler_ext = operation.repair_stenosis_coefficient(preop_config, result_handler, repair_dict['extensive'])

    # custom repair case
    postop_config_cust, result_handler_cust = operation.repair_stenosis_coefficient(preop_config, result_handler, repair_dict['custom'])


def test_cwss_adaptation():
    '''
    test the constant wss tree adaptation algorithm
    '''
    
    config_handler = ConfigHandler.from_file('tests/cases/LPA_RPA_0d_steady/preop_config.in')

    with open('tests/cases/LPA_RPA_0d_steady/result_handler.out', 'rb') as ff:
        result_handler = pickle.load(ff)
    
    with open('tests/cases/repair.json') as ff:
        repair_dict = json.load(ff)
    
    repair_config = repair_dict['proximal']

    preop.construct_cwss_trees(config_handler, result_handler, fig_dir='tests/cases/LPA_RPA_0d_steady/', d_min=0.49)


    operation.repair_stenosis_coefficient(config_handler, result_handler, repair_config)

    adapt_constant_wss(config_handler, result_handler)

    result_handler.format_results()

    print(result_handler.clean_results)



def test_pries_adaptation():
    '''
    test the constant wss tree adaptation algorithm
    '''
    
    config_handler = ConfigHandler.from_file('tests/cases/LPA_RPA_0d_steady/preop_config.in')

    with open('tests/cases/LPA_RPA_0d_steady/result_handler.out', 'rb') as ff:
        result_handler = pickle.load(ff)
    
    with open('tests/cases/repair.json') as ff:
        repair_dict = json.load(ff)
    
    repair_config = repair_dict['proximal']

    log_file = 'tests/cases/LPA_RPA_0d_steady/LPA_RPA_0d_steady.log'

    write_to_log(log_file, 'testing tree construction', write=True)

    preop.construct_pries_trees(config_handler, result_handler, log_file, d_min=0.49)

    operation.repair_stenosis_coefficient(config_handler, result_handler, repair_config, log_file)

    adapt_pries_secomb(config_handler, result_handler, log_file)

    result_handler.format_results()

    print(result_handler.clean_results)


def test_run_from_file():
    expfile = 'exp_config_test.json'
    os.chdir('tests/cases/LPA_RPA_0d_steady/experiments')

    interface.run_from_file(expfile, vis_trees=True)


def test_pa_optimizer():
    # test the pa optimizer pipeline

    os.chdir('tests/cases/full_pa_test')
    input_file = 'AS1_SU0308_prestent.json'
    log_file = 'full_pa_test.log'
    clinical_targets = 'clinical_targets.csv'
    mesh_surfaces_path = '/home/ndorn/Documents/Stanford/PhD/PPAS/svPPAS/models/AS1_SU0308_prestent/Meshes/1.8M_elements_v3/mesh-surfaces'

    optimized_pa_config, preop_result = preop.optimize_pa_bcs(
        input_file,
        mesh_surfaces_path,
        clinical_targets,
        log_file,
        show_optimization=False,
    )

    # save the optimized pa config
    with open('optimized_pa_config.json', 'w') as ff:
        json.dump(optimized_pa_config, ff)

    # save the preop_Result
    with open('preop_result.out', 'wb') as ff:
        pickle.dump(preop_result, ff)



if __name__ == '__main__':

    # test_preop()
    test_pa_optimizer()