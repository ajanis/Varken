from sys import version_info
from logging import getLogger

logger = getLogger('temp')
# Check for python3.6 or newer to resolve erroneous typing.NamedTuple issues
if version_info < (3, 6, 2):
    logger.error('Varken requires python3.6.2 or newer. You are on python%s.%s.%s - Exiting...',
                 version_info.major, version_info.minor, version_info.micro)
    exit(1)


class DynamicNamedTuple:
    def __init__(self, **kwargs):
        # Predefined fields with optional defaults
        self._field_defaults = {}
        for key, value in self.__class__.__dict__.items():
            if not key.startswith('_') and not callable(value):
                self._field_defaults[key] = value

        # Assign provided values, default where applicable
        for key in self._field_defaults:
            setattr(self, key, kwargs.pop(key, self._field_defaults[key]))

        # Add any additional fields dynamically
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        fields = {key: getattr(self, key) for key in vars(self) if not key.startswith('_')}
        return f"{self.__class__.__name__}({fields})"


# Server Structures
class InfluxServer(DynamicNamedTuple):
    password: str = 'root'
    port: int = 8086
    ssl: bool = False
    url: str = 'localhost'
    username: str = 'root'
    verify_ssl: bool = False
    org: str = '-'


class Influx2Server(DynamicNamedTuple):
    url: str = 'localhost'
    org: str = 'server'
    token: str = 'TOKEN'
    bucket: str = 'varken'
    timeout: int = 10000
    ssl: bool = False
    verify_ssl: bool = False


class SonarrServer(DynamicNamedTuple):
    api_key: str = None
    future_days: int = 0
    future_days_run_seconds: int = 30
    id: int = None
    missing_days: int = 0
    missing_days_run_seconds: int = 30
    queue: bool = False
    queue_run_seconds: int = 30
    url: str = None
    verify_ssl: bool = False


class RadarrServer(DynamicNamedTuple):
    api_key: str = None
    get_missing: bool = False
    get_missing_run_seconds: int = 30
    id: int = None
    queue: bool = False
    queue_run_seconds: int = 30
    url: str = None
    verify_ssl: bool = False


class OmbiServer(DynamicNamedTuple):
    api_key: str = None
    id: int = None
    issue_status_counts: bool = False
    issue_status_run_seconds: int = 30
    request_total_counts: bool = False
    request_total_run_seconds: int = 30
    request_type_counts: bool = False
    request_type_run_seconds: int = 30
    url: str = None
    verify_ssl: bool = False


class OverseerrServer(DynamicNamedTuple):
    api_key: str = None
    id: int = None
    url: str = None
    verify_ssl: bool = False
    get_request_total_counts: bool = False
    request_total_run_seconds: int = 30
    num_latest_requests_to_fetch: int = 10
    num_latest_requests_seconds: int = 30


class TautulliServer(DynamicNamedTuple):
    api_key: str = None
    fallback_ip: str = None
    get_activity: bool = False
    get_activity_run_seconds: int = 30
    get_stats: bool = False
    get_stats_run_seconds: int = 30
    id: int = None
    url: str = None
    verify_ssl: bool = None
    maxmind_license_key: str = None


class SickChillServer(DynamicNamedTuple):
    api_key: str = None
    get_missing: bool = False
    get_missing_run_seconds: int = 30
    id: int = None
    url: str = None
    verify_ssl: bool = False


class UniFiServer(DynamicNamedTuple):
    get_usg_stats_run_seconds: int = 30
    id: int = None
    password: str = 'ubnt'
    site: str = None
    url: str = 'unifi.domain.tld:8443'
    username: str = 'ubnt'
    usg_name: str = None
    verify_ssl: bool = False


# Shared
class QueuePages(DynamicNamedTuple):
    page: int = None
    pageSize: int = None
    sortKey: str = None
    sortDirection: str = None
    totalRecords: str = None
    records: list = None


# Ombi Structures
class OmbiRequestCounts(DynamicNamedTuple):
    approved: int = 0
    available: int = 0
    pending: int = 0


class OmbiIssuesCounts(DynamicNamedTuple):
    inProgress: int = 0
    pending: int = 0
    resolved: int = 0


class OmbiTVRequest(DynamicNamedTuple):
    background: str = None
    childRequests: list = None
    denied: bool = None
    deniedReason: None = None
    externalProviderId: str = None
    id: int = None
    imdbId: str = None
    languageProfile: str = None
    markedAsDenied: str = None
    overview: str = None
    posterPath: str = None
    qualityOverride: None = None
    releaseDate: str = None
    rootFolder: None = None
    status: str = None
    title: str = None
    totalSeasons: int = None
    tvDbId: int = None
    requestedByAlias: str = None
    requestStatus: str = None


class OmbiMovieRequest(DynamicNamedTuple):
    approved: bool = None
    approved4K: bool = None
    available: bool = None
    available4K: bool = None
    background: str = None
    canApprove: bool = None
    denied: bool = None
    denied4K: None = None
    deniedReason: None = None
    deniedReason4K: None = None
    digitalRelease: bool = None
    digitalReleaseDate: None = None
    has4KRequest: bool = None
    id: int = None
    imdbId: str = None
    is4kRequest: bool = None
    issueId: None = None
    issues: None = None
    langCode: str = None
    languageCode: str = None
    markedAsApproved: str = None
    markedAsApproved4K: str = None
    markedAsAvailable: None = None
    markedAsAvailable4K: None = None
    markedAsDenied: str = None
    markedAsDenied4K: str = None
    overview: str = None
    playedByUsersCount: int = None
    posterPath: str = None
    qualityOverride: int = None
    released: bool = None
    releaseDate: str = None
    requestedByAlias: str = None
    requestedDate: str = None
    requestedDate4k: str = None
    requestedUser: dict = None
    requestedUserId: str = None
    requestStatus: str = None
    requestType: int = None
    rootPathOverride: int = None
    showSubscribe: bool = None
    source: int = None
    status: str = None
    subscribed: bool = None
    theMovieDbId: int = None
    title: str = None
    watchedByRequestedUser: str = None


# Overseerr
class OverseerrRequestCounts(DynamicNamedTuple):
    pending: int = None
    approved: int = None
    processing: int = None
    available: int = None
    total: int = None
    movie: int = None
    tv: int = None
    declined: int = None


# Sonarr
class SonarrTVShow(DynamicNamedTuple):
    added: str = None
    airTime: str = None
    alternateTitles: list = None
    certification: str = None
    cleanTitle: str = None
    ended: bool = None
    firstAired: str = None
    genres: list = None
    id: int = None
    images: list = None
    imdbId: str = None
    languageProfileId: int = None
    monitored: bool = None
    nextAiring: str = None
    network: str = None
    overview: str = None
    path: str = None
    previousAiring: str = None
    qualityProfileId: int = None
    ratings: dict = None
    rootFolderPath: str = None
    runtime: int = None
    seasonFolder: bool = None
    seasons: list = None
    seriesType: str = None
    sortTitle: str = None
    statistics: dict = None
    status: str = None
    tags: list = None
    title: str = None
    titleSlug: str = None
    tvdbId: int = None
    tvMazeId: int = None
    tvRageId: int = None
    useSceneNumbering: bool = None
    year: int = None
    originalLanguage: str = None


class SonarrEpisode(DynamicNamedTuple):
    absoluteEpisodeNumber: int = None
    airDate: str = None
    airDateUtc: str = None
    episodeFileId: int = None
    episodeNumber: int = None
    grabbed: bool = None
    hasFile: bool = None
    id: int = None
    monitored: bool = None
    runtime: int = None
    overview: str = None
    seasonNumber: int = None
    seriesId: int = None
    title: str = None
    unverifiedSceneNumbering: bool = None
    sceneAbsoluteEpisodeNumber: int = None
    sceneEpisodeNumber: int = None
    sceneSeasonNumber: int = None
    series: SonarrTVShow = None
    tvdbId: int = None
    finaleType: str = None
    episodeFile: dict = None
    endTime: str = None
    grabTime: str = None
    seriesTitle: str = None
    images: list = None
    lastSearchTime: str = None


class SonarrQueue(DynamicNamedTuple):
    downloadClient: str = None
    downloadId: str = None
    episodeId: int = None
    id: int = None
    indexer: str = None
    language: dict = None
    languages: list[dict] = []
    protocol: str = None
    quality: dict = None
    size: float = None
    sizeleft: float = None
    status: str = None
    statusMessages: list = None
    title: str = None
    trackedDownloadState: str = None
    trackedDownloadStatus: str = None
    seriesId: int = None
    errorMessage: str = None
    outputPath: str = None
    series: SonarrTVShow = None
    episode: SonarrEpisode = None
    timeleft: str = None
    estimatedCompletionTime: str = None
    seasonNumber: int = None
    customFormats: list[dict] = []
    customFormatScore: int = None
    added: str = None
    downloadClientHasPostImportCategory: bool = None
    episodeHasFile: bool = None


# Radarr
class RadarrMovie(DynamicNamedTuple):
    added: str = None
    alternateTitles: list = None
    certification: str = None
    cleanTitle: str = None
    collection: dict = None
    digitalRelease: str = None
    folderName: str = None
    genres: list = None
    hasFile: bool = None
    id: int = None
    images: list = None
    imdbId: str = None
    inCinemas: str = None
    isAvailable: bool = None
    minimumAvailability: str = None
    monitored: bool = None
    movieFile: dict = None
    originalTitle: str = None
    overview: str = None
    path: str = None
    physicalRelease: str = None
    qualityProfileId: int = None
    ratings: dict = None
    runtime: int = None
    secondaryYear: int = None
    secondaryYearSourceId: int = None
    sizeOnDisk: float = None
    sortTitle: str = None
    status: str = None
    studio: str = None
    tags: list = None
    titleSlug: str = None
    tmdbId: int = None
    website: str = None
    year: int = None
    youTubeTrailerId: str = None
    title: str = None
    originalLanguage: str = None
    addOptions: str = None
    popularity: str = None
    rootFolderPath: str = None


# Radarr Queue
class RadarrQueue(DynamicNamedTuple):
    customFormats: list = None
    downloadClient: str = None
    downloadId: str = None
    id: int = None
    indexer: str = None
    languages: list = None
    movieId: int = None
    protocol: str = None
    quality: dict = None
    size: float = None
    sizeleft: float = None
    status: str = None
    statusMessages: list = None
    title: str = None
    trackedDownloadState: str = None
    trackedDownloadStatus: str = None
    timeleft: str = None
    estimatedCompletionTime: str = None
    errorMessage: str = None
    outputPath: str = None
    movie: RadarrMovie = None
    timeleft: str = None
    customFormatScore: int = None
    indexerFlags: int = None
    added: str = None
    downloadClientHasPostImportCategory: bool = None


# Sickchill
class SickChillTVShow(DynamicNamedTuple):
    airdate: str = None
    airs: str = None
    episode: int = None
    ep_name: str = None
    ep_plot: str = None
    indexerid: int = None
    network: str = None
    paused: int = None
    quality: str = None
    season: int = None
    show_name: str = None
    show_status: str = None
    tvdbid: int = None
    weekday: int = None


# Tautulli
class TautulliStream(DynamicNamedTuple):
    _field_defaults: dict = {
        "actors": None,
        "added_at": None,
        "allow_guest": None,
        "art": None,
        "aspect_ratio": None,
        "audience_rating": None,
        "audience_rating_image": None,
        "audio_bitrate": None,
        "audio_bitrate_mode": None,
        "audio_channel_layout": None,
        "audio_channels": None,
        "audio_codec": None,
        "audio_decision": None,
        "audio_language": None,
        "audio_language_code": None,
        "audio_profile": None,
        "audio_sample_rate": None,
        "bandwidth": None,
        "banner": None,
        "bif_thumb": None,
        "bitrate": None,
        "channel_icon": None,
        "channel_stream": None,
        "channel_title": None,
        "children_count": None,
        "collections": None,
        "container": None,
        "content_rating": None,
        "current_session": None,
        "date": None,
        "deleted_user": None,
        "device": None,
        "directors": None,
        "do_notify": None,
        "duration": None,
        "email": None,
        "extra_type": None,
        "file": None,
        "file_size": None,
        "friendly_name": None,
        "full_title": None,
        "genres": None,
        "grandparent_guid": None,
        "grandparent_rating_key": None,
        "grandparent_thumb": None,
        "grandparent_title": None,
        "group_count": None,
        "group_ids": None,
        "guid": None,
        "height": None,
        "id": None,
        "indexes": None,
        "ip_address": None,
        "ip_address_public": None,
        "is_admin": None,
        "is_allow_sync": None,
        "is_home_user": None,
        "is_restricted": None,
        "keep_history": None,
        "labels": None,
        "last_viewed_at": None,
        "library_name": None,
        "live": None,
        "live_uuid": None,
        "local": None,
        "location": None,
        "machine_id": None,
        "media_index": None,
        "media_type": None,
        "optimized_version": None,
        "optimized_version_profile": None,
        "optimized_version_title": None,
        "original_title": None,
        "originally_available_at": None,
        "parent_guid": None,
        "parent_media_index": None,
        "parent_rating_key": None,
        "parent_thumb": None,
        "parent_title": None,
        "paused_counter": None,
        "percent_complete": None,
        "platform": None,
        "platform_name": None,
        "platform_version": None,
        "player": None,
        "pre_tautulli": None,
        "product": None,
        "product_version": None,
        "profile": None,
        "progress_percent": None,
        "quality_profile": None,
        "rating": None,
        "rating_image": None,
        "rating_key": None,
        "reference_id": None,
        "relay": None,
        "relayed": None,
        "row_id": None,
        "section_id": None,
        "secure": None,
        "selected": None,
        "session_id": None,
        "session_key": None,
        "shared_libraries": None,
        "sort_title": None,
        "started": None,
        "state": None,
        "stopped": None,
        "stream_aspect_ratio": None,
        "stream_audio_bitrate": None,
        "stream_audio_bitrate_mode": None,
        "stream_audio_channel_layout": None,
        "stream_audio_channel_layout_": None,
        "stream_audio_channels": None,
        "stream_audio_codec": None,
        "stream_audio_decision": None,
        "stream_audio_language": None,
        "stream_audio_language_code": None,
        "stream_audio_sample_rate": None,
        "stream_bitrate": None,
        "stream_container": None,
        "stream_container_decision": None,
        "stream_duration": None,
        "stream_subtitle_codec": None,
        "stream_subtitle_container": None,
        "stream_subtitle_decision": None,
        "stream_subtitle_forced": None,
        "stream_subtitle_format": None,
        "stream_subtitle_language": None,
        "stream_subtitle_language_code": None,
        "stream_subtitle_location": None,
        "stream_video_bit_depth": None,
        "stream_video_bitrate": None,
        "stream_video_codec": None,
        "stream_video_codec_level": None,
        "stream_video_decision": None,
        "stream_video_dynamic_range": None,
        "stream_video_framerate": None,
        "stream_video_full_resolution": None,
        "stream_video_height": None,
        "stream_video_language": None,
        "stream_video_language_code": None,
        "stream_video_ref_frames": None,
        "stream_video_resolution": None,
        "stream_video_scan_type": None,
        "stream_video_width": None,
        "studio": None,
        "sub_type": None,
        "subtitle_codec": None,
        "subtitle_container": None,
        "subtitle_decision": None,
        "subtitle_forced": None,
        "subtitle_format": None,
        "subtitle_language": None,
        "subtitle_language_code": None,
        "subtitle_location": None,
        "subtitles": None,
        "summary": None,
        "synced_version": None,
        "synced_version_profile": None,
        "tagline": None,
        "throttled": None,
        "thumb": None,
        "title": None,
        "transcode_audio_channels": None,
        "transcode_audio_codec": None,
        "transcode_container": None,
        "transcode_decision": None,
        "transcode_height": None,
        "transcode_hw_decode": None,
        "transcode_hw_decode_title": None,
        "transcode_hw_decoding": None,
        "transcode_hw_encode": None,
        "transcode_hw_encode_title": None,
        "transcode_hw_encoding": None,
        "transcode_hw_full_pipeline": None,
        "transcode_hw_requested": None,
        "transcode_key": None,
        "transcode_progress": None,
        "transcode_protocol": None,
        "transcode_speed": None,
        "transcode_throttled": None,
        "transcode_video_codec": None,
        "transcode_width": None,
        "type": None,
        "updated_at": None,
        "user": None,
        "user_id": None,
        "user_rating": None,
        "user_thumb": None,
        "username": None,
        "video_bit_depth": None,
        "video_bitrate": None,
        "video_codec": None,
        "video_codec_level": None,
        "video_decision": None,
        "video_dynamic_range": None,
        "video_frame_rate": None,
        "video_framerate": None,
        "video_full_resolution": None,
        "video_height": None,
        "video_language": None,
        "video_language_code": None,
        "video_profile": None,
        "video_ref_frames": None,
        "video_resolution": None,
        "video_scan_type": None,
        "video_width": None,
        "view_offset": None,
        "watched_status": None,
        "width": None,
        "writers": None,
        "year": None,
    }
    actors: list = None
    added_at: str = None
    allow_guest: int = None
    art: str = None
    aspect_ratio: str = None
    audience_rating: str = None
    audience_rating_image: str = None
    audio_bitrate: str = None
    audio_bitrate_mode: str = None
    audio_channel_layout: str = None
    audio_channels: str = None
    audio_codec: str = None
    audio_decision: str = None
    audio_language: str = None
    audio_language_code: str = None
    audio_profile: str = None
    audio_sample_rate: str = None
    bandwidth: str = None
    banner: str = None
    bif_thumb: str = None
    bitrate: str = None
    channel_icon: str = None
    channel_stream: int = None
    channel_title: str = None
    children_count: str = None
    collections: list = None
    container: str = None
    content_rating: str = None
    current_session: str = None
    date: str = None
    deleted_user: int = None
    device: str = None
    directors: list = None
    do_notify: int = None
    duration: str = None
    email: str = None
    extra_type: str = None
    file: str = None
    file_size: str = None
    friendly_name: str = None
    full_title: str = None
    genres: list = None
    grandparent_guid: str = None
    grandparent_rating_key: str = None
    grandparent_thumb: str = None
    grandparent_title: str = None
    group_count: int = None
    group_ids: str = None
    guid: str = None
    height: str = None
    id: str = None
    indexes: int = None
    ip_address: str = None
    ip_address_public: str = None
    is_admin: int = None
    is_allow_sync: int = None
    is_home_user: int = None
    is_restricted: int = None
    keep_history: int = None
    labels: list = None
    last_viewed_at: str = None
    library_name: str = None
    live: int = None
    live_uuid: str = None
    local: str = None
    location: str = None
    machine_id: str = None
    media_index: str = None
    media_type: str = None
    optimized_version: int = None
    optimized_version_profile: str = None
    optimized_version_title: str = None
    original_title: str = None
    originally_available_at: str = None
    parent_guid: str = None
    parent_media_index: str = None
    parent_rating_key: str = None
    parent_thumb: str = None
    parent_title: str = None
    paused_counter: int = None
    percent_complete: int = None
    platform: str = None
    platform_name: str = None
    platform_version: str = None
    player: str = None
    pre_tautulli: str = None
    product: str = None
    product_version: str = None
    profile: str = None
    progress_percent: str = None
    quality_profile: str = None
    rating: str = None
    rating_image: str = None
    rating_key: str = None
    reference_id: int = None
    relay: int = None
    relayed: int = None
    row_id: int = None
    section_id: str = None
    secure: str = None
    selected: int = None
    session_id: str = None
    session_key: str = None
    shared_libraries: list = None
    sort_title: str = None
    started: int = None
    state: str = None
    stopped: int = None
    stream_aspect_ratio: str = None
    stream_audio_bitrate: str = None
    stream_audio_bitrate_mode: str = None
    stream_audio_channel_layout: str = None
    stream_audio_channel_layout_: str = None
    stream_audio_channels: str = None
    stream_audio_codec: str = None
    stream_audio_decision: str = None
    stream_audio_language: str = None
    stream_audio_language_code: str = None
    stream_audio_sample_rate: str = None
    stream_bitrate: str = None
    stream_container: str = None
    stream_container_decision: str = None
    stream_duration: str = None
    stream_subtitle_codec: str = None
    stream_subtitle_container: str = None
    stream_subtitle_decision: str = None
    stream_subtitle_forced: int = None
    stream_subtitle_format: str = None
    stream_subtitle_language: str = None
    stream_subtitle_language_code: str = None
    stream_subtitle_location: str = None
    stream_video_bit_depth: str = None
    stream_video_bitrate: str = None
    stream_video_codec: str = None
    stream_video_codec_level: str = None
    stream_video_decision: str = None
    stream_video_dynamic_range: str = None
    stream_video_framerate: str = None
    stream_video_full_resolution: str = None
    stream_video_height: str = None
    stream_video_language: str = None
    stream_video_language_code: str = None
    stream_video_ref_frames: str = None
    stream_video_resolution: str = None
    stream_video_scan_type: str = None
    stream_video_width: str = None
    studio: str = None
    sub_type: str = None
    subtitle_codec: str = None
    subtitle_container: str = None
    subtitle_decision: str = None
    subtitle_forced: int = None
    subtitle_format: str = None
    subtitle_language: str = None
    subtitle_language_code: str = None
    subtitle_location: str = None
    subtitles: int = None
    summary: str = None
    synced_version: int = None
    synced_version_profile: str = None
    tagline: str = None
    throttled: str = None
    thumb: str = None
    title: str = None
    transcode_audio_channels: str = None
    transcode_audio_codec: str = None
    transcode_container: str = None
    transcode_decision: str = None
    transcode_height: str = None
    transcode_hw_decode: str = None
    transcode_hw_decode_title: str = None
    transcode_hw_decoding: int = None
    transcode_hw_encode: str = None
    transcode_hw_encode_title: str = None
    transcode_hw_encoding: int = None
    transcode_hw_full_pipeline: int = None
    transcode_hw_requested: int = None
    transcode_key: str = None
    transcode_progress: int = None
    transcode_protocol: str = None
    transcode_speed: str = None
    transcode_throttled: int = None
    transcode_video_codec: str = None
    transcode_width: str = None
    type: str = None
    updated_at: str = None
    user: str = None
    user_id: int = None
    user_rating: str = None
    user_thumb: str = None
    username: str = None
    video_bit_depth: str = None
    video_bitrate: str = None
    video_codec: str = None
    video_codec_level: str = None
    video_decision: str = None
    video_dynamic_range: str = None
    video_frame_rate: str = None
    video_framerate: str = None
    video_full_resolution: str = None
    video_height: str = None
    video_language: str = None
    video_language_code: str = None
    video_profile: str = None
    video_ref_frames: str = None
    video_resolution: str = None
    video_scan_type: str = None
    video_width: str = None
    view_offset: str = None
    watched_status: int = None
    width: str = None
    writers: list = None
    year: str = None


# Lidarr
class LidarrQueue(DynamicNamedTuple):
    artistId: int = None
    albumId: int = None
    language: dict = None
    quality: dict = None
    size: float = None
    title: str = None
    timeleft: str = None
    sizeleft: float = None
    status: str = None
    trackedDownloadStatus: str = None
    trackedDownloadState: str = None
    statusMessages: list = None
    errorMessage: str = None
    downloadId: str = None
    protocol: str = None
    downloadClient: str = None
    indexer: str = None
    outputPath: str = None
    downloadForced: bool = None
    id: int = None
    estimatedCompletionTime: str = None


class LidarrAlbum(DynamicNamedTuple):
    title: str = None
    disambiguation: str = None
    overview: str = None
    artistId: int = None
    foreignAlbumId: str = None
    monitored: bool = None
    anyReleaseOk: bool = None
    profileId: int = None
    duration: int = None
    albumType: str = None
    secondaryTypes: list = None
    mediumCount: int = None
    ratings: dict = None
    releaseDate: str = None
    releases: list = None
    genres: list = None
    media: list = None
    artist: dict = None
    images: list = None
    links: list = None
    statistics: dict = {}
    id: int = None
