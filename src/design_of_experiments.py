"""
design_of_experiments.py: Classes and wrapper for design of experiment methods
"""

import numpy as np


class FullOrthogonal:

    def __init__(self, parameters, options=None):
        """
        FullOrthogonal constructor
        :param parameters: dict; parameter and values pairs
        :param options: dict; for this method, only one option
                order: specify the order to expand on parameters and specify parameter to be paired
        :return:
        """

        order = options['order'] if options and ('order' in options.keys()) else []
        ordered_names = []
        for o in order:
            if isinstance(o, list):
                ordered_names.extend(o)
            else:
                ordered_names.append(o)
        param_names = parameters.keys()
        for pn in param_names:
            if pn not in ordered_names:
                order.append(pn)
                ordered_names.append(pn)
        param_names = order

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
                    if hasattr(pn,'__len__') and not isinstance(pn,str):
                        for i_pn, i_val in zip(pn,val):
                            oj.update({i_pn: i_val})
                    else:
                        oj.update({pn: val})
                    new_jobs.append(oj.copy())
            job_form = new_jobs
        self.job_list = job_form
        self.job_iter = iter(job_form)
    # end __init__

    def next(self):
        """ Return the next job to be run """
        return self.job_iter.next()
    # end next

    def is_complete(self):
        if self.job_iter.__length_hint__() == 0:
            return True
        else:
            return False
    # end is_complete

    def get_options(self):
        return ["order"]