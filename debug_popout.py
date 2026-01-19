#!/usr/bin/env python3

import sys
import os
import traceback
sys.path.append(os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer

# Debug the WeaponPopOut creation with minimal dependencies
def test_weapon_popout():
    try:
        # Import just the minimal classes needed
        from views.configuration import WeaponPopOut
        
        # Create a minimal parent
        class MinimalParent:
            def __init__(self):
                pass
                
        parent = MinimalParent()
        
        print("Creating WeaponPopOut...")
        weapon_popout = WeaponPopOut(parent)
        print("WeaponPopOut created successfully!")
        print("Window title:", weapon_popout.windowTitle())
        print("Window visible:", weapon_popout.isVisible())
        
        return True
        
    except Exception as e:
        print(f"Error creating WeaponPopOut: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    app = QApplication([])
    
    if test_weapon_popout():
        print("✓ WeaponPopOut works!")
        
        # Test multiple rapid creations to see if layout issue appears
        print("\nTesting rapid creation...")
        for i in range(3):
            print(f"Creating weapon popout {i+1}...")
            success = test_weapon_popout()
            if not success:
                print(f"✗ Failed at iteration {i+1}")
                break
        else:
            print(f"✓ Success at iteration {i+1}")
    else:
        print("✗ WeaponPopOut failed!")
        
    print("Test completed.")