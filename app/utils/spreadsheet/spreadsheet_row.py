from datetime import datetime

from app.utils import create_activity_url
from app.utils.strava.response import StravaResponse


class SpreadsheetRow:
    def __init__(self, data: StravaResponse, activity_id: int) -> None:
        if not data.OK:
            self.new = [
                str(activity_id),
                'ERRO NA API',
                f'=HIPERLINK(\"{data.JSON["id"]}\";\"LOGIN\")',
                data.JSON['message'],
                '',
                '',
                '',
                '',
                '',
            ]

        else:
            activity_date = data.JSON['start_date_local']
            date_obj = datetime.strptime(activity_date, "%Y-%m-%dT%H:%M:%SZ")

            """Converte o tempo em segundos para o formato H:MM:SS"""
            seconds = data.JSON['moving_time']
            hours, rest = divmod(seconds, 3600)
            minutes, seconds = divmod(rest, 60)
            time_str = f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"

            self.new = [
                f'=HIPERLINK(\"{create_activity_url(data.JSON["id"], external=True)}\";\"{data.JSON["id"]}\")',
                data.JSON['name'],
                data.JSON['type'],
                date_obj.strftime("%d/%m/%Y"),
                data.JSON.get('average_heartrate') or 0,
                data.JSON.get('max_heartrate') or 0,
                data.JSON.get('total_elevation_gain') or 0,
                data.JSON['distance'],
                time_str,
            ]
