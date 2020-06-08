# data stuff 
import pandas as pd
import numpy as np

# plot stuff
import matplotlib.pyplot as plt 
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
import seaborn as sea

# GTK stuff
import gi
gi.require_version('Champlain', '0.12')
gi.require_version('GtkChamplain', '0.12')
gi.require_version('GtkClutter', '1.0')
from gi.repository import GtkClutter, Clutter
GtkClutter.init([])  # Must be initialized before importing those:
from gi.repository import GObject, Gtk, Champlain, GtkChamplain, Pango

params = {"ytick.color" : "w",
          "xtick.color" : "w",
          "axes.labelcolor" : "w",
          "axes.edgecolor" : "w"}
plt.rcParams.update(params)

import os
import sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

class TimeWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Time Series")
        self.connect("delete-event", Gtk.main_quit)
        self.set_title( "Time Series" )
        self.fig = Figure(dpi=100)
        self.fig.patch.set_alpha(0)
        # self.fig.suptitle("The time series view will go here.", fontsize=14, fontweight='bold',color="white")
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.add(self.canvas)
        self.connect("destroy", self.hide)

    def make_time_plot(self, ts_data):
        self.add(self.canvas)
        self.set_size_request(800, 600)
        self.ax.clear()
        ts_data['Time'] = pd.to_datetime(ts_data['Time'])# - pd.to_timedelta(7, unit='d')
        ts_data = ts_data.sort_values('Time').reset_index( drop=True)
        ts_data['Time'] = ts_data['Time'].apply(lambda x : x.strftime('%b %-d'))
        print(ts_data)
        plot = sea.pointplot(y='Cases', 
                             x='Time', 
                             hue="Location",  
                             ax = self.ax, 
                             markers='o', 
                             data=ts_data)
        self.ax.xaxis.set_label_text("")
        self.ax.patch.set_alpha(0)
        #self.ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        for ind, label in enumerate(plot.get_xticklabels()):
            if ind % 10 == 0:  # every 10th label is kept
                label.set_visible(True)
            else:
                label.set_visible(False)
        self.fig.canvas.draw()
        self.show_all()
        print("figure made")

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

        #stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        #stack.set_transition_duration(1000)

        # self.noteBook = Gtk.Notebook();
        #self.noteBook.set_tab_pos(Gtk.POS_LEFT);
        #self.stack = Gtk.Stack()
        # self.noteBook.append_page(embed, Gtk.Label("Map View"))
        #noteBook.set_
        #self.stack.add_titled(embed, "Map", "Map View")

        box_r = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box_r.get_style_context(), "linked")

        box_l = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box_l.get_style_context(), "linked")

        box_r.pack_start(self.make_liststore_state(), True, True, 0)
        box_r.pack_start(self.make_liststore_day(), True, True, 0)
        box_l.pack_start(self.make_liststore_proportion(), True, True, 0)
        box_r.pack_start(self.spinbutton, True, True, 0)

        #canvas = self.make_time_series()
        #self.make_time_series()
        #self.make_time_series()
        self.time_vue = TimeWindow()

        #stack_switcher = Gtk.StackSwitcher()
        #stack_switcher.set_stack(self.stack)
        #box_l.pack_end(stack_switcher, True, True, 0)

        hb.pack_start(box_r)
        hb.pack_end(box_l)
        
        #self.add(self.stack)
        #self.add(self.noteBook)
        self.add(embed)

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


    def make_spin_zoom(self):
        self.spinbutton = Gtk.SpinButton.new_with_range(0, 20, 1)
        self.spinbutton.connect("changed", self.zoom_changed)
        self.view.connect("notify::zoom-level", self.map_zoom_changed)
        self.spinbutton.set_value(4)

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
        self.mark = pd.DataFrame()
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
        self.data['label'] = [Champlain.Label.new() for i in self.data.index]
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
        for _, i in self.mark.iterrows():
            # i.point.set_color(i[self.day + '_size'])
            if(self.proportion == 0):
                i['label'].set_text("{:,}".format(i[self.day]) + 
                                       " Cases, " + 
                                       "{:,}".format(i['pop']) + 
                                       " Pop\n" +
                                       i['county_name'] +
                                       ", " + 
                                       i['state_name'])
            elif(self.proportion == 1):
                i['label'].set_text("{:,}".format(i[self.day]) + 
                                       " Cases Per=mill, " + 
                                       "{:,}".format(i['pop']) + 
                                       " Pop\n" +
                                       i['county_name'] +
                                       ", " + 
                                       i['state_name'])

    def mark_function(self, ct, st, x1, x0):

        def fun(actor, event, view):
            #lb = Champlain.Label.new_with_text(ct + ", " + st)
            loca = self.data
            loca = loca[loca['state_name'] == st]
            loca = loca[loca['county_name'] == ct]
            for _, i in loca.iterrows():
                i['label'].set_location(x1, x0)
                # i.point.set_color(i[''])
                if(self.proportion == 0):
                    i['label'].set_text("{:,}".format(i[self.day]) + 
                                           " Cases, " + 
                                           "{:,}".format(i['pop']) + 
                                           " Pop\n" +
                                           i['county_name'] +
                                           ", " + 
                                           i['state_name'])
                elif(self.proportion == 1):
                    i['label'].set_text("{:,}".format(i[self.day]) + 
                                           " Cases Per=mill, " + 
                                           "{:,}".format(i['pop']) + 
                                           " Pop\n" +
                                           i['county_name'] +
                                           ", " + 
                                           i['state_name'])
                self.marker_layer.add_marker(i['label'])
            self.mark = self.mark.append(loca)
            loca = loca[self.days].T
            loca.columns = ["Cases"]
            loca['Time'] = loca.index.values
            loca['day'] = pd.to_datetime(loca.index, infer_datetime_format=True)
            loca["Location"] = ct + ", " + st
            #print(self.ts_data.head())
            loca = loca[loca["Cases"] > 0]
            #print(loca.head())
            self.data.to_csv("working.csv")
            self.ts_data = self.ts_data.append(loca)
            # print(self.ts_data.head())
            self.time_vue.make_time_plot(self.ts_data)

        return fun

        




win = HeaderBarWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

