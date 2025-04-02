"""
The inspiration for the settings manager is entirely from b2luigi and how it manages its settings.
"""


class SettingsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._settings = {}
        return cls._instance

    def set_setting(self, key, value):
        """Set a setting with the given key and value."""
        self._settings[key] = value

    def get_setting(self, key, default=None):
        """Retrieve a setting by key. Returns the default if the key is not found."""
        return self._settings.get(key, default)


# Instantiate settings manager
settings = SettingsManager()
