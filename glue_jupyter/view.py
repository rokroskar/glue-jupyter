from ipywidgets import HBox, Tab, VBox, Output

from IPython.display import display

from glue.viewers.common.viewer import Viewer
from glue.viewers.common.utils import get_viewer_tools
from glue.core.layer_artist import LayerArtistContainer
from glue.core import message as msg
from glue.core.subset import Subset


from glue_jupyter.utils import _update_not_none

from glue_jupyter.common.toolbar import BasicJupyterToolbar
from glue_jupyter.widgets.layer_options import LayerOptionsWidget

__all__ = ['IPyWidgetView', 'IPyWidgetLayerArtistContainer']


class IPyWidgetLayerArtistContainer(LayerArtistContainer):

    def __init__(self):
        super(IPyWidgetLayerArtistContainer, self).__init__()
        pass


class IPyWidgetView(Viewer):

    _layer_artist_container_cls = IPyWidgetLayerArtistContainer

    inherit_tools = True
    tools = []
    subtools = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialize_layer_options()
        self.initialize_toolbar()

    @property
    def toolbar_selection_tools(self):
        """
        The selection tools, e.g. rectangular or polygon selection.
        """
        return self.toolbar

    @property
    def toolbar_active_subset(self):
        """
        A dropdown providing control over the current active subset.
        """
        return self.session.application.widget_subset_select

    @property
    def toolbar_selection_mode(self):
        """
        Buttons providing control over logical selections.
        """
        return self.session.application.widget_subset_mode

    @property
    def figure_widget(self):
        """
        The main figure widget.
        """
        raise NotImplementedError()

    @property
    def output_widget(self):
        """
        A widget containing any textual output from the figures (including
        errors).
        """
        return self._output_widget

    @property
    def viewer_options(self):
        """
        A widget containing the options for the current viewer.
        """
        return self._layout_viewer_options

    @property
    def layer_options(self):
        """
        A widget containing a layer selector and the options for the selected
        layer.
        """
        return self._layout_layer_options

    @property
    def layout(self):
        """
        The widget containing the final layout of the individual figure widgets.
        """
        return self._layout

    def create_layout(self):

        # Take all the different widgets and construct a standard layout
        # for the viewers, based on ipywidgets HBox and VBox. This can be
        # overriden in sub-classes to create alternate layouts.

        self._layout_toolbar = HBox([self.toolbar_selection_tools,
                                     self.toolbar_active_subset,
                                     self.toolbar_selection_mode])

        self._layout_viewer_options = self._options_cls(self.state)

        self._layout_tab = Tab([self._layout_viewer_options,
                                self._layout_layer_options])
        self._layout_tab.set_title(0, "General")
        self._layout_tab.set_title(1, "Layers")

        self._output_widget = Output()

        self._layout = VBox([self._layout_toolbar,
                             HBox([self.figure_widget, self._layout_tab]),
                             self._output_widget])

    def show(self):
        display(self._layout)

    def add_data(self, data, color=None, alpha=None, **layer_state):

        result = super().add_data(data)

        if not result:
            return

        layer = list(self._layer_artist_container[data])[-1]

        layer_state = dict(layer_state)
        _update_not_none(layer_state, color=color, alpha=alpha)
        layer.state.update_from_dict(layer_state)

        return True

    def _update_subset(self, message):
        # TODO: move improvement here to glue-core
        if message.subset in self._layer_artist_container:
            for layer_artist in self._layer_artist_container[message.subset]:
                if isinstance(message, msg.SubsetUpdateMessage) and message.attribute not in ['subset_state']:
                    pass
                else:
                    layer_artist.update()
            self.redraw()

    def get_layer_artist(self, cls, layer=None, layer_state=None):
        return cls(self, self.state, layer=layer, layer_state=layer_state)

    def initialize_layer_options(self):
        self._layout_layer_options = LayerOptionsWidget(self)

    def initialize_toolbar(self):

        from glue.config import viewer_tool

        self.toolbar = BasicJupyterToolbar()

        # Need to include tools and subtools declared by parent classes unless
        # specified otherwise
        tool_ids, subtool_ids = get_viewer_tools(self.__class__)

        if subtool_ids:
            raise ValueError('subtools are not yet supported in Jupyter viewers')

        for tool_id in tool_ids:
            mode_cls = viewer_tool.members[tool_id]
            mode = mode_cls(self)
            self.toolbar.add_tool(mode)
