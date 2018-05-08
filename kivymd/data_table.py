# -*- coding: utf-8 -*-
import hashlib
import json
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BoundedNumericProperty, ListProperty, NumericProperty, ObjectProperty, \
    OptionProperty, \
    ReferenceListProperty, StringProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.backgroundcolorbehavior import SpecificBackgroundColorBehavior
from kivymd.icon_definitions import md_icons
from kivymd.label import MDLabel
from kivymd.ripplebehavior import RectangularRippleBehavior
from kivymd.selectioncontrols import MDCheckbox
from kivymd.theming import ThemableBehavior
from kivymd.button import MDIconButton
from kivy.uix.scrollview import ScrollView

Builder.load_string('''
#:import NDBadgeLabel kivymd.navigationdrawer.NDBadgeLabel 
#:import MDIconButton kivymd.button.MDIconButton
<MDDataTable>:
    size_hint_y: None
    height: self._min_list_height
    padding: 0, self._list_vertical_padding
    canvas:
        Color:
            rgba: self.md_bg_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
        Color:
            rgba: self.theme_cls.bg_light


<BaseCellLabel>
    shorten: False if root.fullfilled and len(self.text)<20 else True 
    padding: dp(8), 0
    canvas:
        Color:
            rgba: self.theme_cls.divider_color if root.divider is not None else (0, 0, 0, 0)
        Line:
            points: (root.x ,root.y, root.x+self.width, root.y)\
                    if root.divider == 'Full' else\
                    (root.x+root._txt_left_pad, root.y,\
                    root.x+self.width-root._txt_left_pad-root._txt_right_pad,\
                    root.y)

<HeaderLabel>
    canvas:
        Color:
            rgba: self.theme_cls.divider_color if root.divider is not None else (0, 0, 0, 0)
        Line:
            points: (root.x ,root.y, root.x+self.width, root.y)\
                if root.divider == 'Full' else\
                (root.x+root._txt_left_pad, root.y,\
                root.x+self.width-root._txt_left_pad-root._txt_right_pad,\
                root.y)
    size_hint_y: None
    theme_text_color: 'Secondary'
    text_color: 'Secondary'
    orientation: 'horizontal'
    padding: dp(8), 0
    MDLabel:
        shorten: True
        id: _text
        text: root.text
        theme_text_color: 'Secondary'
    NDBadgeLabel:
        id: _badge
        text: root.badge_text
        halign: 'right'
        valign: 'middle'
        font_name: 'Icons'
        font_style: 'Icon'
        font_size: 16
        theme_text_color: 'Hint'
        text_color: 'Hint'

<RowLabel>
    bgcolor: 1, 1, 1, 1
    theme_text_color: 'Primary'
    canvas.before:
        Color:
            rgba: self.bgcolor
        Rectangle:
            pos: self.pos
            size: self.size

<ItemCheckbox>
    canvas:
        Color:
            rgba: self.theme_cls.divider_color if root.divider is not None else (0, 0, 0, 0)
        Line:
            points: (root.x ,root.y, root.x+self.width, root.y)\
                    if root.divider == 'Full' else\
                    (root.x+root._txt_left_pad, root.y,\
                    root.x+self.width-root._txt_left_pad-root._txt_right_pad,\
                    root.y)
    size_hint: .5,.5
    
<ActionColumn>:
    canvas:
        Color:
            rgba: self.theme_cls.divider_color if root.divider is not None else (0, 0, 0, 0)
        Line:
            points: (root.x ,root.y, root.x+self.width, root.y)\
                if root.divider == 'Full' else\
                (root.x+root._txt_left_pad, root.y,\
                root.x+self.width-root._txt_left_pad-root._txt_right_pad,\
                root.y)
    size_hint: None,None
    size:(self.size[0],self.minimum_height)
    disabled:root.disabled


<MDTableSimple>:
    cols:len(root.col_sequence)

<CellLayout>:
    MDLabel:
        text:root.text
        font_style:root.font_style
        halign:root.halign
    MDSeparator:
        height: dp(1)    
        
            


''')

counter = 0


class CellLayout(BoxLayout):
    orientation = 'vertical'
    text = StringProperty()
    font_style = StringProperty('Subhead')
    halign = StringProperty('left')
    def __init__(self,**kwargs):
        super(CellLayout,self).__init__(**kwargs)
        try:
            if float(self.text):
                self.halign = 'center'
            elif self.text=='0' or self.text=='0.0':
                self.halign = 'center'
        except:
            self.halign ='left'


class MDTableSimple(GridLayout):
    data = ListProperty()
    col_sequence = ListProperty()
    sorted_by = StringProperty()
    font_style =StringProperty('Subhead')
    child_height =NumericProperty(0)
    def __init__(self,**kwargs):
        super(MDTableSimple,self).__init__(**kwargs)

    def setData(self,*args):
        self.clear_widgets()
        try:
            for item in self.data:
                for header in self.col_sequence:
                    if self.child_height:
                        self.add_widget(CellLayout(text = item[header],font_style=self.font_style,size_hint_y=None,height=self.child_height))
                    else:
                        self.add_widget(CellLayout(text = item[header],font_style=self.font_style))
        except Exception as e:
            print("Exception while setData Error: ",str(e))


class ActionColumn(BoxLayout):

    theme_cls = App.get_running_app().theme_cls
    divider = OptionProperty('Full', options=['Full', 'Inset', None])
    disabled = BooleanProperty(True)
    text=StringProperty('')
    def __init__(self,**kwargs):
        super(ActionColumn,self).__init__(**kwargs)





class ItemCheckbox(MDCheckbox):
    divider = OptionProperty('Full', options=['Full', 'Inset', None])


class BaseCellLabel(MDLabel, ThemableBehavior):
    '''
    Base class representing a Cell in the Data Table
    '''
    _txt_top_pad = NumericProperty(dp(16))
    _txt_bot_pad = NumericProperty(dp(15))  # dp(20) - dp(5)
    '''The top and bottom padding for label'''

    fullfilled = BooleanProperty(False)

    _num_lines = 1
    '''Number of lines allowed.'''

    divider = OptionProperty('Full', options=['Full', 'Inset', None])
    '''The default divider that will be placed below every cell'''

    def __init__(self, **kwargs):
        super(BaseCellLabel, self).__init__(**kwargs)
        # Set default height of cell label to 40 dp
        self.height = dp(40)



class HeaderLabel(BoxLayout, RectangularRippleBehavior, ButtonBehavior, ThemableBehavior,
                  SpecificBackgroundColorBehavior):
    '''
        A variation of BaseCellLabel that uses different styling to represent a Header Cell
    '''

    divider = OptionProperty('Full', options=['Full', 'Inset', None])
    '''The default divider that will be placed below every cell'''

    badge_text = StringProperty(u"{}".format(md_icons['unfold-more']))
    '''The property to be used to display sorting icons with the header cells'''

    text = StringProperty()
    '''The text to be displayed inside the header cell'''

    _txt_top_pad = NumericProperty(dp(16))
    _txt_bot_pad = NumericProperty(dp(15))  # dp(20) - dp(5)
    '''The top and bottom padding for label'''
    grandparent = None


    def __init__(self, **kwargs):
        super(HeaderLabel, self).__init__(**kwargs)
        # Set default height of cell label to 40 dp
        self.height = dp(40)

    def on_release(self):
        self.grandparent = self.parent.parent

        """
        Performs sorting operation on header cell click
        """
        # Iterate over header data items and look for header selected for sort-by
        for index, item in enumerate(self.grandparent.data[0]):
            if str(item).__eq__(self.text):
                # Iterate over each header cell in data table and
                # check for corresponding label and change its icon
                for i, header_cell in enumerate(self.grandparent.headerGrid.children):
                    if header_cell.text.__eq__(item):
                        is_ascending = header_cell.badge_text.__eq__(
                            u"{}".format(md_icons['chevron-up']))
                        # Switch icons
                        if is_ascending:
                            header_cell.badge_text = u"{}".format(md_icons['chevron-down'])
                        else:
                            header_cell.badge_text = u"{}".format(md_icons['chevron-up'])
                        # Sort the list and repopulate
                        if self.grandparent is not None:
                            self.grandparent.sorted_column = index
                            self.grandparent.sorted_column_name = header_cell.text
                            self.grandparent.is_descending_sort = not is_ascending
                            self.grandparent.on_sort(self.grandparent.sorted_column_name, not is_ascending)
                        elif header_cell.parent.parent is not None:
                            header_cell.parent.parent.sorted_column = index
                            header_cell.parent.parent.sorted_column_name = header_cell.text
                            header_cell.parent.parent.is_descending_sort = not is_ascending
                            header_cell.parent.parent.on_sort(
                                header_cell.parent.parent.sorted_column_name, not is_ascending)
                    else:
                        # Reset all other button
                        header_cell.badge_text = u"{}".format(md_icons['unfold-more'])


class RowLabel(BaseCellLabel):
    '''
        A variation of BaseCellLabel that uses different styling to represent a Row Cell
    '''
    fullfilled = BooleanProperty(False)
    bgcolor = ListProperty()
    '''The background color for the cell'''

    def __init__(self, **kwargs):
        super(RowLabel, self).__init__(**kwargs)


class MDDataTable(BoxLayout, ThemableBehavior):
    fullfilled = BooleanProperty(False)
    '''to make content shorten of fullfilled'''

    headerGrid = ObjectProperty()
    bodyGrid = ObjectProperty()
    scroll = ObjectProperty()
    orientation = 'vertical'
    size_hint = (1,1)
    pos_hint = {'top':1}
    '''
        A Material Design DataTable
    '''
    theme_cls = App.get_running_app().theme_cls
    ''' get running app theme class'''

    r = BoundedNumericProperty(1., min=0., max=1.)
    g = BoundedNumericProperty(1., min=0., max=1.)
    b = BoundedNumericProperty(1., min=0., max=1.)
    a = BoundedNumericProperty(0., min=0., max=1.)
    md_bg_color = ReferenceListProperty(r, g, b, a)
    '''The background color for the DataTable'''
    action=ListProperty(['edit','delete'])
    '''Add action buttons to every row'''

    _min_list_height = dp(16)
    '''The minimum height for row in the DataTable'''

    _list_vertical_padding = dp(8)
    '''The padding between rows in the DataTable'''

    data = ListProperty()
    '''The data structure for data in the DataTable'''

    paginated_data = ListProperty()
    '''The temporary data structure to hold data for pagination in the DataTable'''

    is_all_checked = BooleanProperty(False)
    '''The flag to indicate if all items are selected'''

    sorted_column = -1
    '''The index of the column currently used for sorting'''

    sorted_column_name = StringProperty()
    '''The name of the column currently used for sorting'''

    selected_id = StringProperty()
    '''The id of the selected row'''

    is_descending_sort = False
    '''The flag to indicate the direction of sorting (asc or dsc)'''

    sort_callback = ObjectProperty()
    '''Callback for sorting action'''

    isedit = BooleanProperty(False)
    '''The flag to idicate edit action'''

    isdelete = BooleanProperty(False)
    '''The flag to idicate delete action'''

    isinfo = BooleanProperty(False)
    '''The flag to idicate info action'''

    iscopy = BooleanProperty(False)
    '''The flag to indicate copy action'''

    selected_rows = ListProperty([])

    def __init__(self, **kwargs):
        super(MDDataTable, self).__init__(**kwargs)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

    def edit_press(self,*args):
        try:
            self.selected_id = args[0].parent.id
            self.isedit = not self.isedit

        except Exception as e:
            print("Exeption while edit hit Error: ",str(e))

    def delete_press(self,*args):
        try:
            self.selected_id = args[0].parent.id
            self.isdelete =False if self.isdelete else True
        except Exception as e:
            print("Exeption while delete hit Error: ",str(e))

    def info_press(self, *args):
        try:

            self.selected_id = args[0].parent.id
            self.isinfo =False if self.isinfo else True

        except Exception as e:
            print("Exeption while info hit Error: ",str(e))

    def copy_press(self, *args):

        try:

            self.selected_id = args[0].parent.id
            self.iscopy = False if self.iscopy else True

        except Exception as e:
            print("Exeption while copy hit Error: ", str(e))

    def populate(self, sort_by='', is_descending=False):
        """
        Populates the data into the DataTable with respect to provided sorting arguments
        :param sort_by: The column to be used for sorting, defaults to empty
        :param is_descending: The flag to indicate the direction of the sort (asc or dsc)
        """
        # Remove all widgets from parent
        self.clear_widgets()
        # Reset minimum height for row items
        self.minimum_height = self._min_list_height
        # Set number of rows
        self.rows = len(self.data)
        # Set number of columns
        self.cols = (len(self.data[0].keys()) if self.rows > 0 else 0) + 1
        # Counter for added rows
        if len(self.action)>0:
            self.cols = self.cols+1
        n = 0

        self.headerGrid=GridLayout(cols=self.cols,size_hint_y=None,height=dp(50))
        self.scroll =ScrollView(size_hint=(1, 1),do_scroll_y=True )
        self.bodyGrid = GridLayout(cols= self.cols,size_hint_x=0.99,size_hint_y=None,height=dp(50)*(len(self.data)-1))
        self.scroll.add_widget(self.bodyGrid)
        self.add_widget(self.headerGrid)
        self.add_widget(self.scroll)

        # Add header data
        if self.rows > 0:
            # Add a checkbox along with header row data
            checkbox = ItemCheckbox(id='select_all')
            checkbox.active = True if self.is_all_checked else False
            checkbox.bind(active=self.mutate_all)
            self.headerGrid.add_widget(checkbox)
            # self.add_widget(checkbox)
            # Add a header cell for each item in the first row
            for headerCell in self.data[0].values():
                label = HeaderLabel()
                # Set text
                label.text = headerCell
                # Set sorting indicator icon
                label.badge_text = u"{}".format(md_icons['unfold-more'])
                # Define text styling
                label.font_style = 'Body1'
                # label.halign = 'left'
                label.theme_text_color = 'Secondary'
                label.size_hint_y = None

                # If current cell is used for sorting, then apply the appropriate indicator icon
                if sort_by and label.text.__eq__(sort_by):
                    if is_descending:
                        label.badge_text = u"{}".format(md_icons['chevron-up'])
                    else:
                        label.badge_text = u"{}".format(md_icons['chevron-down'])
                self.headerGrid.add_widget(label)
                # self.add_widget(label)
                n += 1
            if len(self.action)>0:
                action_head_size = dp(45)*len(self.action) if len(self.action)>2 else dp(40)*2
                self.headerGrid.add_widget(BaseCellLabel(text="Action",theme_text_color='Secondary',size_hint_x=None,size=(action_head_size,0)))
            # self.add_widget(self.headerGrid)
        # Add row data


        for i, rowData in enumerate(self.data):
            # Skip the header row
            if i == 0:
                continue
            self.add_row(rowData)
        global counter
        counter = 0
        # Reset the selection attribute on each repopulate
        if self.is_all_checked:
            self.select_all(self.is_all_checked)



    def add_widget(self, widget, index=0, **kwargs):
        '''Adds a new widget to the parent and increases height'''
        super(MDDataTable, self).add_widget(widget, index)
        self.height += widget.height

    def remove_widget(self, widget):
        '''Removes a widget from the parent and decreases height'''
        super(MDDataTable, self).remove_widget(widget)
        self.height -= widget.height

    def add_row(self, row_data):
        '''Adds a new row to the parent'''
        global counter
        self.rows += 1
        n = 0

        # Add a checkbox along with row data
        checkbox = ItemCheckbox(size_hint_y=None,height=dp(50))
        # Generate hash using the row data and use it as Id for the row in the Data Table
        checkbox.id = self.generate_id(row_data)
        # if checkbox.id == self.selected_id:
        #     checkbox.active = True
        checkbox.bind(active=self.select_row)
        self.bodyGrid.add_widget(checkbox)
        # Add a row cell for each item in the first row
        for i, item in enumerate(row_data.values()):
            cell = RowLabel(font_style='Body1',
                            fullfilled = self.fullfilled,
                            theme_text_color='Primary',
                            text=str(item),
                            size_hint_y=None, halign='left',
                            height=dp(50),
                            id=("row_" + str(counter) + "_col_" + str(n)))
            cell_width = Window.size[0] * cell.size_hint_x
            cell.text_size = (cell_width - 30, None)
            cell.texture_update()
            # Change background color if this cell belongs to the column that is used for sorting
            if self.sorted_column > -1 and self.sorted_column == n:
                cell.bgcolor = cell.theme_cls.divider_color
            # self.add_widget(cell)
            self.bodyGrid.add_widget(cell)
            n += 1
        try:
            if len(self.action):
                from kivymd.button import MDIconButton
                action_col_size = dp(40) * len(self.action) if len(self.action) > 2 else dp(40) * 2
                action_button = ActionColumn(disabled=False,size_hint_x=None,size=(action_col_size,0),size_hint_y=None,height=dp(50))
                action_button.id = self.generate_id(row_data)
                for j,item in enumerate(self.action):
                    if item == 'edit':
                        edit_button = MDIconButton(id =str(i)+str(j),icon='pencil-box-outline',theme_text_color="Custom",text_color=self.theme_cls.primary_color)
                        edit_button.bind(on_press=self.edit_press)
                        action_button.add_widget(edit_button)
                    elif item == 'delete':
                        delete_button = MDIconButton(id =str(i)+str(j),icon='close-box-outline',theme_text_color="Error")
                        delete_button.bind(on_press=self.delete_press)
                        action_button.add_widget(delete_button)
                    elif item == 'copy' :
                        copy_button = MDIconButton(id =str(i)+str(j),icon='content-copy',theme_text_color="Primary")
                        copy_button.bind(on_press=self.copy_press)
                        action_button.add_widget(copy_button)
                    else:
                        info_button = MDIconButton(id =str(i)+str(j),icon='information',theme_text_color="Custom",text_color=self.theme_cls.primary_color)
                        info_button.bind(on_press=self.info_press)
                        action_button.add_widget(info_button)
                # self.add_widget(action_button)
                self.bodyGrid.add_widget(action_button)
        except Exception as e:
            print("exception while action column ",str(e))
        counter += 1

    def remove_row(self, row_data):
        '''Removes a row from the parent'''
        for item in row_data.values():
            for cell in self.parent.children:
                if cell.text.__eq__(item):
                    self.remove_widget(cell)
        self.rows -= 1

    def mutate_all(self, checkbox, checked, **kwargs):
        '''Selects or Unselects all rows in the parent'''
        self.is_all_checked = checked
        self.select_all(checked)

    def select_row(self, checkbox, checked, **kwargs):
        '''Selects the row associated with the provided CheckBox in the parent'''
        try:
            if not self.is_all_checked:
                checkbox.active = checked
                if checked:
                    self.selected_rows.append(self.find_row_by_id(checkbox.id))
                else:
                    self.selected_rows.remove(self.find_row_by_id(checkbox.id))


            # elif self.is_all_checked and checkbox.id =='select_all':
            #     checkbox.active=checked
            #     if checked:
            #         self.selected_rows= self.paginated_data[1:]
            #     else:
            #         self.selected_rows = []
            else:
                if checked:
                    self.selected_rows.append(self.find_row_by_id(checkbox.id))
                else:
                    self.selected_rows.remove(self.find_row_by_id(checkbox.id))
        except Exception as e:
            print("exception while select row Error: ",str(e))

    @staticmethod
    def generate_id(row_data):
        '''
        Generates a hash id using the provided row data.
        :param row_data: The data to be hashed
        :return: The hash value for the row that is to be used as Id for it
        '''
        return "row_" + str(hashlib.sha1(json.dumps(row_data, sort_keys=True).encode('utf-8')).hexdigest())

    def find_row_by_id(self, hash_id):
        '''
        Provides the row in the data table that matches the provided id
        :param hash_id: The id of the row to be fetched
        :return: The row matching the id
        '''
        row = ObjectProperty()
        for current_row in self.data:
            if self.generate_id(current_row).__eq__(hash_id):
                row = current_row
        return row

    def select_all(self, checked):
        '''
        Select all functionality for DataTable
        :param checked: flag for selection/un-selection
        '''
        for cell in self.bodyGrid.children:
            if isinstance(cell, ItemCheckbox):
                cell.active = checked

    def set_sort_callback(self, callback):
        '''
        Callback for sorting action
        :param callback: The callback method that is used for delegation of sorting action
        '''
        self.sort_callback = callback

    def on_sort(self, item, is_descending=False):
        '''Internal method used to delegate the sorting action to the callback'''
        self.sort_callback(item, is_descending)

    def set_display_range(self, start, end):
        '''Pagination functionality for the DataTable. Displays the data items within the given range.'''
        header_row = self.data[0]
        content_rows = [self.data[i] for i in range(1, len(self.data))]

        self.paginated_data = [header_row]
        self.paginated_data.extend(content_rows[start:end])
        self.data = self.data
        self.data = self.paginated_data
