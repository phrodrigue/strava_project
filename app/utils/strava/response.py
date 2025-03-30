class StravaResponse:
    """Classe para padronizar as possiveis respostas ao chamar a API do Strava"""
    OK = True

    def __init__(
        self,
        token_not_present=False,
        token_expired=False,
        request_error=False,
        json=None
    ):
        self.TOKEN_NOT_PRESENT = token_not_present
        self.TOKEN_EXPIRED = token_expired
        self.REQUEST_ERROR = request_error
        self.JSON = {} if not json else json

        if token_not_present or token_expired or request_error:
            self.OK = False
