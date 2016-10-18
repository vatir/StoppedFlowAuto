
if __name__ == "__main__":
    from Control import ConfigOptions
    from Control import Methods
    
    ControlWindow = Methods.ControlWindow()
    ViewerWindow  = ControlWindow.StartViewer()
    
    ViewerWindow.SetAlwaysOnTop()
