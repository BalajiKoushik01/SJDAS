"""
Tool Activation Methods Mixin
Provides all missing tool activation methods for PremiumDesignerView
"""
import logging

logger = logging.getLogger("SJ_DAS.ToolActivation")


class ToolActivationMixin:
    """
    Mixin class providing all tool activation methods.
    Add this to PremiumDesignerView to fix missing method errors.
    """

    def activate_pencil(self):
        """Activate 1-pixel pencil drawing tool"""
        try:
            if hasattr(self, 'editor'):
                self.editor.set_active_tool("pencil")
            if hasattr(self, 'update_status_bar'):
                self.update_status_bar("Tool: Pencil (1px)")
            logger.info("Activated pencil tool")
        except Exception as e:
            logger.error(f"Failed to activate pencil: {e}")

    def activate_fill_tool(self):
        """Activate fill bucket tool"""
        try:
            if hasattr(self, 'editor'):
                self.editor.set_active_tool("fill")
            if hasattr(self, 'update_status_bar'):
                self.update_status_bar("Tool: Fill Bucket")
            logger.info("Activated fill tool")
        except Exception as e:
            logger.error(f"Failed to activate fill tool: {e}")

    def activate_eyedropper(self):
        """Activate eyedropper color picker tool"""
        try:
            if hasattr(self, 'editor'):
                self.editor.set_active_tool("eyedropper")
            if hasattr(self, 'update_status_bar'):
                self.update_status_bar("Tool: Eyedropper")
            logger.info("Activated eyedropper tool")
        except Exception as e:
            logger.error(f"Failed to activate eyedropper: {e}")

    def activate_shape_tool(self, shape_type="rectangle"):
        """Activate shape drawing tool"""
        try:
            if hasattr(self, 'editor'):
                self.editor.set_active_tool("shape")
                if hasattr(self.editor, 'shape_type'):
                    self.editor.shape_type = shape_type
            if hasattr(self, 'update_status_bar'):
                self.update_status_bar(f"Tool: {shape_type.title()}")
            logger.info(f"Activated shape tool: {shape_type}")
        except Exception as e:
            logger.error(f"Failed to activate shape tool: {e}")

    def activate_line_tool(self):
        """Activate line drawing tool"""
        self.activate_shape_tool("line")

    def activate_rectangle_tool(self):
        """Activate rectangle drawing tool"""
        self.activate_shape_tool("rectangle")

    def activate_circle_tool(self):
        """Activate circle drawing tool"""
        self.activate_shape_tool("circle")

    def activate_polygon_tool(self):
        """Activate polygon drawing tool"""
        self.activate_shape_tool("polygon")
