from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpacerItem, QSizePolicy)
from qfluentwidgets import (MessageBoxBase, SubtitleLabel, LineEdit, 
                            PasswordLineEdit, PrimaryPushButton, InfoBar, InfoBarPosition)

from sj_das.core.services.cloud_service import CloudService

class CloudLoginDialog(MessageBoxBase):
    """Dialog for authenticating with the SJDAS Cloud Backend."""
    
    login_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('SJDAS Cloud Login', self)
        
        # User input fields
        self.userLineEdit = LineEdit(self)
        self.userLineEdit.setPlaceholderText("Username or Email")
        self.userLineEdit.setText("admin")  # Default for testing
        
        self.passwordLineEdit = PasswordLineEdit(self)
        self.passwordLineEdit.setPlaceholderText("Password")
        self.passwordLineEdit.setText("admin")  # Default for testing
        
        # Add to layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(15)
        self.viewLayout.addWidget(QLabel("Connect to the secure cloud to enable AI Decoding & Exporting.", self))
        self.viewLayout.addSpacing(15)
        self.viewLayout.addWidget(self.userLineEdit)
        self.viewLayout.addWidget(self.passwordLineEdit)
        self.viewLayout.addSpacing(10)
        
        # Customize buttons
        self.yesButton.setText('Login')
        self.cancelButton.setText('Cancel')
        self.widget.setMinimumWidth(350)
        
        self.cloud_service = CloudService.instance()
        self.cloud_service.login_successful.connect(self._on_login_success)
        self.cloud_service.login_failed.connect(self._on_login_failed)
        
        # We override the yes button behavior to prevent it from closing immediately
        self.yesButton.disconnect()
        self.yesButton.clicked.connect(self._perform_login)
        
    def _perform_login(self):
        username = self.userLineEdit.text().strip()
        password = self.passwordLineEdit.text().strip()
        
        if not username or not password:
            InfoBar.error("Input Required", "Please enter both username and password.", 
                          duration=2000, parent=self)
            return
            
        self.yesButton.setText("Connecting...")
        self.yesButton.setDisabled(True)
        
        self.cloud_service.login(username, password)
        
    def _on_login_success(self, token):
        self.yesButton.setText("Success!")
        self.login_success.emit()
        self.accept()
        
    def _on_login_failed(self, error):
        self.yesButton.setDisabled(False)
        self.yesButton.setText("Login")
        InfoBar.error("Login Failed", str(error), duration=3000, parent=self)
