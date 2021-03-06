import ipyvuetify as v
import traitlets
from ipywidgets import Image

from glue.icons import icon_path
import glue.viewers.common.tool

__all__ = ['BasicJupyterToolbar']

ICON_WIDTH = 20


class BasicJupyterToolbar(v.BtnToggle):
    active_tool = traitlets.Instance(glue.viewers.common.tool.Tool)

    def __init__(self, viewer):
        self.output = viewer.output_widget
        self.tools = {}
        super().__init__(v_model=None, class_='transparent')

    @traitlets.observe('v_model')
    def _on_change_v_model(self, change):
        with self.output:
            if change.new is not None:
                self.active_tool = self.tools[change.new]

    @traitlets.observe('active_tool')
    def _on_change_active_tool(self, change):
        with self.output:
            if change.old:
                change.old.deactivate()
            if change.new:
                change.new.activate()

    def add_tool(self, tool):
        self.tools[tool.tool_id] = tool
        icon = Image.from_file(icon_path(tool.icon, icon_format='svg'), width=ICON_WIDTH)
        button = v.Btn(v_on="tooltip.on", icon=True, children=[icon], value=tool.tool_id)
        annotated = v.Tooltip(
            bottom=True,
            v_slots=[{
                'name': 'activator',
                'variable': 'tooltip',
                'children': button}],
            children=[tool.tool_tip])
        self.children = list(self.children) + [annotated]


# traitlets bug?
BasicJupyterToolbar.active_tool.default_value = None
