def _init_professional_features(self):
    """Initialize all professional features from Weeks 1-4."""
    try:
        # Week 1: Grid, Selection, Styles, Blends
        self.grid_manager = GridManager(self.editor)
        self.magic_wand = MagicWandTool()
        self.quick_selection = QuickSelectionTool()
        self.color_range = ColorRangeSelector()
        self.selection_refiner = SelectionRefiner()
        # Layer styles and blend modes initialized on-demand

        # Week 2: Liquify, Curves, Text Warp, Vectors
        from sj_das.filters.week2_features import (CurvesAdjustment,
                                                   LiquifyTool, TextWarpTool)
        from sj_das.tools.vector_tools import PenTool, ShapeTools

        self.liquify = LiquifyTool()
        self.curves = CurvesAdjustment()
        self.text_warp = TextWarpTool()
        self.pen_tool = PenTool()
        self.shapes = ShapeTools()

        # Week 3: Content-Aware, Batch, 3D
        from sj_das.automation.batch_processing import (ActionRecorder,
                                                        BatchProcessor)
        from sj_das.effects.effects_3d import Shapes3D, Text3D
        from sj_das.filters.content_aware import (ContentAwareFill,
                                                  ContentAwareMove,
                                                  ContentAwareScale)

        self.content_fill = ContentAwareFill()
        self.content_scale = ContentAwareScale()
        self.content_move = ContentAwareMove()
        self.action_recorder = ActionRecorder()
        self.batch_processor = BatchProcessor(self.action_recorder)
        self.text_3d = Text3D()
        self.shapes_3d = Shapes3D()

        # Week 4: Camera RAW, Perspective
        from sj_das.filters.camera_raw import CameraRAW, PerspectiveCorrection

        self.camera_raw = CameraRAW()
        self.perspective = PerspectiveCorrection()

        logger.info("[OK] Professional features initialized (60+ features)")

    except Exception as e:
        logger.error(f"Failed to initialize professional features: {e}")
