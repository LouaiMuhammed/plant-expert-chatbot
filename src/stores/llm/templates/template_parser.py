import os
import importlib

class TemplateParser:

    def __init__(self, language: str=None, default_language='en'):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None
        self.set_language(language)

    def set_language(self, language: str):
        if not language:
            self.language = self.default_language
            return

        language_path = os.path.join(self.current_path, "locales", language)
        if language and os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language

    def get(self, group: str, key: str, vars: dict=None):
        if not group or not key:
            return None
        if vars is None:
            vars = {}
        
        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py")
        targeted_language = self.language
        
        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.default_language, f"{group}.py")
            targeted_language = self.default_language
        if not os.path.exists(group_path):
            return None
        
        # import group module

        module = importlib.import_module(
            f"stores.llm.templates.locales.{targeted_language}.{group}"
        )

        if not module:
            return None
        
        key_attribute = getattr(module, key)
        return key_attribute.substitute(vars)
    
