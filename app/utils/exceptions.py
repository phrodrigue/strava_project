class SportNotAllowedException(Exception):
    def __init__(self, sport):
        self.message = f'Esporte nao permitido (\'{sport}\').'
        super().__init__(self.message)


class APIResponseException(Exception):
    def __init__(self, message):
        super().__init__(message)
