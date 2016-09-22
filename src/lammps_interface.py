"""
lammps_interface.py: Defines functions for reading and writing the lammps parameter files
for the MD simulations.
"""


def parse_inputfile(filename):
    """
    parse_inputfile parses a lammps parameter file with a certain structure to get variables.

    :param filename: str; filename to parse
    :return: dict; set of variables and default values
    """

    parameters = {}

    with open(filename, 'r') as inputfile:
        for line in inputfile:
            words = line.split()
            if len(words) > 0 and words[0] == "variable":
                if words[2] == "equal":
                    parameters.update({words[1]: float(words[3])})
                elif words[2] == "string":
                    parameters.update({words[1]: words[3]})

    return parameters
# end parse_inputfile


def write_inputfile(filename, pattern, parameters):
    """

    :param filename: str; new input filename to create
    :param pattern: str; input filename to use as a pattern
    :param parameters: dict; new parameter values to use
    :return:
    """

    inputfile = open(filename,'w')

    with open(pattern,'r') as pat:
        for line in pat:
            words = line.split()
            if len(words) > 0 and words[0] == "variable" and words[1] in parameters.keys():
                words[3] = str(parameters[words[1]])
            inputfile.write(' '.join(words))
            inputfile.write('\n')
    inputfile.close()
# end write_inputfile
