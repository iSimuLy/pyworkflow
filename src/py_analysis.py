"""
py_analysis.py: Analysis class for python md workflow module.
Analysis class will have ownership over parameters, design of experiments, and simulation sets.
"""

import os
from warnings import warn
from shutil import copy2
from lammps_interface import parse_inputfile, write_inputfile
from design_of_experiments import FullOrthogonal
import py_scheduler as sched


class PyWorkflow:

    def __init__(self):

        self.name = 'Name'
        self.input = None       # TODO: Should be an interface object
        self.geometry = None
        self.analysis = None
        self.manager = None     # TODO: Define this

        self.parameters = None
        self._active_parameters = None
    # end __init__

    # *** Setting Functions *** #

    def set_name(self, name):
        self.name = name
    # end set_name

    def set_input(self, filename):
        """
        Set the input deck name.
        :param filename: str; filepath to input deck.
        :return: None
        """
        if os.path.exists(filename):
            self.parameters = parse_inputfile(filename)
            self.set_study_parameters(self.parameters)
        else:
            warn("Filename: " + filename + " doesn't exist.")
    # end set_input

    def set_geometry(self, geometry):
        # I don't have a use for this in the current use-case, but should check it for being a function or filename
        self.geometry = geometry
    # end set_geometry

    def set_analysis_method(self, doe=None, **kwargs):
        """
        Sets up the DoE of the specified type.
        :param doe: str; type of DoE to setup
        :param kwargs: dict; options to DoE type
        :return: None
        """

        if 'variables' in kwargs.keys():
            self.set_study_parameters(kwargs['variables'])

        if doe.lower() == "orthogonal":
            self.analysis = FullOrthogonal(self._active_parameters, **kwargs)
        else:
            raise Exception('Analysis type {} has not been created yet.'.format(doe))
    # end set_analysis_method

    def set_study_parameters(self, parameters):
        """
        Sets the analysis variables for this analysis.
        :param parameters: dict; parameter/value pairs. Values can be single values or lists of values.
        :return: None
        """
        self._active_parameters = parameters
        # TODO: Make sure all active parameters are in self.parameters
    # end set_study_parameters

    def set_parameter_value(self, parameter, value):
        # TODO: Define method - change value of _active_parameter
        pass
    # end set_parameter_value

    def remove_parameter(self, param_name):
        if param_name in self._active_parameters.keys():
            del(self._active_parameters[param_name])
    # end remove_parameter

    # *** Getter Functions *** #

    def get_active_parameters(self):
        return self._active_parameters
    # end get_active_parameters

    # *** Control functions *** #

    def start(self, **kwargs):
        """
        Starts running the experiments in the analysis.
        :return: None
        """

        # my_scheduler = sched.Scheduler()

        job_number = 0
        # TODO: the following algorithm only works for analysis types where all jobs are created up front.
        while not self.analysis.is_complete():

            job_name = '{}{}'.format(self.name, job_number)
            if not os.path.exists(job_name):
                os.mkdir(job_name)
            job_params = self.analysis.next()
            print "Writing to {}:".format(job_name)
            print "\t", job_params
            job_input = job_name + '.param'
            write_inputfile(os.path.join(job_name, job_input), self.input, job_params)

            job_number += 1

            # TODO: For generalization, would also need to copy geometry files, or run geometry script

            job = LammpsJob(job_name, job_input, localdir=os.path.join(os.getcwd(), job_name),
                            workdir='/scratch/bradley/' + job_name, **kwargs)
            os.system(job.run())
        # my_scheduler.add_job(job)

    # end start
# end PyWorkflow


class LammpsJob:

    clusters = ["raptor", "talon", "shadow"]
    compute = ["apex", "bazooka", "javelin"]
    cluster_ppn = {'raptor': 8, 'talon': 12, 'shadow': 20}
    pbs_form = """
    #!/bin/bash
    # #PBS Input script for automated job submission
    ##Required Directives--------------------------------------
    #PBS -l nodes={nodes}:ppn={ppn}
    #PBS -l walltime={time}
    #PBS -q {queue}

    ## Optional Directives --------------------------------------
    #PBS -N {name}
    #PBS -j oe
    #PBS -m e

    cd {work}
    mpirun -np {numproc} lmp_{system} -var restart {re} -in {inp} > lmp.out
    """

    def __init__(self, name, in_deck, **kwargs):
        # Set default parameters
        params = {'otherfiles': None, 'system': None, 'numproc': 1, 'workdir': '/scratch/bradley/',
                  'localdir': os.getcwd(), 'queue': 'q64p48h', 'walltime': 1, 're': 0, 'inp': in_deck}
        params.update(kwargs)
        if params['system'] is not None:
            params.update({'nodes': int(params['numproc'] / LammpsJob.cluster_ppn[params['system']]),
                       'ppn': LammpsJob.cluster_ppn[params['system']]})

        self.system = params['system']

        if params['numproc'] > 1:
            if params['system'] is None:
                self.command_string = "cd {workdir}; mpirun -np {numproc} lmp_blazer -var restart {re} -in {inp}".\
                    format(**params)
            elif params['system'] in LammpsJob.compute:
                self.command_string = 'rsh {system} "cd {workdir}; mpirun -np {numproc} -var restart {re} -in {inp}"'.\
                    format(**params)
            elif params['system'] in LammpsJob.clusters:
                self.command_string = 'rsh {system}-login "cd {workdir}; echo {pbs} > job.pbs; qsub job.pbs"'.\
                    format(pbs=LammpsJob.pbs_form.format(**params), **params)

        if not os.path.exists(params['workdir']):
            os.mkdir(params['workdir'])

        if params['otherfiles'] is not None:
            for f in params['otherfiles']:
                copy2(os.path.join(params['localdir'], f), os.path.join(params['workdir'], f))
        copy2(os.path.join(params['localdir'], in_deck), os.path.join(params['workdir'], in_deck))
    # end __init__

    def run(self):
        return self.command_string

    def progress(self):
        pass
# end LammpsJob
