import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

from matplotlib.figure import Figure
import matplotlib.cm as cm
import matplotlib.pyplot as plt

from numpy import arange, pi, random, linspace

#Possibly this rendering backend is broken currently
#from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
import geopandas
import pandas as pd
import io
from PIL import Image
    


class HeaderBarWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="HeaderBar Demo")
        self.set_border_width(10)
        self.set_default_size(400, 200)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "HeaderBar example"
        self.set_titlebar(hb)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")


        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(1000)

        
        gdf = pd.read_pickle("flu_cov_map.pkl")
        fig, ax = plt.subplots(1, 1)
        gdf.plot(column='covid19', ax=ax, legend=True)
        gdf.geometry
        cid = fig.canvas.mpl_connect('button_press_event', Gtk.main_quit)
        #canvas = FigureCanvas(fig)
        #stack.add_titled(canvas, "check", "Check Button")

        #buf = io.BytesIO()
        #fig.savefig(buf, format='png', dpi = 97)
        #buf.seek(0)
        #pil_img = deepcopy(Image.open(buf))
        # buf.close()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        im = Image.open(buf)
        buf.close()
        #self.picturearea = self.builder.get_object('imagefield')
        image = Gtk.Image()
        canvas = FigureCanvas(im)
        stack.add_titled(canvas, "check", "Check Button")
        
        label = Gtk.Label()
        label.set_markup("<big>A fancy label</big>")
        stack.add_titled(label, "label", "A label")

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        box.pack_start(stack_switcher, True, True, 0)

        hb.pack_start(box)
        
        self.add(stack)


win = HeaderBarWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

