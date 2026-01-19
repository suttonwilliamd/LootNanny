import os
import json
import webbrowser
import urllib.parse
import requests
from threading import Thread
import time

from PyQt5.QtWidgets import QFileDialog, QTextEdit, QHBoxLayout, QFormLayout, QHeaderView, QTabWidget, QCheckBox, QGridLayout, QComboBox, QLineEdit, QLabel, QApplication, QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt
from modules.twitch import Commands, TwitchIntegration


CMD_NAMES = {
    Commands.INFO: "Information (info)",
    Commands.COMMANDS: "List Commands (commands)",
    Commands.TOP_LOOTS: "Top Loots (toploots)",
    Commands.ALL_RETURNS: "All Returns (allreturns)"
}





class TwitchTab(QWidget):

    def __init__(self, app: "LootNanny", config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app

        self.command_toggles = {}

        self.create_layout()

        # Bot
        self.twitch_bot = None
        self.twitch_bot_thread = None

        # Finalize Initialization
        self.validate_settings()

    def to_config(self):
        return {
            "token": self.oauth_token_text.text(),
            "username": self.username_text.text(),
            "channel": self.channel_text.text(),
            "prefix": self.command_prefix_text.text(),
            "commands_enabled": list(map(lambda c: c.value, self.commands_enabled))
        }

    def create_layout(self):
        layout = QVBoxLayout()

        form_inputs = QFormLayout()
        layout.addLayout(form_inputs)

        # Chat Location
        self.oauth_token_text = QLineEdit(self.app.config.twitch_token.ui_value)
        self.oauth_token_text.editingFinished.connect(self.on_settings_changed)
        form_inputs.addRow("OAuth Token:", self.oauth_token_text)

        btn = QPushButton("Get New OAuth Token:")
        btn.released.connect(self.get_oauth_token)
        form_inputs.addWidget(btn)

        self.username_text = QLineEdit(self.app.config.twitch_username.ui_value, enabled=True)
        self.username_text.editingFinished.connect(self.on_settings_changed)
        form_inputs.addRow("Bot Name:", self.username_text)

        self.channel_text = QLineEdit(self.app.config.twitch_channel.ui_value)
        self.channel_text.editingFinished.connect(self.on_settings_changed)
        form_inputs.addRow("Channel:", self.channel_text)

        self.command_prefix_text = QLineEdit(self.app.config.twitch_prefix.ui_value)
        self.command_prefix_text.editingFinished.connect(self.on_settings_changed)
        form_inputs.addRow("Command Prefix:", self.command_prefix_text)

        for i, cmd in enumerate(Commands):
            widget = QCheckBox(CMD_NAMES[cmd.value], self)
            widget.setChecked(cmd in self.app.config.twitch_commands_enabled.value)
            layout.addWidget(widget)
            widget.toggled.connect(self.on_commands_toggled)
            self.command_toggles[cmd] = widget

        layout.addStretch()

        self.start_btn = QPushButton("Start Twitch Bot:", enabled=False)
        self.start_btn.released.connect(self.start_twitch_bot)
        form_inputs.addWidget(self.start_btn)

        self.setLayout(layout)

    def get_oauth_token(self):
        """Get OAuth token - open generator and handle input"""
        try:
            webbrowser.open("https://twitchtokengenerator.com/")
            
            # Show input dialog for token
            token, ok = QInputDialog.getText(
                self, 
                'Enter OAuth Token',
                'Paste your OAuth Token:',
                text=""
            )
                
            if ok and token:
                # Handle various token formats from generator
                clean_token = token.strip()
                if not clean_token.startswith("oauth:"):
                    clean_token = f"oauth:{clean_token}"
                elif clean_token.startswith("v7"):  # Handle v7 format
                    clean_token = f"oauth:{clean_token}"
                elif clean_token.startswith("access_token="):  # Handle URL format
                    # Extract token from URL format
                    if "&" in clean_token:
                        clean_token = clean_token.split("&")[0].replace("access_token=", "")
                        clean_token = f"oauth:{clean_token}"
                    
                self.oauth_token_text.setText(clean_token)
                self.on_settings_changed()
                QMessageBox.information(self, "Success", "OAuth token set successfully!")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get OAuth token: {str(e)}")
    


    def start_twitch_bot(self):
        self.start_btn.setEnabled(False)
        self.start_btn.setText("Restart App To Start Twitch Bot Again :( (Work in progress)")
        if self.twitch_bot is not None:
            # Kill old twitch bot
            return  # TODO: This is harder than I first intneded to do cleanly, maybe need a daemon process :(
        
        try:
            print("Starting twitch bot")
            self.twitch_bot = TwitchIntegration(
                self.app,
                username=self.username_text.text(),
                token=self.oauth_token_text.text(),
                channel=self.channel_text.text(),
                command_prefix=self.command_prefix_text.text()
            )
            self.twitch_bot_thread = Thread(target=self.twitch_bot.start, daemon=True)
            self.twitch_bot_thread.start()
            QMessageBox.information(self, "Bot Started", f"Twitch bot '{self.username_text.text()}' is starting in channel '{self.channel_text.text()}'")
        except Exception as e:
            error_msg = f"Failed to start Twitch bot: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "Bot Start Error", error_msg)
            
            # Re-enable the button so user can try again
            self.start_btn.setEnabled(True)
            self.start_btn.setText("Start Twitch Bot:")

    def on_settings_changed(self):
        self.app.config.twitch_token = self.oauth_token_text.text()
        self.app.config.twitch_username = self.username_text.text()
        self.app.config.twitch_channel = self.channel_text.text()
        self.app.config.twitch_prefix = self.command_prefix_text.text()

        self.validate_settings()
        self.app.save_config()

    def validate_settings(self):
        missing_fields = []
        
        if not self.app.config.twitch_token.value:
            missing_fields.append("OAuth Token")
        if not self.app.config.twitch_username.value:
            missing_fields.append("Bot Name")
        if not self.app.config.twitch_channel.value:
            missing_fields.append("Channel")
        if not self.app.config.twitch_prefix.value:
            missing_fields.append("Command Prefix")
        
        if not missing_fields:
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)
            # Show helpful message
            if len(missing_fields) == 1:
                msg = f"Please fill in: {missing_fields[0]}"
            else:
                msg = f"Please fill in: {', '.join(missing_fields[:-1])} and {missing_fields[-1]}"
            
            # Only show message if it's not already showing (avoid spam)
            if not hasattr(self, '_last_validation_msg') or self._last_validation_msg != msg:
                self._last_validation_msg = msg
                QMessageBox.information(self, "Missing Information", msg)

    def on_commands_toggled(self):
        for command, checkbox in self.command_toggles.items():
            checkbox: QComboBox
            if checkbox.isChecked():
                self.app.config.twitch_commands_enabled.value.add(command)
            else:
                self.app.config.twitch_commands_enabled.value.discard(command)
        self.app.save_config()
