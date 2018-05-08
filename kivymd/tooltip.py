from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import  ListProperty,BooleanProperty,StringProperty
from kivymd.label import MDLabel
from kivy.factory import Factory
Builder.load_string("""
<MDToolTipLabel@Label>:
    id:tooltip
    size_hint: None, None
    size: (self.texture_size[0]+10,self.texture_size[1]+10)
    pos_hint:{'bottom':0}
    canvas.before:
        Color: 
            rgb: 0.2, 0.2, 0.2                                                                                                           
        Rectangle:
            size: self.size
            pos: self.pos
""")


class ToolTipBehavior(object):
    tooltip_text = StringProperty()
    open = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(ToolTipBehavior, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.open = False

    def update_tooltip(self, **kwargs):
        self.all_data = kwargs
        self.tooltip_text = kwargs.get('tooltip_text') if kwargs.get('tooltip_text') != None else self.tooltip_text
        self.tooltip = Factory.MDToolTipLabel(text=self.tooltip_text)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]

        inside = self.collide_point(*self.to_widget(*pos))

        if inside and not self.open and self.tooltip_text != '' and not self.disabled:
            self.tooltip = Factory.MDToolTipLabel(text=self.tooltip_text)
            # self.get_root_window().set_system_cursor("hand")
            self.tooltip.pos = (pos[0],pos[1]-40)
            Clock.schedule_once(self.display_tooltip, 1)
            self.open = True
        elif not inside and self.open:
            Clock.unschedule(self.display_tooltip)
            self.close_tooltip()
        elif inside and self.open:
            self.tooltip.pos = (pos[0],pos[1]-40)

    def close_tooltip(self, *args):
        self.open = False
        Window.remove_widget(self.tooltip)

    def display_tooltip(self, *args):
        Window.add_widget(self.tooltip)
        Clock.schedule_once(self.close_tooltip, 1)
