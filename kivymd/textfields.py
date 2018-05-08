# -*- coding: utf-8 -*-
import sys
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.metrics import sp
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.properties import OptionProperty, ListProperty
from kivy.uix.textinput import TextInput
from kivymd.label import MDLabel
from kivymd.theming import ThemableBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.behaviors import FocusBehavior

Builder.load_string('''
<MDTextField>:
    canvas.before:
        Clear
        Color:
            rgba: self.line_color_normal
        Line:
            points: self.x, self.y + dp(16), self.x + self.width, self.y + dp(16)
            width: 1
            dash_length: dp(3)
            dash_offset: 2 if self.disabled else 0
        Color:
            rgba: self._current_line_color
        Rectangle:
            size: self._line_width, dp(2)
            pos: self.center_x - (self._line_width / 2), self.y + dp(16)
        Color:
            rgba: self._current_error_color
        Rectangle:
            texture: self._msg_lbl.texture
            size: self._msg_lbl.texture_size
            pos: self.x, self.y-dp(5)
        Color:
            rgba: self._current_right_lbl_color
        Rectangle:
            texture: self._right_msg_lbl.texture
            size: self._right_msg_lbl.texture_size
            pos: self.width-self._right_msg_lbl.texture_size[0]+dp(45), self.y
        Color:
            rgba: (self._current_line_color if self.focus and not self.cursor_blink else (0, 0, 0, 0))
        Rectangle:
            pos: [int(x) for x in self.cursor_pos]
            size: 1, -self.line_height
        Color:
            rgba: self._current_hint_text_color
        Rectangle:
            texture: self._hint_lbl.texture
            size: self._hint_lbl.texture_size
            pos: self.x, self.y + self.height - self._hint_y
        Color:
            rgba: self.disabled_foreground_color if self.disabled else \
            (self.hint_text_color if not self.text and not self.focus else self.foreground_color)

    font_name: 'Roboto'
    foreground_color: app.theme_cls.text_color
    font_size: sp(16)
    bold: False
    padding: 0, dp(16), 0, dp(10)
    multiline: False
    size_hint_y: None
    height: self.minimum_height + dp(8)

<TextfieldLabel>
    disabled_color: self.theme_cls.disabled_hint_text_color
    text_size: (self.width, None)
    mipmap:True
    markup:True
    shorten:True
    
<MDSelect>:
    size_hint_y:None
    height:dp(40)
    pos:self.pos
    text:selected_field.text
    
    MDTextField:
        id:selected_field
        size_hint_x:1
        write_tab: False
        hint_text:root.hint_text
        helper_text:root.helper_text
        readonly:root.readonly
        text:root.text
        on_text:root.on_text(self,self.text)
        on_text_validate:root.on_select()
        on_focus:root.on_focus(self,self.focus)
    BoxLayout:
        opacity:0 if selected_field.focus else self.parent.opacity
        canvas.before:
            Color:
                rgba:(1,1,1,1)
            Rectangle:
                size:self.size
                pos:self.pos    
        padding:0,dp(20),0,dp(20)
        size_hint:None,None
        width:dp(30)
        pos_hint:{'right':1,'top':1}
        height:dp(20)
        MDLabel:
            id: drop_down
            pos_hint:{'center_y':0.5}
            font_style: 'Icon'
            text: u"{}".format(md_icons['menu-down'])
            # halign: 'right'
            # valign: 'middle'
           
            
           
    
''')


class FixedHintTextInput(TextInput):
    instances=[]
    count =0
    hint_text = StringProperty('')



    def on__hint_text(self, instance, value):
        pass

    def _refresh_hint_text(self):
        pass


class TextfieldLabel(MDLabel):

    def on_theme_text_color(self, instance, value):
        t = self.theme_cls
        op = self.opposite_colors
        setter = self.setter('color')
        t.unbind(**self._currently_bound_property)
        c = {}
        if value == 'Primary':
            c = {'text_color' if not op else 'opposite_text_color': setter}
            t.bind(**c)
            self.color = t.text_color if not op else t.opposite_text_color
        elif value == 'Secondary':
            c = {'secondary_text_color' if not op else
                 'opposite_secondary_text_color': setter}
            t.bind(**c)
            self.color = t.secondary_text_color if not op else \
                t.opposite_secondary_text_color
        elif value == 'Hint':
            c = {'disabled_hint_text_color' if not op else
                 'opposite_disabled_hint_text_color': setter}
            t.bind(**c)
            self.color = t.disabled_hint_text_color if not op else \
                t.opposite_disabled_hint_text_color
        elif value == 'Error':
            c = {'error_color': setter}
            t.bind(**c)
            self.color = t.error_color
        elif value == 'Custom':
            self.color = self.text_color if self.text_color else (0, 0, 0, 1)
        self._currently_bound_property = c


class MDTextField(ThemableBehavior, FixedHintTextInput):

    helper_text = StringProperty("This field is required")
    helper_text_mode = OptionProperty('none', options=['none', 'on_error', 'persistent', 'on_focus'])

    max_text_length = NumericProperty(None)
    required = BooleanProperty(False)

    color_mode = OptionProperty('primary', options=['primary', 'accent', 'custom'])
    line_color_normal = ListProperty()
    line_color_focus = ListProperty()
    error_color = ListProperty()

    error = BooleanProperty(False)
    _text_len_error = BooleanProperty(False)

    _hint_lbl_font_size = NumericProperty(sp(16))
    _hint_y = NumericProperty(dp(38))
    _line_width = NumericProperty(0)
    _current_line_color = ListProperty([0.0, 0.0, 0.0, 0.0])
    _current_error_color = ListProperty([0.0, 0.0, 0.0, 0.0])
    _current_hint_text_color = ListProperty([0.0, 0.0, 0.0, 0.0])
    _current_right_lbl_color = ListProperty([0.0, 0.0, 0.0, 0.0])

    def __init__(self, **kwargs):

        self._msg_lbl = TextfieldLabel(font_style='Caption',
										halign='left',
										valign='middle',
										text=self.helper_text)
        self._right_msg_lbl = TextfieldLabel(font_style='Caption',
                                             halign='right',
                                             valign='middle',
                                             text="")

        self._hint_lbl = TextfieldLabel(font_style='Subhead',
                                        halign='left',
                                        valign='middle')

        super(MDTextField, self).__init__(**kwargs)
        self.line_color_normal = [0.0,0.0,0.0,0.07]
        self.line_color_focus = self.theme_cls.primary_color
        self.error_color = self.theme_cls.error_color

        self._current_hint_text_color = self.theme_cls.disabled_hint_text_color
        self._current_line_color = self.line_color_normal

        self.bind(helper_text=self._set_msg,
                  hint_text=self._set_hint,
                  _hint_lbl_font_size=self._hint_lbl.setter('font_size'),
                  helper_text_mode=self._set_message_mode,
                  max_text_length=self._set_max_text_length,
                  text=self.on_text)
        self.theme_cls.bind(primary_color=self._update_primary_color,
                            theme_style=self._update_theme_style,
                            accent_color=self._update_accent_color)
        self.has_had_text = False



    def _update_colors(self, color):
        self.line_color_focus = color
        if not self.error and not self._text_len_error:
            self._current_line_color = color
            if self.focus:
                self._current_line_color = color


    def _update_accent_color(self, *args):
        if self.color_mode == "accent":
            self._update_colors(self.theme_cls.accent_color)

    def _update_primary_color(self, *args):
        if self.color_mode == "primary":
            self._update_colors(self.theme_cls.primary_color)

    def _update_theme_style(self, *args):
        self.line_color_normal = self.theme_cls.divider_color
        if not any([self.error, self._text_len_error]):
            if not self.focus:
                self._current_hint_text_color = self.theme_cls.disabled_hint_text_color
                self._current_right_lbl_color = self.theme_cls.disabled_hint_text_color
                if self.helper_text_mode == "persistent":
                    self._current_error_color = self.theme_cls.disabled_hint_text_color

    def on_width(self, instance, width):
        if any([self.focus, self.error, self._text_len_error]) and instance is not None:
            self._line_width = width
        self._msg_lbl.width = self.width
        self._right_msg_lbl.width = self.width
        self._hint_lbl.width = self.width

    def on_focus(self, *args):
        self.bind(error=self.on_focus)
        Animation.cancel_all(self, '_line_width', '_hint_y',
                             '_hint_lbl_font_size')
        if self.max_text_length is None:
            max_text_length = sys.maxsize
        else:
            max_text_length = self.max_text_length
        if len(self.text) > max_text_length or all([self.required, len(self.text) == 0, self.has_had_text]):
            self._text_len_error = True
        if self.error or all([self.max_text_length is not None and len(self.text) > self.max_text_length]):
            has_error = True
        else:
            if all([self.required, len(self.text) == 0, self.has_had_text]):
                has_error = True
            else:
                has_error = False

        if self.focus:
            self.has_had_text = True
            Animation.cancel_all(self, '_line_width', '_hint_y',
                                 '_hint_lbl_font_size')
            if len(self.text) == 0:
                Animation(_hint_y=dp(14),
                          _hint_lbl_font_size=sp(12), duration=.2,
                          t='out_quad').start(self)
            Animation(_line_width=self.width, duration=.2, t='out_quad').start(self)
            if has_error and len(self.text)>0:
                Animation(duration=.2, _current_hint_text_color=self.error_color,
                          _current_right_lbl_color=self.error_color,
                          _current_line_color=self.error_color).start(self)
                if self.helper_text_mode == "on_error" and (self.error or self._text_len_error):
                    Animation(duration=.2, _current_error_color=self.error_color).start(self)
                elif self.helper_text_mode == "on_error" and not self.error and not self._text_len_error:
                    Animation(duration=.2, _current_error_color=(0, 0, 0, 0)).start(self)
                elif self.helper_text_mode == "persistent":
                    Animation(duration=.2, _current_error_color=self.theme_cls.disabled_hint_text_color).start(self)
                elif self.helper_text_mode == "on_focus":
                    Animation(duration=.2, _current_error_color=self.theme_cls.disabled_hint_text_color).start(self)
            else:
                Animation(duration=.2, _current_hint_text_color=self.line_color_focus,
                          _current_right_lbl_color=self.theme_cls.disabled_hint_text_color,_current_line_color=self.line_color_focus).start(self)
                if self.helper_text_mode == "on_error":
                    Animation(duration=.2, _current_error_color=(0, 0, 0, 0)).start(self)
                if self.helper_text_mode == "persistent":
                    Animation(duration=.2, _current_error_color=self.theme_cls.disabled_hint_text_color).start(self)
                elif self.helper_text_mode == "on_focus":
                    Animation(duration=.2, _current_error_color=self.theme_cls.disabled_hint_text_color).start(self)
        else:
            if len(self.text) == 0:
                Animation(_hint_y=dp(38),
                          _hint_lbl_font_size=sp(16), duration=.2,
                          t='out_quad').start(self)
            if has_error:
                Animation(duration=.2, _current_line_color=self.error_color,
                          _current_hint_text_color=self.error_color,
                          _current_right_lbl_color=self.error_color).start(self)
                if self.helper_text_mode == "on_error" and (self.error or self._text_len_error):
                    Animation(duration=.2, _current_error_color=self.error_color).start(self)
                elif self.helper_text_mode == "on_error" and not self.error and not self._text_len_error:
                    Animation(duration=.2, _current_error_color=(0, 0, 0, 0)).start(self)
                elif self.helper_text_mode == "persistent":
                    Animation(duration=.2, _current_error_color=self.theme_cls.disabled_hint_text_color).start(self)
                elif self.helper_text_mode == "on_focus":
                    Animation(duration=.2, _current_error_color=(0, 0, 0, 0)).start(self)
            else:
                Animation(duration=.2, _current_line_color=self.line_color_focus,
                          _current_hint_text_color=self.theme_cls.disabled_hint_text_color,
                          _current_right_lbl_color=(0, 0, 0, 0)).start(self)
                if self.helper_text_mode == "on_error":
                    Animation(duration=.2, _current_error_color=(0, 0, 0, 0)).start(self)
                elif self.helper_text_mode == "persistent":
                    Animation(duration=.2, _current_error_color=self.theme_cls.disabled_hint_text_color).start(self)
                elif self.helper_text_mode == "on_focus":
                    Animation(duration=.2, _current_error_color=(0, 0, 0, 0)).start(self)

                Animation(_line_width=0, duration=.2, t='out_quad').start(self)

    def on_text(self, instance, text):
        if len(text) > 0 or self.focus:
            self.has_had_text = True
            Animation(_hint_y=dp(14),
                      _hint_lbl_font_size=sp(12), duration=.2,
                      t='out_quad').start(self)
        else:
            self.has_had_text = False
            Animation(_hint_y=dp(38),
                      _hint_lbl_font_size=sp(16), duration=.2,
                      t='out_quad').start(self)

        if self.max_text_length is not None:
            self._right_msg_lbl.text = "{}/{}".format(len(text), self.max_text_length)
            max_text_length = self.max_text_length
        else:
            max_text_length = sys.maxsize
        if len(text) > max_text_length or all([self.required, len(self.text) == 0, self.has_had_text]):
            self._text_len_error = True
        else:
            self._text_len_error = False
        if self.error or self._text_len_error:
            if self.focus:
                Animation(duration=.2, _current_hint_text_color=self.error_color,
                          _current_line_color=self.error_color).start(self)
                if self.helper_text_mode == "on_error" and (self.error or self._text_len_error):
                    Animation(duration=.2, _current_error_color=self.error_color).start(self)
                if self._text_len_error:
                    Animation(duration=.2, _current_right_lbl_color=self.error_color).start(self)
        else:
            if self.focus:
                Animation(duration=.2, _current_right_lbl_color=self.theme_cls.disabled_hint_text_color).start(self)
                Animation(duration=.2, _current_hint_text_color=self.line_color_focus,
                          _current_line_color=self.line_color_focus).start(self)
                if self.helper_text_mode == "on_error":
                    Animation(duration=.2, _current_error_color=(0, 0, 0, 0)).start(self)
        if len(self.text) > 0 and not self.focus:
            self._hint_y = dp(14)
            self._hint_lbl_font_size = sp(12)

    def on_text_validate(self):
        self.has_had_text = True
        if self.max_text_length is None:
            max_text_length = sys.maxsize
        else:
            max_text_length = self.max_text_length
        if len(self.text) > max_text_length or all([self.required, len(self.text) == 0, self.has_had_text]):
            self._text_len_error = True

    def _set_hint(self, instance, text):
        self._hint_lbl.text = text

    def _set_msg(self, instance, text):
        self._msg_lbl.text = text
        self.helper_text = text

    def _set_message_mode(self, instance, text):
        self.helper_text_mode = text
        if self.helper_text_mode == "persistent":
            Animation(duration=.1, _current_error_color=self.theme_cls.disabled_hint_text_color).start(self)

    def _set_max_text_length(self, instance, length):
        self.max_text_length = length
        self._right_msg_lbl.text = "{}/{}".format(len(self.text), length)

    def on_color_mode(self, instance, mode):
        if mode == "primary":
            self._update_primary_color()
        elif mode == "accent":
            self._update_accent_color()
        elif mode == "custom":
            self._update_colors(self.line_color_focus)

    def on_line_color_focus(self, *args):
        if self.color_mode == "custom":
            self._update_colors(self.line_color_focus)

    def reset(self):
        self.text=''
        self.helper_text=''
        Animation(duration=.2,_current_right_lbl_color=(0, 0, 0, 0), _current_line_color=self.line_color_normal,_current_error_color=self.theme_cls.disabled_hint_text_color,
                  _current_hint_text_color=self.theme_cls.disabled_hint_text_color,
                  ).start(self)






class MDSelect(RelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
    icon = StringProperty()
    focus = BooleanProperty(False)
    selected_value = StringProperty('')
    helper_text = StringProperty('')
    readonly = BooleanProperty(True)
    multiselect = BooleanProperty(False)
    options = ListProperty()
    footer = StringProperty()
    header = StringProperty()
    error = BooleanProperty(False)
    isfooterclicked = BooleanProperty(False)
    isheaderclicked = BooleanProperty(False)

    def __init__(self,**kwargs):
        super(MDSelect,self).__init__(**kwargs)
        self.bind(error=self.on_error)
        self.bind(focus=self.reverse_focus)

    def on_focus(self,instance,value):
        self.focus=value

    def on_touch_up(self,touch):
        if self.collide_point(touch.x,touch.y):
            self.on_select()


    def reverse_focus(self,instance,value):
        self.ids.selected_field.focus=self.focus

    def on_press(self, *args):
        if self.focus==False:
            self.focus = True

    def on_error(self,*args):
        self.ids.selected_field.error=self.error

    def on_text(self, instance, text):
        if isinstance(instance,MDTextField) and text!='':
            return True
        else:
            return False

    def option_selected(self,*args):
        selected_list =','.join(map(str,[i.text for i in self.list.selected_nodes]))
        if self.list.selected_nodes!=[] and self.multiselect==False:
            self.text=self.list.selected_nodes[0].text
        elif self.multiselect==True:
            self.text = selected_list

    def on_select(self,*args):
        from kivymd.option import MDOption
        self.focus = self.ids.selected_field.focus
        self.list = MDOption(options=self.options,multiselect=self.multiselect, scroll_count=1, header=self.header, footer=self.footer)
        self.list.bind(selected_nodes=self.option_selected)
        self.list.open(self)

    def on_footer_clicked(self,*args):
        self.isfooterclicked = not self.isfooterclicked

    def on_header_clicked(self,*args):
        self.isheaderclicked = not self.isheaderclicked

    def reset(self):
        self.ids.selected_field.reset()

