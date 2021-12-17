#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 16:08:00 2018 (MDT)

@author: Rogers F. Silva
"""

import ujson as json
import os
import sys
import copy
import numpy as np
import utils as ut
import phase_keys as pk
from constants import OUTPUT_TEMPLATE
import traceback

LOCAL_SCICA_PHASES = \
    pk.SPATIALLY_CONSTRAINED_ICA_LOCAL + \
    pk.DFNC_PREPROC_LOCAL_EXEMPLARS + \
    pk.DFNC_PREPROC_LOCAL + \
    pk.DKMEANS_LOCAL + \
    pk.DKM_NOEX_LOCAL

# import pydevd_pycharm
#
# pydevd_pycharm.settrace('172.17.0.1', port=8881, stdoutToServer=True, stderrToServer=True)

if __name__ == '__main__':

    PIPELINE = LOCAL_SCICA_PHASES

    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(ut.listRecursive(parsed_args, 'computation_phase'))
    computation_output = copy.deepcopy(OUTPUT_TEMPLATE)
    if not phase_key:
        ut.log("***************************************", parsed_args["state"])
    ut.log("Starting local phase %s" % phase_key, parsed_args["state"])
    ut.log("With input %s" % str(parsed_args), parsed_args["state"])
    for i, expected_phases in enumerate(PIPELINE):
        ut.log("Expecting phase %s, Got phase %s" %
               (expected_phases.get("recv"), phase_key), parsed_args["state"])
        if expected_phases.get('recv') == phase_key or expected_phases.get('recv') in phase_key:
            actual_cp = None
            operations = expected_phases.get('do')
            operation_args = expected_phases.get('args')
            operation_kwargs = expected_phases.get('kwargs')
            for operation, args, kwargs in zip(operations, operation_args, operation_kwargs):
                if 'input' in parsed_args.keys():
                    ut.log('Operation %s is getting input with keys %s' %
                           (operation.__name__, str(parsed_args['input'].keys())), parsed_args['state'])
                else:
                    ut.log('Operation %s is not getting any input!' % operation.__name__, parsed_args['state'])
                try:
                    ut.log("Trying operation %s, with args %s, and kwargs %s" %
                           (operation.__name__, str(args), str(kwargs)), parsed_args["state"])
                    computation_output = operation(parsed_args,
                                                   *args,
                                                   **kwargs)
                except NameError as akerr:
                    ut.log("Hit expected error %s" %
                           (str(akerr)), parsed_args["state"])
                    try:
                        ut.log("Trying operation %s, with kwargs only" %
                               (operation.__name__), parsed_args["state"])
                        computation_output = operation(parsed_args,
                                                       **kwargs)
                    except NameError as kerr:
                        ut.log("Hit expected error %s" %
                               (str(kerr)), parsed_args["state"])
                        try:
                            ut.log("Trying operation %s, with args only" %
                                   (operation.__name__), parsed_args["state"])
                            computation_output = operation(parsed_args,
                                                           *args)
                        except NameError as err:
                            ut.log("Hit expected error %s" %
                                   (str(err)), parsed_args["state"])
                            ut.log("Trying operation %s, with no args or kwargs" %
                                   (operation.__name__), parsed_args["state"])
                            computation_output = operation(parsed_args)
                parsed_args = copy.deepcopy(computation_output)
                ut.log("Finished with operation %s" %
                       (operation.__name__), parsed_args["state"])
                ut.log("Operation output has keys %s" % str(parsed_args['output'].keys()), parsed_args["state"])
            if expected_phases.get('send'):
                computation_output["output"]["computation_phase"] = expected_phases.get(
                    'send')
            ut.log("Finished with phase %s" %
                   expected_phases.get("send"), parsed_args["state"])
            break
    ut.log("Computation output looks like %s, and output keys %s" %
           (str(computation_output.keys()), str(computation_output["output"].keys())), parsed_args["state"])

    try:
        # ut.clean_np_arrays('output', computation_output)
        # ut.clean_np_arrays('cache', computation_output)
        sys.stdout.write(json.dumps(computation_output))
    except:
        with open(parsed_args['state']['outputDirectory'] + os.sep + 'EXCEPTION_TRACE.txt', 'w') as e:
            e.write(traceback.format_exc())
            e.write("\n\n\n" + "*" * 51 + 'cache' + '*' * 51)
            e.write(f"\n{computation_output['cache']}")
            e.write("\n" + "*" * 51 + 'output' + '*' * 51)
            e.write(f"\n{computation_output['output']}")
        raise IOError(f"*** Parsing error with output *** : Check EXCEPTION_TRACE.txt file")
