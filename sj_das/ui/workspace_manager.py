"""
Workspace management system for SJ-DAS.

Provides predefined and custom workspace layouts similar to
Adobe Creative Suite, allowing users to optimize their workspace
for different tasks (Design, Export, Analysis).
"""

import json
import logging
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger("SJ_DAS.WorkspaceManager")


class WorkspaceManager(QObject):
    """
    Manages workspace layouts and panel arrangements.

    Features:
        - Predefined workspaces (Design, Export, Analysis)
        - Custom workspace saving/loading
        - Quick workspace switching
        - Layout persistence
    """

    workspace_changed = pyqtSignal(str)  # Emits workspace name

    # Predefined workspace configurations
    WORKSPACES = {
        'design': {
            'name': 'Design',
            'description': 'Optimized for design and editing',
            'panels': {
                'left': ['tools'],
                'right': ['layers', 'colors', 'yarn', 'weaves'],
                'bottom': None
            },
            'shortcuts': {
                'switch': 'F5'
            }
        },
        'export': {
            'name': 'Export',
            'description': 'Optimized for loom export',
            'panels': {
                'left': ['tools'],
                'right': ['loom_config', 'export_preview', 'colors'],
                'bottom': 'export_log'
            },
            'shortcuts': {
                'switch': 'F6'
            }
        },
        'analysis': {
            'name': 'Analysis',
            'description': 'Optimized for AI analysis',
            'panels': {
                'left': ['tools'],
                'right': ['ai_panel', 'histogram', 'layers'],
                'bottom': 'analysis_results'
            },
            'shortcuts': {
                'switch': 'F7'
            }
        },
        'minimal': {
            'name': 'Minimal',
            'description': 'Distraction-free editing',
            'panels': {
                'left': ['tools'],
                'right': [],
                'bottom': None
            },
            'shortcuts': {
                'switch': 'F8'
            }
        }
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_workspace = 'design'
        self.custom_workspaces: dict[str, dict] = {}
        self.config_path = Path.home() / '.sj_das' / 'workspaces.json'
        self.load_custom_workspaces()

    def switch_workspace(self, workspace_name: str) -> bool:
        """
        Switch to a different workspace.

        Args:
            workspace_name: Name of workspace to switch to

        Returns:
            True if workspace was found and switched
        """
        if workspace_name not in self.WORKSPACES and workspace_name not in self.custom_workspaces:
            logger.warning(f"Workspace '{workspace_name}' not found")
            return False

        self.current_workspace = workspace_name
        self.workspace_changed.emit(workspace_name)
        logger.info(f"Switched to workspace: {workspace_name}")
        return True

    def get_workspace_config(self, workspace_name: str | None = None) -> dict:
        """
        Get configuration for a workspace.

        Args:
            workspace_name: Name of workspace (uses current if None)

        Returns:
            Workspace configuration dictionary
        """
        name = workspace_name or self.current_workspace

        if name in self.WORKSPACES:
            return self.WORKSPACES[name]
        elif name in self.custom_workspaces:
            return self.custom_workspaces[name]
        else:
            return self.WORKSPACES['design']  # Fallback

    def save_custom_workspace(self, name: str, config: dict) -> bool:
        """
        Save current layout as a custom workspace.

        Args:
            name: Name for the custom workspace
            config: Workspace configuration

        Returns:
            True if saved successfully
        """
        self.custom_workspaces[name] = {
            'name': name,
            'description': config.get('description', 'Custom workspace'),
            'panels': config.get('panels', {}),
            'custom': True
        }

        self._persist_workspaces()
        logger.info(f"Saved custom workspace: {name}")
        return True

    def delete_custom_workspace(self, name: str) -> bool:
        """Delete a custom workspace."""
        if name in self.custom_workspaces:
            del self.custom_workspaces[name]
            self._persist_workspaces()
            logger.info(f"Deleted custom workspace: {name}")
            return True
        return False

    def get_all_workspaces(self) -> list[dict]:
        """Get list of all available workspaces."""
        workspaces = []

        # Add predefined workspaces
        for key, config in self.WORKSPACES.items():
            workspaces.append({
                'id': key,
                'name': config['name'],
                'description': config['description'],
                'custom': False
            })

        # Add custom workspaces
        for key, config in self.custom_workspaces.items():
            workspaces.append({
                'id': key,
                'name': config['name'],
                'description': config.get('description', ''),
                'custom': True
            })

        return workspaces

    def load_custom_workspaces(self):
        """Load custom workspaces from disk."""
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path) as f:
                self.custom_workspaces = json.load(f)
            logger.info(
                f"Loaded {len(self.custom_workspaces)} custom workspaces")
        except Exception as e:
            logger.error(f"Failed to load custom workspaces: {e}")

    def _persist_workspaces(self):
        """Save custom workspaces to disk."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.custom_workspaces, f, indent=2)
            logger.debug("Persisted custom workspaces")
        except Exception as e:
            logger.error(f"Failed to persist workspaces: {e}")

    def apply_workspace_to_view(self, view):
        """
        Apply current workspace layout to a view.

        Args:
            view: The main designer view to apply layout to
        """
        config = self.get_workspace_config()
        panels = config.get('panels', {})

        # Show/hide panels based on workspace
        panels.get('right', [])

        # This would need to be implemented in the view
        # to show/hide specific panels
        logger.info(f"Applied workspace '{self.current_workspace}' to view")

        # Example: view.show_panels(right_panels)
        # Example: view.show_bottom_panel(panels.get('bottom'))
