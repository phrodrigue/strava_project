class SportNotAllowedException(Exception):
    def __init__(self, sport):
        self.message = f'Esporte nao permitido (\'{sport}\').'
        super().__init__(self.message)


class DeletedActivityException(Exception):
    def __init__(self, strava_id):
        self.message = f'Atividade [{strava_id}] nao encontrada no Strava.'
        super().__init__(self.message)


class APIResponseException(Exception):
    def __init__(self, message):
        self.message = f'Erro ao fazer chamada a API do Strava\n{message}'
        super().__init__(self.message)
