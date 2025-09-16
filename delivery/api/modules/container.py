

class ModulesActionsDiContainer:
    @property
    def order_chain(self):
        from .order_chain.actions import OrderChainActions
        return OrderChainActions()