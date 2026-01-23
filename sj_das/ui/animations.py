"""
Elegant Animation System for SJ-DAS
Provides smooth, premium animations for UI elements
"""
from PyQt6.QtCore import (QEasingCurve, QPoint, QPropertyAnimation, QRect,
                          pyqtProperty)
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget


class AnimationHelper:
    """
    Helper class for creating smooth, elegant animations.
    Uses cubic-bezier easing for premium feel.
    """

    # Animation Durations (ms)
    DURATION_FAST = 200
    DURATION_NORMAL = 300
    DURATION_SLOW = 500

    # Easing Curves
    EASE_IN_OUT = QEasingCurve.Type.InOutCubic
    EASE_OUT = QEasingCurve.Type.OutCubic
    EASE_IN = QEasingCurve.Type.InCubic
    EASE_ELASTIC = QEasingCurve.Type.OutElastic

    @staticmethod
    def fade_in(widget: QWidget, duration: int = 300, on_finished=None):
        """
        Smooth fade-in animation.

        Args:
            widget: Widget to animate
            duration: Animation duration in ms
            on_finished: Callback when animation completes
        """
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(AnimationHelper.EASE_OUT)

        if on_finished:
            animation.finished.connect(on_finished)

        animation.start()
        return animation

    @staticmethod
    def fade_out(widget: QWidget, duration: int = 300, on_finished=None):
        """
        Smooth fade-out animation.

        Args:
            widget: Widget to animate
            duration: Animation duration in ms
            on_finished: Callback when animation completes
        """
        effect = widget.graphicsEffect()
        if not effect:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(AnimationHelper.EASE_IN)

        if on_finished:
            animation.finished.connect(on_finished)

        animation.start()
        return animation

    @staticmethod
    def slide_in_from_right(
            widget: QWidget, duration: int = 400, distance: int = 300):
        """
        Slide widget in from the right side.

        Args:
            widget: Widget to animate
            duration: Animation duration in ms
            distance: Distance to slide in pixels
        """
        original_pos = widget.pos()
        start_pos = QPoint(original_pos.x() + distance, original_pos.y())
        widget.move(start_pos)

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        animation.setEasingCurve(AnimationHelper.EASE_OUT)

        animation.start()
        return animation

    @staticmethod
    def slide_in_from_bottom(
            widget: QWidget, duration: int = 400, distance: int = 200):
        """
        Slide widget in from the bottom.

        Args:
            widget: Widget to animate
            duration: Animation duration in ms
            distance: Distance to slide in pixels
        """
        original_pos = widget.pos()
        start_pos = QPoint(original_pos.x(), original_pos.y() + distance)
        widget.move(start_pos)

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        animation.setEasingCurve(AnimationHelper.EASE_OUT)

        animation.start()
        return animation

    @staticmethod
    def scale_in(widget: QWidget, duration: int = 300):
        """
        Scale widget from 0 to full size with elastic effect.

        Args:
            widget: Widget to animate
            duration: Animation duration in ms
        """
        original_geometry = widget.geometry()
        center = original_geometry.center()

        # Start from center point
        start_rect = QRect(center.x(), center.y(), 0, 0)

        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_rect)
        animation.setEndValue(original_geometry)
        animation.setEasingCurve(AnimationHelper.EASE_ELASTIC)

        animation.start()
        return animation

    @staticmethod
    def pulse(widget: QWidget, duration: int = 1000,
              scale_factor: float = 1.05):
        """
        Create a subtle pulse animation (scale up and down).

        Args:
            widget: Widget to animate
            duration: Full cycle duration in ms
            scale_factor: How much to scale (1.05 = 5% larger)
        """
        original_size = widget.size()
        larger_size = original_size * scale_factor

        animation = QPropertyAnimation(widget, b"size")
        animation.setDuration(duration // 2)
        animation.setStartValue(original_size)
        animation.setEndValue(larger_size)
        animation.setEasingCurve(AnimationHelper.EASE_IN_OUT)

        # Create reverse animation
        animation.finished.connect(
            lambda: AnimationHelper._pulse_reverse(
                widget, original_size, duration // 2))

        animation.start()
        return animation

    @staticmethod
    def _pulse_reverse(widget: QWidget, original_size, duration: int):
        """Helper for pulse animation reverse."""
        animation = QPropertyAnimation(widget, b"size")
        animation.setDuration(duration)
        animation.setStartValue(widget.size())
        animation.setEndValue(original_size)
        animation.setEasingCurve(AnimationHelper.EASE_IN_OUT)
        animation.start()

    @staticmethod
    def glow_effect(widget: QWidget, color: QColor = QColor(
            0, 240, 255), duration: int = 500):
        """
        Create a glow effect by animating opacity.

        Args:
            widget: Widget to glow
            color: Glow color
            duration: Animation duration in ms
        """
        # This would typically use a custom painted overlay
        # For now, we'll use opacity pulsing
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.6)
        animation.setEasingCurve(AnimationHelper.EASE_IN_OUT)
        animation.setLoopCount(-1)  # Infinite loop

        animation.start()
        return animation


class AnimatedDialog:
    """
    Mixin class for dialogs with entrance animations.
    """

    def show_with_animation(self, animation_type='fade'):
        """
        Show dialog with animation.

        Args:
            animation_type: 'fade', 'slide_bottom', 'scale'
        """
        self.show()

        if animation_type == 'fade':
            AnimationHelper.fade_in(
                self, duration=AnimationHelper.DURATION_NORMAL)
        elif animation_type == 'slide_bottom':
            AnimationHelper.slide_in_from_bottom(
                self, duration=AnimationHelper.DURATION_NORMAL)
        elif animation_type == 'scale':
            AnimationHelper.scale_in(
                self, duration=AnimationHelper.DURATION_NORMAL)

    def close_with_animation(self, animation_type='fade'):
        """
        Close dialog with animation.

        Args:
            animation_type: 'fade' or other
        """
        if animation_type == 'fade':
            AnimationHelper.fade_out(
                self,
                duration=AnimationHelper.DURATION_FAST,
                on_finished=self.close)
        else:
            self.close()
