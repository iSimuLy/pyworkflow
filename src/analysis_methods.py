"""
analysis_methods.py: Classes and wrapper for analysis methods
"""

import numpy as np


class FullOrthogonal:

    options = ["order"]

    def __init__(self, parameters=None, order=None):
        """
        FullOrthogonal constructor
        :param parameters: dict; parameter and values pairs
        :param order: specify the order to expand on parameters and specify parameter to be paired
        :return:
        """

        if not parameters:
            parameters = {}

        if not order:
            self.order = []

        self.job_list = None
        self.job_iter = None

        self.create_analyses(parameters)
    # end __init__

    def create_analyses(self, parameters):

        ordered_names = []
        for o in self.order:
            if isinstance(o, list):
                ordered_names.extend(o)
            else:
                ordered_names.append(o)
        param_names = parameters.keys()
        for pn in param_names:
            if pn not in ordered_names:
                self.order.append(pn)
                ordered_names.append(pn)

        param_names = self.order
        job_form = [dict((i, None) for i in ordered_names)]
        for pn in param_names:
            new_jobs = []
            if isinstance(pn, list):
                values = [parameters[pi] if (hasattr(parameters[pi], '__len__') or isinstance(parameters[pi], str))
                          else [parameters[pi]] for pi in pn]
                lengths = [len(val) for val in values]
                if not np.all(np.array(lengths) == lengths[0]):
                    raise Exception("For paired parameters, value lengths must be the same.")
            else:
                values = parameters[pn]
                if not hasattr(values, '__len__') or isinstance(values, str):
                    values = [values]

            for val in np.array(values).T:
                for oj in job_form:
                    if hasattr(pn, '__len__') and not isinstance(pn,str):
                        for i_pn, i_val in zip(pn,val):
                            oj.update({i_pn: i_val})
                    else:
                        oj.update({pn: val})
                    new_jobs.append(oj.copy())
            job_form = new_jobs
        self.job_list = job_form
        self.job_iter = iter(job_form)
    # end create_analyses

    def set_options(self, **kwargs):
        pass  # TODO: set order, then recreate analyses
    # end set_options

    def next(self):
        """ Return the next job to be run """
        return self.job_iter.next()
    # end next

    def is_complete(self):
        return self.job_iter.__length_hint__() == 0
    # end is_complete

    def get_options(self):
        return self.options
    # end get_options
# end FullOrthogonal
