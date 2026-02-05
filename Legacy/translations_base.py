# Translations v2.0 - Optimized & Complete
#  ES (default),  EN,  FR,  DE,  PT
# Lazy loading for 0ms startup impact

class Translations:
    def __init__(self):
        self.current_language = "es"
        self._trans = None
    
    @property
    def translations(self):
        if not self._trans:
            self._trans = self._load()
        return self._trans
    
    def _load(self):
        return {"es": self._es(), "en": self._en(), "fr": self._fr(), "de": self._de(), "pt": self._pt()}
