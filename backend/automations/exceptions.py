class AutomationValidationError(Exception):
    def __init__(self, errors: dict):
        self.errors = errors  # e.g. {'steps': {...}, 'trigger': {...}}
        super().__init__(str(errors))