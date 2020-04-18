import gi
import pandas as pd
import geopandas as gpd
import numpy as np
import geoplot as gplt
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
        self.set_default_size(400, 200)

        data = gpd.read_file('data_set2/full_data.shp')
        #for i in data[data[data.columns[35]] == 1].T.iterrows():
        #    print(i)

        # self.days = data.columns[35:-1]
        # self.days = data.columns[-10:-1]
        self.days = data.columns[35:36]
        # for d in self.days:
        #     data[d] = pd.to_numeric(data[d])
        self.active_ob = 0

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Contagion Viewer"
        self.set_titlebar(hb)

        embed = GtkChamplain.Embed()

        embed.set_size_request(640, 480)

        self.view = embed.get_view()
        self.view.set_reactive(True)
        self.view.connect('button-release-event', self.mouse_click_cb,
            self.view)

        self.view.set_property('kinetic-mode', True)
        self.view.set_property('zoom-level', 5)

        scale = Champlain.Scale()
        scale.connect_view(self.view)
        self.view.bin_layout_add(scale, Clutter.BinAlignment.START,
            Clutter.BinAlignment.END)

        license = self.view.get_license_actor()
        license.set_extra_text("Do what you want but I am RMFlynn")

        self.view.center_on(39.739, -104.984)

        self.obs = []
        for i, day in enumerate(self.days):
            self.obs.append(self.make_marker_layer(self.view, data, day))
            self.view.add_layer(self.obs[i])
            self.obs[i].hide_all_markers()

        self.path_layer = Champlain.PathLayer()

        liststore = Gtk.ListStore(int, str)
        for i, day in enumerate(self.days):
            liststore.append([i, str(day)])

        combo = Gtk.ComboBox()
        combo.set_model(liststore)
        cell = Gtk.CellRendererText()
        combo.pack_start(cell, False)
        combo.add_attribute(cell, 'text', 1)
        combo.connect("changed", self.toggle_layer)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(1000)

        combo.set_active(0)

        self.spinbutton = Gtk.SpinButton.new_with_range(0, 20, 1)
        self.spinbutton.connect("changed", self.zoom_changed)
        self.view.connect("notify::zoom-level", self.map_zoom_changed)
        self.spinbutton.set_value(5)
        

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

        box_r.pack_start(combo, True, True, 0)
        box_l.pack_start(self.spinbutton, True, True, 0)
        box_l.pack_end(stack_switcher, True, True, 0)

        hb.pack_start(box_r)
        hb.pack_end(box_l)
        
        self.add(stack)

    def make_stack():
        pass

    def add_node(self, path_layer, lat, lon):
        coord = Champlain.Coordinate.new_full(lat, lon)
        path_layer.add_node(coord)

    def mouse_click_cb(self, actor, event, view):
        x, y = event.x, event.y
        lon, lat = view.x_to_longitude(x), view.y_to_latitude(y)
        print("Mouse click at: %f %f" % (lat, lon))
        return True

    def zoom_changed(self, widget):
        self.view.set_property("zoom-level", self.spinbutton.get_value_as_int())

    def map_zoom_changed(self, widget, value):
        self.spinbutton.set_value(self.view.get_property("zoom-level"))

    def toggle_layer(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        id = model.get_value(iter, 0)
        #self.path_layer.show()
        #iter = widget.get_active_iter()
        #print(id)
        self.obs[self.active_ob].hide_all_markers()
        self.obs[id].show_all_markers()
        self.active_ob = id 
        #self.path_layer.hide()

    def zoom_in(self, widget):
        self.view.zoom_in()

    def zoom_out(self, widget):
        self.view.zoom_out()

    def make_marker_layer(self, view, data, day):
        for i in data[data[day] == 1].T.iterrows():
            print(i)
        orange = Clutter.Color.new(0xf3, 0x94, 0x07, 0xbb)
        layer = Champlain.MarkerLayer()
        
        max_case = np.amax(data[self.days].values)
        data = data.sort_values(by=[day], ascending=False)
        data = data[data[day] > 0]
        for i in data[data[day] == 1].T.iterrows():
            print(i)
        data['label'] = data[day].apply(str)
        data['size'] = (data[day]/(max_case/500)).apply(int)
        data['size'] = data['size'].apply(lambda x: 7 if x < 7 else x)
        
        # add colors based on size
        hue_dat = pd.DataFrame({
            'hue' : sns.color_palette("Reds_d", max(data['size'])), 
            'size' : list(range(max(data['size'])))
            })
        def multi(v):
            return v[0]*255, v[1]*255, v[2]*255
        
        hue_dat.hue = hue_dat.hue.apply(multi)
        hue_dat.hue = hue_dat.hue.apply(lambda x : Clutter.Color.new(*x, 150))
        data = pd.merge(data, hue_dat, on='size')
        for i in data[data[day] == 1].T.iterrows():
            print(i)
        
        for _, i in data.iterrows():
            point = Champlain.Point.new()
            x = i.geometry.centroid.representative_point().coords[:][0]
            point.set_color(i['hue'])
            point.set_size(i['size'])
            point.set_location(x[1], x[0])
            layer.add_marker(point)

        dat = data.head(3).copy()
        for _, i in dat.iterrows():
            label = Champlain.Label.new_with_text(i['label'] + "\n" + i['county_nam'] + " " + i['STNAME'])
            #x = i.geometry.centroid.representative_point().coords[:][0]
            x = i.geometry
            label.set_location(x[1], x[0])
            layer.add_marker(point)
            layer.add_marker(label)

        layer.show()
        return layer



win = HeaderBarWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

