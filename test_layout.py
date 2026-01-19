#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication
from views.configuration import ConfigTab

# Create a minimal app
app = QApplication([])

# Create a minimal parent class
class MockConfig:
    def __init__(self):
        self.custom_weapons = []
        self.location = "C:/Users/sutto/Documents/Entropia Universe/chat.log"
        self.theme = "dark"

class TestParent:
    def __init__(self):
        self.config = MockConfig()
        self.theme = "dark"
    
    def add_weapon_cancled(self):
        print("Weapon add cancelled")
    
    def on_added_weapon(self, weapon, amp, scope, sight_1, sight_2, damage_enhancers, accuracy_enhancers, economy_enhancers):
        print(f"Weapon added: {weapon}")

# Create parent and try to open config tab
parent = TestParent()
config_tab = ConfigTab(parent)

# Try to add a new weapon
config_tab.add_new_weapon()

print("Test completed")