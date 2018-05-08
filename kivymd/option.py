# -*- coding: utf-8 -*-

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.metrics import dp
from kivy.properties import NumericProperty, ListProperty, OptionProperty, \
    StringProperty, ObjectProperty,BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
import kivymd.material_resources as m_res
from kivymd.theming import ThemableBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import CompoundSelectionBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.scrollview import ScrollView
from kivymd.card import MDCard
from kivy.clock import Clock
from kivymd.button import MDFlatButton
from kivymd.elevationbehavior import RectangularElevationBehavior
from kivy.uix.button import Button

Builder.load_string('''
#:import STD_INC kivymd.material_resources.STANDARD_INCREMENT
#:import MDCheckbox kivymd.selectioncontrols.MDCheckbox
<Box>
    size_hint:(None,None)
    height:self.minimum_height

<ExtraOption>
    size_hint_x:1
    size_hint_y: None
    height: dp(48)
    color:app.theme_cls.primary_color
    background_normal:''
    background_down:''
    background_color:app.theme_cls.accent_color if self.state=='normal' else app.theme_cls.accent_dark 
    
<MDMultiSelectItem>
    size_hint_y: None
    height: dp(48)
    padding: dp(16), 0
    checkbox:chkbox
    canvas.before:
        Color:
            rgba: root.background_color
        Rectangle:
            size: self.size
            pos: self.pos
    MDCheckbox:
        id:chkbox
        size_hint:    None, None
        size:        dp(25), dp(48)        
    MDLabel:
        id:item_text        
        text: root.text
        theme_text_color: 'Primary'           

<MDOptionItem>
    size_hint_y: None
    height: dp(48)
    padding: dp(16), 0
    canvas.before:
        Color:
            rgba: root.background_color
        Rectangle:
            size: self.size
            pos: self.pos
    MDLabel:        
        text: root.text
        theme_text_color: 'Primary'
         
                    
<MDOption>:
    size_hint_y:None
    height:self.minimum_height
    cols:1
    
<OptionScroll>:
    size_hint_y:None
    height:dp(48)*4
                
                        
''')


class Box(BoxLayout):
    def __init__(self,**kwargs):
        super(Box,self).__init__(**kwargs)


class ExtraOption(Button):
    def __init__(self,**kwargs):
        super(ExtraOption,self).__init__(**kwargs)


class OptionScroll(ScrollView):
    def __init__(self,**kwargs):
        super(OptionScroll,self).__init__(**kwargs)

class MDOption(FocusBehavior, CompoundSelectionBehavior, GridLayout):
    cols = NumericProperty(1)
    options = ListProperty()
    header = StringProperty()
    footer = StringProperty()
    keyboard_select = BooleanProperty(True)
    multiselect = BooleanProperty(False)
    parent_obj=ObjectProperty()
    container = OptionScroll()
    panel = MDCard(orientation='vertical',size_hint=(None,None))

    def __init__(self,**kwargs):
        super(MDOption,self).__init__(**kwargs)
        self.bind(focus=self.out)
        self.add_options()
        self.bind(selected_nodes=self.changeInSelected)

    def changeInSelected(self,*args):
        if self.multiselect:
            for i in args[1]:
                i.checkbox.active=True

    def add_options(self):
        self.clear_widgets()
        for i,item in enumerate(self.options):
            c = MDOptionItem(text=str(item)) if self.multiselect == False else MDMultiSelectItem(text=str(item))
            c.bind(on_touch_down=self.do_touch)
            self.add_widget(c)
            self.focus = True

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        try:
            if keycode[1]=='enter':
                self.parent_obj.text = self.selected_nodes[0].text if self.multiselect==False else ','.join(map(str,[i.text for i in self.selected_nodes]))
                self.dismiss()
                self.parent_obj.focus=True
            if keycode[1]=='tab':
                self.dismiss()
                self.parent_obj.focus = True
            if keycode[1] == 'esc':
                self.dismiss()
            if super(MDOption, self).keyboard_on_key_down(
                    window, keycode, text, modifiers):
                return True
            if self.select_with_key_down(window, keycode, text, modifiers):
                return True
            return False
        except Exception as e:
            self.dismiss()

    def keyboard_on_key_up(self, window, keycode):
        if super(MDOption, self).keyboard_on_key_up(window, keycode):
            return True
        if self.select_with_key_up(window, keycode):
            return True
        return False

    def goto_node(self, key, last_node, last_node_idx):
        ''' This function is used to go to the node by typing the number
        of the text of the button.
        '''
        node, idx = super(MDOption, self).goto_node(key, last_node,
                                                          last_node_idx)
        if node != last_node:
            self.container.scroll_to(node)
            return node, idx

        items = list(enumerate(self.get_selectable_nodes()))
        '''If self.nodes_order_reversed (the default due to using
        self.children which is reversed), the index is counted from the
        starts of the selectable nodes, like normal but the nodes are traversed
        in the reverse order.
        '''
        # start searching after the last selected node
        if not self.nodes_order_reversed:
            items = items[last_node_idx + 1:] + items[:last_node_idx + 1]
        else:
            items = items[:last_node_idx][::-1] + items[last_node_idx:][::-1]

        for i, child in items:
            if child.text.startswith(key):
                self.container.scroll_to(child)
                return child, i
        self.container.scroll_to(node)
        return node, idx

    def select_node(self, node):
        from kivy.app import App
        root=App.get_running_app()
        node.background_color = root.theme_cls.accent_light
        return super(MDOption, self).select_node(node)

    def deselect_node(self, node):
        if self.multiselect:
            node.checkbox.active=False
        node.background_color = (1, 1, 1, 1)
        super(MDOption, self).deselect_node(node)


    def do_touch(self, instance, touch):
        if ('button' in touch.profile and touch.button in
                ('scrollup', 'scrolldown', 'scrollleft', 'scrollright')) or\
                instance.collide_point(*touch.pos):
            if self.multiselect == False:
                self.select_with_touch(instance, touch)
                self.dismiss()
            else:
                pass
                # self.select_with_touch(instance, touch)
                # instance.checkbox.active=not instance.checkbox.active
                if instance.checkbox.active==True:
                    self.deselect_node(instance)
                elif instance.checkbox.active==False:
                    self.select_node(instance)




        else:
            return False
        return True

    def open(self,instance):
        self.panel.clear_widgets()
        self.container.clear_widgets()
        self.parent_obj =instance
        self.size_hint_x = None
        self.width =instance.width
        self.panel.width =instance.width
        minimum_height = dp(48) * 4 if len(self.options) > 4 else dp(48) * len(self.options)
        if self.header!='':
            header_button =ExtraOption(text=self.header)
            header_button.bind(on_press=self.parent_obj.on_header_clicked)
            header_button.bind(on_touch_down=self.out)
            self.panel.add_widget(header_button)
        if len(self.options)>0:
            self.container.add_widget(self)
            self.container.height = minimum_height
            self.panel.add_widget(self.container)
        if self.footer != '':
            footer_button = ExtraOption(text=self.footer)
            footer_button.bind(on_press=self.parent_obj.on_footer_clicked)
            footer_button.bind(on_touch_down=self.out)
            self.panel.add_widget(footer_button)

        if len(self.options)<4:
            self.panel.pos = instance.to_window(instance.x, instance.y-minimum_height)
        else:
            self.panel.pos = instance.to_window(instance.x, instance.y - (minimum_height-dp(48)))
        if self.options or self.footer or self.header:
            Window.add_widget(self.panel)
            if self.footer or self.header and not self.options:
                self.panel.height = dp(48)

    def out(self,*args):
        if self.focus==True:
            pass
        else:
            self.dismiss()

    def dismiss(self,*args):
        Window.remove_widget(self.panel)


class MDOptionItem(RecycleDataViewBehavior, ButtonBehavior, BoxLayout):
    background_color = ListProperty([1,1,1,1])
    text = StringProperty()


class MDMultiSelectItem(RecycleDataViewBehavior, ButtonBehavior, BoxLayout):
    checkbox = ObjectProperty()
    background_color = ListProperty([1, 1, 1, 1])
    text = StringProperty()




