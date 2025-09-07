from matplotlib import _api, backend_tools, cbook, widgets





class ToolEvent:

    

    def __init__(self, name, sender, tool, data=None):

        self.name = name

        self.sender = sender

        self.tool = tool

        self.data = data





class ToolTriggerEvent(ToolEvent):

    

    def __init__(self, name, sender, tool, canvasevent=None, data=None):

        super().__init__(name, sender, tool, data)

        self.canvasevent = canvasevent





class ToolManagerMessageEvent:

    

    def __init__(self, name, sender, message):

        self.name = name

        self.sender = sender

        self.message = message





class ToolManager:

    



    def __init__(self, figure=None):



        self._key_press_handler_id = None



        self._tools = {}

        self._keys = {}

        self._toggled = {}

        self._callbacks = cbook.CallbackRegistry()



                                   

        self.keypresslock = widgets.LockDraw()

        self.messagelock = widgets.LockDraw()



        self._figure = None

        self.set_figure(figure)



    @property

    def canvas(self):

        

        if not self._figure:

            return None

        return self._figure.canvas



    @property

    def figure(self):

        

        return self._figure



    @figure.setter

    def figure(self, figure):

        self.set_figure(figure)



    def set_figure(self, figure, update_tools=True):

        

        if self._key_press_handler_id:

            self.canvas.mpl_disconnect(self._key_press_handler_id)

        self._figure = figure

        if figure:

            self._key_press_handler_id = self.canvas.mpl_connect(

                'key_press_event', self._key_press)

        if update_tools:

            for tool in self._tools.values():

                tool.figure = figure



    def toolmanager_connect(self, s, func):

        

        return self._callbacks.connect(s, func)



    def toolmanager_disconnect(self, cid):

        

        return self._callbacks.disconnect(cid)



    def message_event(self, message, sender=None):

        

        if sender is None:

            sender = self



        s = 'tool_message_event'

        event = ToolManagerMessageEvent(s, sender, message)

        self._callbacks.process(s, event)



    @property

    def active_toggle(self):

        

        return self._toggled



    def get_tool_keymap(self, name):

        



        keys = [k for k, i in self._keys.items() if i == name]

        return keys



    def _remove_keys(self, name):

        for k in self.get_tool_keymap(name):

            del self._keys[k]



    def update_keymap(self, name, key):

        

        if name not in self._tools:

            raise KeyError(f'{name!r} not in Tools')

        self._remove_keys(name)

        if isinstance(key, str):

            key = [key]

        for k in key:

            if k in self._keys:

                _api.warn_external(

                    f'Key {k} changed from {self._keys[k]} to {name}')

            self._keys[k] = name



    def remove_tool(self, name):

        

        tool = self.get_tool(name)

        if getattr(tool, 'toggled', False):                                           

            self.trigger_tool(tool, 'toolmanager')

        self._remove_keys(name)

        event = ToolEvent('tool_removed_event', self, tool)

        self._callbacks.process(event.name, event)

        del self._tools[name]



    def add_tool(self, name, tool, *args, **kwargs):

        



        tool_cls = backend_tools._find_tool_class(type(self.canvas), tool)

        if not tool_cls:

            raise ValueError('Impossible to find class for %s' % str(tool))



        if name in self._tools:

            _api.warn_external('A "Tool class" with the same name already '

                               'exists, not added')

            return self._tools[name]



        tool_obj = tool_cls(self, name, *args, **kwargs)

        self._tools[name] = tool_obj



        if tool_obj.default_keymap is not None:

            self.update_keymap(name, tool_obj.default_keymap)



                                                                

        if isinstance(tool_obj, backend_tools.ToolToggleBase):

                                                                               

                                                

            if tool_obj.radio_group is None:

                self._toggled.setdefault(None, set())

            else:

                self._toggled.setdefault(tool_obj.radio_group, None)



                                  

            if tool_obj.toggled:

                self._handle_toggle(tool_obj, None, None)

        tool_obj.set_figure(self.figure)



        event = ToolEvent('tool_added_event', self, tool_obj)

        self._callbacks.process(event.name, event)



        return tool_obj



    def _handle_toggle(self, tool, canvasevent, data):

        



        radio_group = tool.radio_group

                                                    

                                                        

        if radio_group is None:

            if tool.name in self._toggled[None]:

                self._toggled[None].remove(tool.name)

            else:

                self._toggled[None].add(tool.name)

            return



                                                              

        if self._toggled[radio_group] == tool.name:

            toggled = None

                                                   

                   

        elif self._toggled[radio_group] is None:

            toggled = tool.name

                                                  

        else:

                                              

            self.trigger_tool(self._toggled[radio_group],

                              self,

                              canvasevent,

                              data)

            toggled = tool.name



                                                           

        self._toggled[radio_group] = toggled



    def trigger_tool(self, name, sender=None, canvasevent=None, data=None):

        

        tool = self.get_tool(name)

        if tool is None:

            return



        if sender is None:

            sender = self



        if isinstance(tool, backend_tools.ToolToggleBase):

            self._handle_toggle(tool, canvasevent, data)



        tool.trigger(sender, canvasevent, data)                          



        s = 'tool_trigger_%s' % name

        event = ToolTriggerEvent(s, sender, tool, canvasevent, data)

        self._callbacks.process(s, event)



    def _key_press(self, event):

        if event.key is None or self.keypresslock.locked():

            return



        name = self._keys.get(event.key, None)

        if name is None:

            return

        self.trigger_tool(name, canvasevent=event)



    @property

    def tools(self):

        

        return self._tools



    def get_tool(self, name, warn=True):

        

        if (isinstance(name, backend_tools.ToolBase)

                and name.name in self._tools):

            return name

        if name not in self._tools:

            if warn:

                _api.warn_external(

                    f"ToolManager does not control tool {name!r}")

            return None

        return self._tools[name]

