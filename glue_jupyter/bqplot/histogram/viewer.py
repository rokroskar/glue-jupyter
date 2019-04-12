from glue.core.subset import roi_to_subset_state
from glue.core.roi import RangeROI
from glue.viewers.histogram.state import HistogramViewerState

from ..common.viewer import BqplotBaseView

from .layer_artist import BqplotHistogramLayerArtist
from .layer_style_widget import HistogramLayerStateWidget
from .viewer_options_widget import HistogramViewerStateWidget


class BqplotHistogramView(BqplotBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    large_data_size = 1e5
    is2d = False

    _state_cls = HistogramViewerState
    _options_cls = HistogramViewerStateWidget
    _data_artist_cls = BqplotHistogramLayerArtist
    _subset_artist_cls = BqplotHistogramLayerArtist
    _layer_style_widget_cls = HistogramLayerStateWidget

    def _roi_to_subset_state(self, roi):
        # TODO: copy paste from glue/viewers/histogram/qt/data_viewer.py
        # TODO Does subset get applied to all data or just visible data?

        bins = self.state.bins

        x = roi.to_polygon()[0]
        lo, hi = min(x), max(x)

        if lo >= bins.min():
            lo = bins[bins <= lo].max()
        if hi <= bins.max():
            hi = bins[bins >= hi].min()

        roi_new = RangeROI(min=lo, max=hi, orientation='x')

        return roi_to_subset_state(roi_new, x_att=self.state.x_att)