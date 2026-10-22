from logging import getLogger
from collections import namedtuple
from requests import Session, Request
from datetime import datetime, timezone, date, timedelta
from influxdb_client.client.exceptions import InfluxDBError

from varken.structures import TautulliStream
from varken.helpers import hashit, connection_handler

GeoData = namedtuple('GeoData', ['city', 'region', 'code', 'latitude', 'longitude'])
GEO_UNKNOWN = GeoData(city=None, region='', code='', latitude=None, longitude=None)


class TautulliAPI(object):
    def __init__(self, server, dbmanager):
        self.dbmanager = dbmanager
        self.server = server
        self.session = Session()
        self.session.params = {'apikey': self.server.api_key}
        self.endpoint = '/api/v2'
        self.logger = getLogger()
        self.my_ip = None
        self.geoip_cache = {}

    def __repr__(self):
        return f"<tautulli-{self.server.id}>"

    def geoip_lookup(self, ip_address):
        """Resolves one IP through Tautulli, which proxies plex.tv. Returns GeoData or None."""
        if not ip_address:
            return None

        if ip_address in self.geoip_cache:
            return self.geoip_cache[ip_address]

        params = {'cmd': 'get_geoip_lookup', 'ip_address': ip_address}
        req = self.session.prepare_request(Request('GET', self.server.url + self.endpoint, params=params))
        g = connection_handler(self.session, req, self.server.verify_ssl)

        data = g.get('response', {}).get('data') if g else None
        if not isinstance(data, dict) or data.get('latitude') is None:
            # Tautulli replaces data with {'error': ...} for an unroutable or malformed IP.
            self.logger.debug('Tautulli could not resolve geodata for IP ending in %s', ip_address.split('.')[-1])
            self.geoip_cache[ip_address] = None
            return None

        geodata = GeoData(city=data.get('city'), region=data.get('region') or '', code=data.get('code') or '',
                          latitude=data.get('latitude'), longitude=data.get('longitude'))
        self.geoip_cache[ip_address] = geodata

        return geodata

    def session_geodata(self, ip_address):
        """Resolves a stream IP, degrading to the configured fallback IP then Varken's own public IP."""
        geodata = self.geoip_lookup(ip_address)
        if geodata:
            return geodata

        self.logger.debug('Public IP missing for Tautulli session...')
        if not self.my_ip:
            self.logger.debug('Attempting to use the fallback IP...')
            geodata = self.geoip_lookup(self.server.fallback_ip)
            if geodata:
                return geodata

            self.my_ip = self.session.get('http://ip.42.pl/raw').text
            self.logger.debug('Looked the public IP and set it to %s', self.my_ip)

        return self.geoip_lookup(self.my_ip) or GEO_UNKNOWN

    def get_activity(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []
        params = {'cmd': 'get_activity'}

        req = self.session.prepare_request(Request('GET', self.server.url + self.endpoint, params=params))
        g = connection_handler(self.session, req, self.server.verify_ssl)

        if not g:
            return

        get = g['response']['data']
        try:
            sessions = [
                TautulliStream(**{k: session.get(k, v) for k, v in TautulliStream._field_defaults.items()})
                for session in get['sessions']
            ]
        except TypeError as e:
            self.logger.error('TypeError has occurred : %s while creating TautulliStream structure', e)
            return

        for session in sessions:
            # Check to see if ip_address_public attribute exists as it was introduced in v2
            try:
                getattr(session, 'ip_address_public')
            except AttributeError:
                self.logger.error('Public IP attribute missing!!! Do you have an old version of Tautulli (v1)?')
                exit(1)

            geodata = self.session_geodata(session.ip_address_public)

            if not all([geodata.latitude, geodata.longitude]):
                latitude = 37.234332396
                longitude = -115.80666344
            else:
                latitude = geodata.latitude
                longitude = geodata.longitude

            if not geodata.city:
                location = '👽'
            else:
                location = geodata.city

            decision = session.transcode_decision
            if decision == 'copy':
                decision = 'direct stream'

            video_decision = session.stream_video_decision
            if video_decision == 'copy':
                video_decision = 'direct stream'
            elif video_decision == '':
                video_decision = 'Music'

            quality = session.stream_video_resolution
            if not quality:
                quality = session.container.upper()
            elif quality in ('SD', 'sd', '4k'):
                quality = session.stream_video_resolution.upper()
            elif session.stream_video_full_resolution:
                quality = session.stream_video_full_resolution
            else:
                quality = session.stream_video_resolution + 'p'

            player_state = session.state.lower()
            if player_state == 'playing':
                player_state = 0
            elif player_state == 'paused':
                player_state = 1
            elif player_state == 'buffering':
                player_state = 3

            # Platform Version Overrides
            product_version = session.product_version
            if session.platform in ('Roku', 'osx', 'windows'):
                product_version = session.product_version.split('-')[0]

            # Platform Overrides
            platform_name = session.platform
            if platform_name in 'osx':
                platform_name = 'macOS'
            if platform_name in 'windows':
                platform_name = 'Windows'

            hash_id = hashit(f'{session.session_id}{session.session_key}{session.username}{session.full_title}')
            influx_payload.append(
                {
                    "measurement": "Tautulli",
                    "tags": {
                        "type": "Session",
                        "session_id": session.session_id,
                        "ip_address": session.ip_address,
                        "friendly_name": session.friendly_name,
                        "username": session.username,
                        "title": session.full_title,
                        "product": session.product,
                        "platform": platform_name,
                        "product_version": product_version,
                        "quality": quality,
                        "video_decision": video_decision.title(),
                        "transcode_decision": decision.title(),
                        "transcode_hw_decoding": session.transcode_hw_decoding,
                        "transcode_hw_encoding": session.transcode_hw_encoding,
                        "media_type": session.media_type.title(),
                        "audio_codec": session.audio_codec.upper(),
                        "audio_profile": session.audio_profile.upper(),
                        "stream_audio_codec": session.stream_audio_codec.upper(),
                        "quality_profile": session.quality_profile,
                        "progress_percent": session.progress_percent,
                        "region_code": geodata.code,
                        "location": location,
                        "full_location": f'{geodata.region} - {geodata.city}',
                        "latitude": latitude,
                        "longitude": longitude,
                        "player_state": player_state,
                        "device_type": platform_name,
                        "relayed": session.relayed,
                        "secure": session.secure,
                        "server": self.server.id
                    },
                    "time": now,
                    "fields": {
                        "hash": hash_id
                    }
                }
            )

        influx_payload.append(
            {
                "measurement": "Tautulli",
                "tags": {
                    "type": "current_stream_stats",
                    "server": self.server.id
                },
                "time": now,
                "fields": {
                    "stream_count": int(get['stream_count']),
                    "total_bandwidth": int(get['total_bandwidth']),
                    "wan_bandwidth": int(get['wan_bandwidth']),
                    "lan_bandwidth": int(get['lan_bandwidth']),
                    "transcode_streams": int(get['stream_count_transcode']),
                    "direct_play_streams": int(get['stream_count_direct_play']),
                    "direct_streams": int(get['stream_count_direct_stream'])
                }
            }
        )

        self.dbmanager.write_points(influx_payload)

    def get_stats(self):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        influx_payload = []
        params = {'cmd': 'get_libraries'}

        req = self.session.prepare_request(Request('GET', self.server.url + self.endpoint, params=params))
        g = connection_handler(self.session, req, self.server.verify_ssl)

        if not g:
            return

        get = g['response']['data']

        for library in get:
            data = {
                    "measurement": "Tautulli",
                    "tags": {
                        "type": "library_stats",
                        "server": self.server.id,
                        "section_name": library['section_name'],
                        "section_type": library['section_type']
                    },
                    "time": now,
                    "fields": {
                        "total": int(library['count'])
                    }
            }
            if library['section_type'] == 'show':
                data['fields']['seasons'] = int(library['parent_count'])
                data['fields']['episodes'] = int(library['child_count'])

            elif library['section_type'] == 'artist':
                data['fields']['artists'] = int(library['count'])
                data['fields']['albums'] = int(library['parent_count'])
                data['fields']['tracks'] = int(library['child_count'])
            influx_payload.append(data)

        self.dbmanager.write_points(influx_payload)

    def get_historical(self, days=30):
        influx_payload = []
        start_date = date.today() - timedelta(days=days)
        params = {'cmd': 'get_history', 'grouping': 1, 'length': 1000000}
        req = self.session.prepare_request(Request('GET', self.server.url + self.endpoint, params=params))
        g = connection_handler(self.session, req, self.server.verify_ssl)

        if not g:
            return

        get = g['response']['data']['data']

        params = {'cmd': 'get_stream_data', 'row_id': 0}
        sessions = []
        for history_item in get:
            if not history_item['id']:
                self.logger.debug('Skipping entry with no ID. (%s)', history_item['full_title'])
                continue
            if date.fromtimestamp(history_item['started']) < start_date:
                continue
            params['row_id'] = history_item['id']
            req = self.session.prepare_request(Request('GET', self.server.url + self.endpoint, params=params))
            g = connection_handler(self.session, req, self.server.verify_ssl)
            if not g:
                self.logger.debug('Could not get historical stream data for %s. Skipping.', history_item['full_title'])
            try:
                self.logger.debug('Adding %s to history', history_item['full_title'])
                history_item.update(g['response']['data'])
                sessions.append(TautulliStream(**history_item))
            except TypeError as e:
                self.logger.error('TypeError has occurred : %s while creating TautulliStream structure', e)
                continue

        for session in sessions:
            geodata = self.session_geodata(session.ip_address)

            if not all([geodata.latitude, geodata.longitude]):
                latitude = 37.234332396
                longitude = -115.80666344
            else:
                latitude = geodata.latitude
                longitude = geodata.longitude

            if not geodata.city:
                location = '👽'
            else:
                location = geodata.city

            decision = session.transcode_decision
            if decision == 'copy':
                decision = 'direct stream'

            video_decision = session.stream_video_decision
            if video_decision == 'copy':
                video_decision = 'direct stream'
            elif video_decision == '':
                video_decision = 'Music'

            quality = session.stream_video_resolution
            if not quality:
                quality = session.container.upper()
            elif quality in ('SD', 'sd', '4k'):
                quality = session.stream_video_resolution.upper()
            elif session.stream_video_full_resolution:
                quality = session.stream_video_full_resolution
            else:
                quality = session.stream_video_resolution + 'p'

            # Platform Overrides
            platform_name = session.platform
            if platform_name in 'osx':
                platform_name = 'Plex Mac OS'
            if platform_name in 'windows':
                platform_name = 'Plex Windows'

            player_state = 100

            hash_id = hashit(f'{session.id}{session.session_key}{session.user}{session.full_title}')
            influx_payload.append(
                {
                    "measurement": "Tautulli",
                    "tags": {
                        "type": "Session",
                        "session_id": session.session_id,
                        "ip_address": session.ip_address,
                        "friendly_name": session.friendly_name,
                        "username": session.user,
                        "title": session.full_title,
                        "product": session.product,
                        "platform": platform_name,
                        "quality": quality,
                        "video_decision": video_decision.title(),
                        "transcode_decision": decision.title(),
                        "transcode_hw_decoding": session.transcode_hw_decoding,
                        "transcode_hw_encoding": session.transcode_hw_encoding,
                        "media_type": session.media_type.title(),
                        "audio_codec": session.audio_codec.upper(),
                        "stream_audio_codec": session.stream_audio_codec.upper(),
                        "quality_profile": session.quality_profile,
                        "progress_percent": session.progress_percent,
                        "region_code": geodata.code,
                        "location": location,
                        "full_location": f'{geodata.region} - {geodata.city}',
                        "latitude": latitude,
                        "longitude": longitude,
                        "player_state": player_state,
                        "device_type": platform_name,
                        "relayed": session.relayed,
                        "secure": session.secure,
                        "server": self.server.id
                    },
                    "time": datetime.fromtimestamp(session.stopped).astimezone().isoformat(),
                    "fields": {
                        "hash": hash_id
                    }
                }
            )
            try:
                self.dbmanager.write_points(influx_payload)
            except InfluxDBError as e:
                if "beyond retention policy" in str(e):
                    self.logger.debug('Only imported 30 days of data per retention policy')
                else:
                    self.logger.error('Something went wrong... post this output in discord: %s', e)
