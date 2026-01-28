from logging import getLogger
from requests import Session, Request
from datetime import datetime, timezone, date, timedelta

from varken.structures import SonarrEpisode, SonarrTVShow, SonarrQueue, QueuePages
from varken.helpers import hashit, connection_handler


class SonarrAPI(object):
    def __init__(self, server, dbmanager):
        self.dbmanager = dbmanager
        self.server = server
        # Create session to reduce server web thread load, and globally define pageSize for all requests
        self.session = Session()
        self.session.headers = {'X-Api-Key': self.server.api_key}
        self.session.params = {'pageSize': 1000}
        self.logger = getLogger()

    def __repr__(self):
        return f"<sonarr-{self.server.id}>"

    def get_episode(self, id):
        endpoint = '/api/v3/episode'
        params = {'episodeIds': id}

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if get is False:
            return

        return SonarrEpisode(**get[0])

    def get_calendar(self, query="Missing"):
        endpoint = '/api/v3/calendar/'
        today = str(date.today())
        last_days = str(date.today() - timedelta(days=self.server.missing_days))
        future = str(date.today() + timedelta(days=self.server.future_days))
        now = datetime.now(timezone.utc).astimezone().isoformat()
        if query == "Missing":
            params = {'start': last_days, 'end': today, 'includeSeries': True}
        else:
            params = {'start': today, 'end': future, 'includeSeries': True}
        influx_payload = []
        air_days = []
        missing_episode_count = 0
        missing_show_ids = set()
        missing_seasons = set()

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
        get = connection_handler(self.session, req, self.server.verify_ssl)

        if not get:
            return

        tv_shows = []
        for show in get:
            try:
                tv_shows.append(SonarrEpisode(**show))
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while creating SonarrEpisode structure for show. Data '
                                  'attempted is: %s', e, show)

        for episode in tv_shows:
            tvShow = episode.series
            if episode.hasFile:
                downloaded = 1
            else:
                downloaded = 0
            if query == "Missing":
                if episode.monitored and not downloaded:
                    missing_episode_count += 1
                    series_id = getattr(episode, 'seriesId', tvShow.get('id'))
                    missing_show_ids.add(series_id)
                    missing_seasons.add((series_id, episode.seasonNumber))
            else:
                sxe = f'S{episode.seasonNumber:0>2}E{episode.episodeNumber:0>2}'
                air_days.append((tvShow['title'], downloaded, sxe, episode.title, episode.airDateUtc, episode.seriesId))

        selected = missing_episode_count if query == "Missing" else len(air_days)
        influx_payload.append(
            {
                "measurement": "Sonarr",
                "tags": {
                    "type": query,
                    "server": self.server.id
                },
                "time": now,
                "fields": {
                    "count": selected,
                    "show_count": len(missing_show_ids) if query == "Missing" else 0,
                    "season_count": len(missing_seasons) if query == "Missing" else 0,
                    "episode_count": selected if query == "Missing" else 0
                }
            }
        )

        if query != "Missing":
            for series_title, dl_status, sxe, episode_title, air_date_utc, sonarr_id in air_days:
                hash_id = hashit(f'{self.server.id}{series_title}{sxe}')
                influx_payload.append(
                    {
                        "measurement": "Sonarr",
                        "tags": {
                            "type": query,
                            "sonarrId": sonarr_id,
                            "server": self.server.id,
                            "name": series_title,
                            "epname": episode_title,
                            "sxe": sxe,
                            "airsUTC": air_date_utc,
                            "downloaded": dl_status
                        },
                        "time": now,
                        "fields": {
                            "hash": hash_id
                        }
                    }
                )

        if influx_payload:
            self.dbmanager.write_points(influx_payload)

    def get_queue(self):
        influx_payload = []
        endpoint = '/api/v3/queue'
        now = datetime.now(timezone.utc).astimezone().isoformat()
        pageSize = 250
        params = {'pageSize': pageSize, 'includeSeries': True, 'includeEpisode': True,
                  'includeUnknownSeriesItems': False}
        queueResponse = []
        queue = []

        req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
        get = connection_handler(self.session, req, self.server.verify_ssl)
        if get is False:
            return

        response = QueuePages(**get)
        queueResponse.extend(response.records)

        while response.totalRecords > response.page * response.pageSize:
            page = response.page + 1
            params = {'pageSize': pageSize, 'page': page, 'includeSeries': True, 'includeEpisode': True,
                      'includeUnknownSeriesItems': False}
            req = self.session.prepare_request(Request('GET', self.server.url + endpoint, params=params))
            get = connection_handler(self.session, req, self.server.verify_ssl)
            if get is False:
                return

            response = QueuePages(**get)
            queueResponse.extend(response.records)

        download_queue = []
        for queueItem in queueResponse:
            try:
                download_queue.append(SonarrQueue(**queueItem))
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while creating Queue structure. Data attempted is: '
                                  '%s', e, queueItem)
        influx_payload.append(
            {
                "measurement": "Sonarr",
                "tags": {
                    "type": "Queue",
                    "server": self.server.id
                },
                "time": now,
                "fields": {
                    "count": len(download_queue)
                }
            }
        )

        if not download_queue:
            self.dbmanager.write_points(influx_payload)
            return

        for queueItem in download_queue:
            tvShow = SonarrTVShow(**queueItem.series)
            try:
                episode = SonarrEpisode(**queueItem.episode)
                sxe = f"S{episode.seasonNumber:0>2}E{episode.episodeNumber:0>2}"
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while processing the sonarr queue. \
                                  Remove invalid queue entry. Data attempted is: %s', e, queueItem)
                continue

            if queueItem.protocol.upper() == 'USENET':
                protocol_id = 1
            else:
                protocol_id = 0

            queue.append((tvShow.title, episode.title, queueItem.protocol.upper(),
                          protocol_id, sxe, queueItem.seriesId, queueItem.quality['quality']['name']))

        for series_title, episode_title, protocol, protocol_id, sxe, sonarr_id, quality in queue:
            hash_id = hashit(f'{self.server.id}{series_title}{sxe}')
            influx_payload.append(
                {
                    "measurement": "Sonarr",
                    "tags": {
                        "type": "Queue",
                        "sonarrId": sonarr_id,
                        "server": self.server.id,
                        "name": series_title,
                        "epname": episode_title,
                        "sxe": sxe,
                        "protocol": protocol,
                        "protocol_id": protocol_id,
                        "quality": quality
                    },
                    "time": now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )

        if influx_payload:
            self.dbmanager.write_points(influx_payload)
