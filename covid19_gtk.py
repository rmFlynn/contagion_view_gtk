import gi
import pandas as pd
#import geopandas as gpd
import numpy as np
#import geoplot as gplt
import matplotlib._color_data as mcd

import seaborn as sns
gi.require_version('Champlain', '0.12')
gi.require_version('GtkChamplain', '0.12')
gi.require_version('GtkClutter', '1.0')
from gi.repository import GtkClutter, Clutter
GtkClutter.init([])  # Must be initialized before importing those:
from gi.repository import GObject, Gtk, Champlain, GtkChamplain, Pango

import os
import sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

class HeaderBarWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="HeaderBar Demo")
        self.set_border_width(10)
        self.set_default_size(900, 600)


        embed = self.load_data() 

        #self.set_data() 
        #self.active_ob = 0

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Contagion Viewer"
        self.set_titlebar(hb)


        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(1000)

        self.spinbutton = Gtk.SpinButton.new_with_range(0, 20, 1)
        self.spinbutton.connect("changed", self.zoom_changed)
        self.view.connect("notify::zoom-level", self.map_zoom_changed)
        self.spinbutton.set_value(4)

        label = Gtk.Label()
        label.set_markup("<big>The point plot, interactive map will go here.</big>")
        stack.add_titled(embed, "Map", "Map View")

        label = Gtk.Label()
        label.set_markup("<big>The supplemental view, should I choose to include it, we'll go here. \n\n But I probably won't include it.</big>")
        stack.add_titled(label, "breakout", "Supplemental")

        label = Gtk.Label()
        label.set_markup("<big>The time series view will go here.</big>")
        stack.add_titled(label, "timeseries", "time series")

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)

        box_r = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box_r.get_style_context(), "linked")

        box_l = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box_l.get_style_context(), "linked")

        box_r.pack_start(self.make_liststore_state(), True, True, 0)
        box_r.pack_start(self.make_liststore_day(), True, True, 0)
        box_r.pack_start(self.spinbutton, True, True, 0)
        box_l.pack_end(stack_switcher, True, True, 0)

        hb.pack_start(box_r)
        hb.pack_end(box_l)
        
        self.add(stack)

    def make_liststore_day(self):
        liststore = Gtk.ListStore(int, str)
        for i, day in enumerate(self.days):
            liststore.append([i, str(day)])

        combo = Gtk.ComboBox()
        combo.set_model(liststore)
        cell = Gtk.CellRendererText()
        combo.pack_start(cell, False)
        combo.add_attribute(cell, 'text', 1)
        combo.connect("changed", self.time_select)
        combo.set_active(0)
        return combo

    def make_liststore_state(self):
        liststore = Gtk.ListStore(int, str)
        self.states = ['Nation']
        liststore.append([0, "Nation Wide"])
        for i, state in enumerate(self.data_orig['STNAME'].unique()):
            liststore.append([i + 1, state])
            self.states.append(state)
        combo = Gtk.ComboBox()
        combo.set_model(liststore)
        cell = Gtk.CellRendererText()
        combo.pack_start(cell, False)
        combo.add_attribute(cell, 'text', 1)
        combo.connect("changed", self.state_select)
        combo.set_active(0)
        return combo

    def zoom_changed(self, widget):
        self.view.set_property("zoom-level", self.spinbutton.get_value_as_int())

    def map_zoom_changed(self, widget, value):
        self.spinbutton.set_value(self.view.get_property("zoom-level"))

    def time_select(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        id = model.get_value(iter, 0)
        self.alter_points(self.view, self.days[id])

    def state_select(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        id = model.get_value(iter, 0)
        #self.alter_points(self.view, self.days[id])
        self.set_data()

    def zoom_in(self, widget):
        self.view.zoom_in()

    def zoom_out(self, widget):
        self.view.zoom_out()

    def load_data(self):
        embed = GtkChamplain.Embed()

        embed.set_size_request(900, 600)

        self.view = embed.get_view()
        self.view.set_reactive(True)

        self.view.set_property('kinetic-mode', True)
        self.view.set_property('zoom-level', 5)

        scale = Champlain.Scale()
        scale.connect_view(self.view)
        self.view.bin_layout_add(scale, Clutter.BinAlignment.START,
            Clutter.BinAlignment.END)

        license = self.view.get_license_actor()
        license.set_extra_text("Do what you want but I am RMFlynn")

        self.view.center_on(39.739, -104.984)

        data = pd.read_pickle('data_set3.pkl')
        #data['hue'] = orange
        self.days = data.columns[37:]
        self.data_orig = data
        self.marker_layer= Champlain.MarkerLayer()
        self.view.add_layer(self.marker_layer)
        self.marker_layer.show()
        return embed

    def set_data(self):
        self.data = self.data_orig
        self.data['point'] = [Champlain.Point.new() for i in self.data.index] 
        #print(self.days)
        max_case = np.amax(self.data[self.days].values)

        for day in self.days:
            print(day)
            sizes = []
            for _, i in self.data.iterrows():
                size = int(i[day]/(max_case/500))
                if (size < 7) and (i[day] > 0):
                    size = 7
                sizes.append(size)
            self.data[day] = sizes
        self.make_marker_layer(self.view)


    def make_marker_layer(self, view):

        orange = Clutter.Color.new(0xf3, 0x94, 0x07, 0xbb)

        self.marker_layer.remove_all()
        self.selected = []
        
        
        for _, i in self.data.iterrows():
            i.point.set_color(orange)
            i.point.set_size(0)
            x = i.geometry
            i.point.set_location(x[1], x[0])
            i.point.connect("button-release-event", self.mark_function(i['county_name'], i['STNAME'], x[1], x[0]), view)
            self.marker_layer.add_marker(i.point)

        self.marker_layer.show()

    def alter_points(self, view, day):
        for _, i in self.data.iterrows():
            i.point.set_size(i[day])
            print(i[day])
            #size = int(i[day]/(self.max_case/500))
            #if (size < 7) and (i[day] > 0):
            #    i.point.set_size(7)
            #else:
            #    i.point.set_size(size)

    def mark_function(self, ct, st, x1, x0):

        def fun(actor, event, view):
            lb = Champlain.Label.new_with_text(ct + ", " + st)
            lb.set_location(x1, x0)
            self.marker_layer.add_marker(lb)
            self.selected.append([ct,st])
            print(self.selected)

        return fun


        




win = HeaderBarWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

