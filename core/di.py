class Container:
    def __init__(self):
        self._providers = {}

    def register(self, name, provider):
        self._providers[name] = provider

    def resolve(self, name):
        provider = self._providers.get(name)
        if provider is None:
            raise KeyError(f"Provider '{name}' not registered")
        return provider()

container = Container()
command_bus = None 
