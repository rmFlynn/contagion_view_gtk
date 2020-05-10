import gi
import pandas as pd
#import geopandas as gpd
import numpy as np
#import geoplot as gplt
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
import numpy as np

import seaborn as sea
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

        self.days = np.load('./days.npy')

        self.proportion = 0
        self.state = "Nation"
        self.load_data() 

        embed = self.make_map() 

        #self.set_data() 
        #self.active_ob = 0
        self.make_marker_layer()

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Contagion Viewer"
        self.set_titlebar(hb)

        self.make_spin_zoom()

        stack = Gtk.Stack()
        #stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(1000)

        stack.add_titled(embed, "Map", "Map View")

        box_r = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box_r.get_style_context(), "linked")

        box_l = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box_l.get_style_context(), "linked")

        box_r.pack_start(self.make_liststore_state(), True, True, 0)
        box_r.pack_start(self.make_liststore_day(), True, True, 0)
        box_l.pack_start(self.make_liststore_proportion(), True, True, 0)
        box_r.pack_start(self.spinbutton, True, True, 0)

        canvas = self.make_time_series()
        stack.add_titled(canvas, "time", "Time Series")

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
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

    # def make_spin_zoom(self):
    #     times = pd.DataFrame()
    #     times['day_str'] = self.days
    #     times['day'] = pd.to_datetime(times.day_str, infer_datetime_format=True)
    #     #counties = ['Denver', 'King', 'New York']
    #     counties = ['Denver', 'New York']
    #     dfs = []
    #     for county in counties:
    #         t_data = data[data.county_name == county][self.days].T
    #         t_data = t_data.reset_index()
    #         t_data.columns = ['day_str', 'cases']
    #         t_data = t_data[t_data['cases'] > 0]
    #         pop = data[data.county_name == county]['pop'].values[0]
    #         #t_data['cases'] = t_data['cases']/(pop / 100000)
    #         t_data['county'] = county 
    #         t_data['day'] = pd.to_datetime(t_data.day_str, infer_datetime_format=True)
    #         dfs.append(t_data.copy())
    #     c_data = pd.concat(dfs)
    #     times =  times[[i in c_data.day_str.values for i in times.day_str.values]]
    #     plt.clf()
    #     plt.figure(figsize=(20,9))
    #     plot = sea.pointplot(y='cases', x='day', hue="county",  markers='o', data=c_data)
    #     plot.set_xticklabels(times.day_str, rotation=45)
    #     #plt.savefig("counties_over_time.png")#, transparent=True)

    def make_spin_zoom(self):
        self.spinbutton = Gtk.SpinButton.new_with_range(0, 20, 1)
        self.spinbutton.connect("changed", self.zoom_changed)
        self.view.connect("notify::zoom-level", self.map_zoom_changed)
        self.spinbutton.set_value(4)

    def make_time_series(self):
        # data = gpd.read_file('./data_set2/full_data.shp')
        # data = pd.read_pickle('data_set3.pkl')
        # obs = list(data.columns[37:])
        times = pd.DataFrame()
        times['day_str'] = self.days
        times['day'] = pd.to_datetime(times.day_str, infer_datetime_format=True)
        loca = [['Los Angeles', 'California'], ['Orange', 'New York']]
        #counties = ['Denver', 'King', 'New York']
        counties = ['Denver', 'New York']
        counties = ['Denver', 'New York']
        #  dfs = []
        #  for county in counties:
        #      #print(self.data_orig['county_name'] )
        #      t_data = self.data_orig[self.data['county_name'] == county][self.days].T
        #      t_data = t_data.reset_index()
        #      t_data.columns = ['day_str', 'cases']
        #      t_data = t_data[t_data['cases'] > 0]
        #      pop = data[data.county_name == county]['pop'].values[0]
        #      #t_data['cases'] = t_data['cases']/(pop / 100000)
        #      t_data['county'] = county 
        #      t_data['day'] = pd.to_datetime(t_data.day_str, infer_datetime_format=True)
        #      dfs.append(t_data.copy())
        #  c_data = pd.concat(dfs)
        #  times =  times[[i in c_data.day_str.values for i in times.day_str.values]]
        label = Gtk.Label()
        label.set_markup("<big>The time series view will go here.</big>")
        return label

    def make_time_plot(self):
        plt.clf()
        plt.figure(figsize=(10,9))
        plot = sea.pointplot(y='Cases', x='Time', hue="Location",  markers='o', data=self.ts_data)
        #  #plot = sea.lineplot(y='cases', x='day_str', hue="county",  markers='O', data=t_data)
        #  #plot.set_xticklabels(plot.get_xticklabels(), rotation=45)
        #  #plot.get_xticklabels()
        # times =  times[[i in self.ts_data.index.values for i in times.day_str.values]]
        #plot.set_xticklabels(self.days, rotation=45)
        print("figure made")
        plt.savefig("counties_over_time.png")#, transparent=True)


    def make_liststore_proportion(self):
        liststore = Gtk.ListStore(int, str)
        for i, day in enumerate(["Total Infected", "Per 1,000,000"]):
            liststore.append([i, str(day)])
        combo = Gtk.ComboBox()
        combo.set_model(liststore)
        cell = Gtk.CellRendererText()
        combo.pack_start(cell, False)
        combo.add_attribute(cell, 'text', 1)
        combo.connect("changed", self.proportion_select)
        combo.set_active(0)
        return combo

    def make_liststore_state(self):
        liststore = Gtk.ListStore(int, str)
        self.states = ['Nation']
        liststore.append([0, "Nation Wide"])
        for i, state in enumerate(self.data['state_name'].unique()):
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
        self.day = self.days[id]
        self.alter_points()

    def state_select(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        id = model.get_value(iter, 0)
        if self.state != self.states[id]:
            self.state=self.states[id]
            self.load_data() 
            self.make_marker_layer()
            self.alter_points()
        #self.alter_points(self.view, self.days[id])
        #self.set_data()


    def proportion_select(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        id = model.get_value(iter, 0)
        print()
        #self.alter_points(self.view, self.days[id])
        if self.proportion != id:
            self.proportion = id
            self.load_data() 
            self.make_marker_layer()
            self.alter_points()
        #self.set_data()

    def zoom_in(self, widget):
        self.view.zoom_in()

    def zoom_out(self, widget):
        self.view.zoom_out()

    def make_map(self):
        embed = GtkChamplain.Embed()

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

        self.marker_layer= Champlain.MarkerLayer()
        self.view.add_layer(self.marker_layer)
        self.marker_layer.show()
        return embed

    def load_data(self):
        self.ts_data = pd.DataFrame()
        if(self.proportion == 0):
            # Red 
            color = Clutter.Color.new(210, 44, 44, 187)
            if(self.state == "Nation"):
                data = pd.read_pickle('data_nation_total.pkl')
            else:
                data = pd.read_pickle('data_state_total.pkl')
                data = data[data['state_name'] == self.state]
        if(self.proportion == 1):
            # Old Orange
            #color = Clutter.Color.new(0xf3, 0x94, 0x07, 0xbb)
            # Orange
            color = Clutter.Color.new(240, 114, 73, 187)
            if(self.state == "Nation"):
                data = pd.read_pickle('data_nation_permi.pkl')
            else:
                data = pd.read_pickle('data_state_permi.pkl')
                data = data[data['state_name'] == self.state]
        self.data = data
        self.data['point'] = [Champlain.Point.new() for i in self.data.index]
        for _, i in self.data.iterrows():
            i.point.set_color(color)


    def make_marker_layer(self):
        view = self.view

        self.marker_layer.remove_all()
        
        for _, i in self.data.iterrows():
            #i.point.set_color(orange)
            i.point.set_size(0)
            x = i.geometry
            i.point.set_location(x[1], x[0])
            i.point.connect("button-release-event", self.mark_function(i['county_name'], i['state_name'], x[1], x[0]), view)
            self.marker_layer.add_marker(i.point)

        self.marker_layer.show()

    def alter_points(self):
        for _, i in self.data.iterrows():
            i.point.set_size(i[self.day + '_size'])
            #print(i[day])

    def mark_function(self, ct, st, x1, x0):

        def fun(actor, event, view):
            lb = Champlain.Label.new_with_text(ct + ", " + st)
            lb.set_location(x1, x0)
            self.marker_layer.add_marker(lb)
            loca = self.data
            loca = loca[loca['state_name'] == st]
            loca = loca[loca['county_name'] == ct]
            loca = loca[self.days].T
            loca.columns = ["Cases"]
            loca['Time'] = loca.index.values
            loca['day'] = pd.to_datetime(loca.index, infer_datetime_format=True)
            loca["Location"] = ct + ", " + st
            #print(self.ts_data.head())
            loca = loca[loca["Cases"] > 0]
            print(loca.head())
            self.data.to_csv("working.csv")
            self.ts_data = self.ts_data.append(loca)
            print(self.ts_data.head())
            self.make_time_plot()

        return fun

        




win = HeaderBarWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

