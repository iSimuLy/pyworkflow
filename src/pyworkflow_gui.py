#!/usr/bin/env python2.6

"""
pmdwork_interface.py: Creates the gui for use with the pmdwork workflow program
"""

import pygtk
import gtk
from py_analysis import PyAnalysis

pygtk.require('2.0')

# Global PyAnalysis object - only one per interface
pya = PyAnalysis()


class InputModule:

    def __init__(self):

        # TODO: Create a main window only if you haven't been passed a container to add to.
        # Main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("pMDWork")
        self.window.set_border_width(10)

        # Close event
        self.window.connect("delete_event", self.delete_event)

        self.box = gtk.VBox(False, 0)
        self.window.add(self.box)
        self.setup_input_deck(self.box)
        self.setup_parameter(self.box)

        self.box.show()
        self.window.show()
    # end __init__

    def setup_input_deck(self, container):

        # * Input file section * #
        bx_input = gtk.HBox(False, 0)
        container.pack_start(bx_input, False, False, 0)

        # Label
        lab_input = gtk.Label("Input File:")
        bx_input.pack_start(lab_input, False)
        lab_input.show()

        # Text box
        input_text = gtk.Entry()
        bx_input.pack_start(input_text)
        input_text.set_text("test.param")
        input_text.show()

        # Open file button
        bt_open_input = gtk.Button()
        lab_bt_open = gtk.HBox(False, 2)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN, 4)
        image.show()
        label = gtk.Label("Open")
        label.show()
        lab_bt_open.pack_start(image)
        lab_bt_open.pack_start(label)
        lab_bt_open.show()
        bt_open_input.add(lab_bt_open)
        bt_open_input.connect("clicked", self.callback_open_input, input_text)
        bt_open_input.show()
        bx_input.pack_start(bt_open_input, False, False)
        bx_input.show()
    # end setup_input_deck

    def setup_parameter(self, container):

        # Input file parameters section
        frame = gtk.Frame("Parameters")
        container.pack_start(frame)

        frame_box = gtk.VBox(False, 0)
        frame.add(frame_box)

        column_labels = gtk.Table(1, 10, True)
        frame_box.pack_start(column_labels, False, False, 0)

        name_label = gtk.Label("Name")
        column_labels.attach(name_label, 0, 2, 0, 1)
        name_label.show()

        value_label = gtk.Label("Values")
        column_labels.attach(value_label, 2, 5, 0, 1)
        value_label.show()

        add_label = gtk.Label("Add")
        column_labels.attach(add_label, 5, 7, 0, 1)
        add_label.show()

        actions_label = gtk.Label("Actions")
        column_labels.attach(actions_label, 7, 10, 0, 1)
        actions_label.show()
        column_labels.show()

        scrolled_window = gtk.ScrolledWindow()
        frame_box.pack_start(scrolled_window)
        self.variable_window = gtk.VBox(False, 0)
        scrolled_window.add_with_viewport(self.variable_window)

        self.refresh_parameterlist()

        scrolled_window.show()
        frame_box.show()
        frame.show()
    # end setup_parameter

    def refresh_parameterlist(self):
        print "Calling refresh"
        self.variable_window.foreach(lambda widget: self.variable_window.remove(widget))

        if pya.simulation_parameters is None or len(pya.simulation_parameters) == 0:
            variable_list = gtk.VBox(False, 0)
            self.variable_window.pack_start(variable_list)
            empty_label = gtk.Label("No simulation parameters found")
            variable_list.pack_start(empty_label)
            empty_label.show()
            variable_list.show()
        else:
            variable_table = gtk.Table(len(pya.simulation_parameters.keys()), 10, True)
            self.variable_window.pack_start(variable_table)
            for i, var in enumerate(pya.simulation_parameters.keys()):

                var_name = gtk.Label(var)
                variable_table.attach(var_name, 0, 2, i, i+1)
                var_name.show()

                var_val = gtk.Label(str(pya.simulation_parameters[var]))
                variable_table.attach(var_val, 2, 5, i, i+1)
                var_val.show()

                var_ent = gtk.Entry()
                variable_table.attach(var_ent, 5, 7, i, i+1)
                var_ent.show()

                action_add = gtk.Button()
                image = gtk.Image()
                image.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)
                action_add.set_image(image)
                action_add.set_label("")
                image.show()
                variable_table.attach(action_add, 7, 8, i, i+1)
                action_add.show()
                action_add.connect("clicked", self.callback_add_values, [var, var_ent])

                action_clear = gtk.Button()
                image = gtk.Image()
                image.set_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_BUTTON)
                action_clear.set_image(image)
                action_clear.set_label("")
                image.show()
                variable_table.attach(action_clear, 8, 9, i, i+1)
                action_clear.show()
                action_clear.connect("clicked", self.callback_clear_values, var)

                action_remove = gtk.Button()
                image = gtk.Image()
                image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_BUTTON)
                action_remove.set_image(image)
                action_remove.set_label("")
                image.show()
                variable_table.attach(action_remove, 9, 10, i, i+1)
                action_remove.show()
                action_remove.connect("clicked", self.callback_remove_variable, var)

                #variable_entry.show()
            variable_table.show()

        self.variable_window.show_all()
        self.variable_window.show()
    # end refresh_parameterlist

    def callback_open_input(self, widget, data):
        pya.set_input(data.get_text())
        self.refresh_parameterlist()
        print "Changed input deck to " + data.get_text()
    # end callback_open_input

    def callback_remove_variable(self, widget, data):
        pya.remove_parameter(data)
        self.refresh_parameterlist()
    # end callback_remove_variable

    def callback_clear_values(self, widget, data):
        pya.simulation_parameters[data] = []
        self.refresh_parameterlist()
    # end callback_clear_values

    def callback_add_values(self, widget, data):
        key = data[0]
        values = data[1].get_text()
        values = [float(val.strip('[]')) for val in values.split(',')]
        print values
        if isinstance(pya.simulation_parameters[key],list):
            pya.simulation_parameters[key] += values
        elif isinstance(pya.simulation_parameters[key],float) or isinstance(pya.simulation_parameters[key],int):
            pya.simulation_parameters[key] = [pya.simulation_parameters[key]] + values
        self.refresh_parameterlist()
    # end callback_add_values

    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
    # end delete_event
# end InputModule


class AnalysisModule:

    def __init__(self):

        # TODO: Create a main window only if you haven't been passed a container to add to.
        # Main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("pMDWork")
        self.window.set_border_width(10)

        # Close event
        self.window.connect("delete_event", self.delete_event)

        self.box = gtk.VBox(False, 0)
        self.window.add(self.box)
        self.setup_analysis_name(self.box)
        self.setup_doe(self.box)

        self.box.show()
        self.window.show()
    # end __init__

    def setup_analysis_name(self, container):

        # Analysis name section
        bx_analysis_name = gtk.HBox(False, 0)
        container.pack_start(bx_analysis_name, False, False, 0)
        lab_name = gtk.Label("Analysis Name (no spaces):")
        bx_analysis_name.pack_start(lab_name, False)
        lab_name.show()
        name_text = gtk.Entry()
        bx_analysis_name.pack_start(name_text)
        name_text.set_text(pya.name)
        name_text.show()
        bx_analysis_name.show()
        name_text.connect("activate", self.callback_change_name)
    # end setup_analysis_name

    def setup_doe(self, container):

        # Design of Experiments section
        doe_frame = gtk.Frame("Design of Experiments")
        container.pack_start(doe_frame)

        doe_box = gtk.VBox(False, 0)
        doe_frame.add(doe_box)

        options_frame = gtk.Frame("Options")
        option_list = gtk.VBox(False, 0)
        options_frame.add(option_list)

        doe_selector = gtk.HBox(False, 0)
        doe_box.pack_start(doe_selector, False, False, 0)
        doe_selector_label = gtk.Label("Analysis Type:")
        doe_selector.pack_start(doe_selector_label, False, False, 5)
        doe_selector_label.show()

        doe_selector_menu = gtk.combo_box_new_text()
        doe_selector.pack_start(doe_selector_menu)
        doe_selector_menu.append_text("Orthogonal")
        doe_selector_menu.append_text("Specified")
        doe_selector_menu.connect("changed", self.callback_change_method, option_list)
        doe_selector_menu.show()
        doe_selector.show()

        doe_box.pack_start(options_frame)
        self.refresh_doe_options(doe_selector_menu.get_active_text(), option_list)

        options_frame.show()
        doe_box.show()
        doe_frame.show()
    # end setup_doe

    def refresh_doe_options(self, doe_type, container):

        container.foreach(lambda widget: container.remove(widget))

        if doe_type:
            pya.setup_design_of_experiments(doe_type)
            options = pya.doe.get_options()
            for opt in options:
                option_item = gtk.HBox(False, 0)
                container.pack_start(option_item)

                lab = gtk.Label(opt)
                option_item.pack_start(lab, False, False, 5)
                lab.show()

                entry = gtk.Entry()
                option_item.pack_start(entry)
                entry.show()
                entry.connect("activate", self.callback_set_option, opt)

                option_item.show()
        else:
            options_label = gtk.Label("The assorted options for each design of experiments method will be here")
            container.pack_start(options_label)
            options_label.show()

        container.show_all()
    # end setup_doe_options

    def callback_change_name(self, widget):
        pya.set_name(widget.get_text())
        print "Changed name to " + widget.get_text()
    # end callback_change_name

    def callback_change_method(self, widget, container):
        print "Changed method to", widget.get_active_text()
        self.refresh_doe_options(widget.get_active_text(), container)
    # end callback_change_method

    def callback_set_option(self, widget, option_name):
        # pya.set_doe_options({option_name: widget.get_text()})
        print option_name, "set to", widget.get_text()
    # end callback_set_option

    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
    # end delete_event
# end AnalysisModule


class WorkflowGui(InputModule, AnalysisModule):

    def __init__(self):

        # TODO: add calls to super constructors

        # ** Initialize analysis object ** #
        self.py_analysis = PyAnalysis('pmd_interface', input="test.param")

        # Main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("pMDWork")
        self.window.set_border_width(10)
        # Close event
        self.window.connect("delete_event", self.delete_event)

        # ** Setup overall layout of window ** #
        self.content_box = gtk.HBox(False, 2)
        self.setup_box = gtk.VBox(False, 0)
        self.status_box = gtk.VBox(False, 0)
        self.window.add(self.content_box)
        self.content_box.pack_start(self.setup_box)
        self.content_box.pack_start(self.status_box)

        # ** Start populating setup side of window ** #
        self.setup()

        # ** Setup the status half of the window ** #

        # ** Show all the boxes ** #
        self.setup_box.show()
        self.status_box.show()
        self.content_box.show()
        self.window.show()
    # end __init__

    def setup_analysis_status(self):

        # TODO: Move analysis status to new class

        # Analysis status
        analysis_status = gtk.Frame("Analysis Status")
        self.status_box.pack_start(analysis_status)
        analysis_label = gtk.Label("Name\tSystem\tCompletion\tETA\t\tWalltime\n" +
                                   "Job1\t\tRaptor\t\t50\%\t0:01:00\t0:05:00")
        analysis_status.add(analysis_label)
        analysis_label.show()
        analysis_status.show()
    # end setup_analysis_status

    def setup_system_status(self):

        # TODO: move system status to new class

        # System status'
        system_status = gtk.Frame("System Loads")
        self.status_box.pack_start(system_status)
        system_label = gtk.Label("Bars here with system loads")
        system_status.add(system_label)
        system_label.show()
        system_status.show()
    # end setup_system_status

    def setup(self):
        self.setup_input_deck(self.setup_box)
        self.setup_parameter(self.setup_box)
        self.setup_analysis_name(self.setup_box)
        self.setup_doe(self.setup_box)
        self.setup_analysis_status()
        self.setup_system_status()
    # end setup

    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
    # end delete_event

    def callback(self, widget, data):
        print "Hello again - %s was pressed" % data
    # end callback
# end WorkflowGui


def main():
    gtk.main()

if __name__ == "__main__":
    # gui = AnalysisModule()
    gui = WorkflowGui()
    main()
