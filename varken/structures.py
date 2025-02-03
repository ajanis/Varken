from sys import version_info
from typing import Optional
from logging import getLogger

logger = getLogger('temp')
# Check for python3.6 or newer to resolve erroneous typing.NamedTuple issues
if version_info < (3, 6, 2):
    logger.error('Varken requires python3.6.2 or newer. You are on python%s.%s.%s - Exiting...',
                 version_info.major, version_info.minor, version_info.micro)
    exit(1)


class FieldDefaultsMeta(type):
    """Metaclass for applying defaults to fields."""

    def __new__(cls, name, bases, dct):
        """Initialize the new class."""
        new_cls = super().__new__(cls, name, bases, dct)

        # Gather field defaults from class attributes
        field_defaults = {}

        for key, value in dct.items():
            # Ignore special methods and internal attributes
            if not key.startswith('__') and not callable(value):
                field_defaults[key] = value

        # Attach the field defaults to the new class
        new_cls._field_defaults = field_defaults

        return new_cls


class BaseModel(metaclass=FieldDefaultsMeta):
    """Base class to handle dynamic fields from APIs."""

    def __init__(self, *args, **kwargs):
        # Ensure the number of positional arguments does not exceed defined fields
        field_names = list(self.__annotations__.keys())
        provided_args = len(args)

        # Assign positional arguments
        for idx, arg in enumerate(args):
            setattr(self, field_names[idx], arg)

        # Assign keyword arguments or use default values from _field_defaults
        for field_name in field_names[provided_args:]:
            if field_name in kwargs:
                setattr(self, field_name, kwargs[field_name])
            else:
                # Use default from _field_defaults, or None if not provided
                setattr(self, field_name, self._field_defaults.get(field_name))

        # Make the instance immutable by setting __setattr__
        self._make_immutable()

    def _make_immutable(self):
        """Make the instance immutable by preventing attribute setting."""
        def readonly_setattr(self, name, value):
            raise AttributeError(f"Cannot modify attribute '{name}' once set")

        self.__setattr__ = readonly_setattr

    def __repr__(self):
        """Provide a readable representation of the object."""
        field_reprs = ', '.join(f"{name}={getattr(self, name)!r}" for name in self.__dict__)
        return f"{self.__class__.__name__}({field_reprs})"


# Server Structures
class InfluxServer(BaseModel):
    password: str = 'root'
    port: int = 8086
    ssl: bool = False
    url: str = 'localhost'
    username: str = 'root'
    verify_ssl: bool = False
    org: str = '-'

class Influx2Server(BaseModel):
    url: str = 'localhost'
    org: str = 'server'
    token: str = 'TOKEN'
    bucket: str = 'varken'
    timeout: int = 10000
    ssl: bool = False
    verify_ssl: bool = False

class SonarrServer(BaseModel):
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

class RadarrServer(BaseModel):
    api_key: str = None
    get_missing: bool = False
    get_missing_run_seconds: int = 30
    id: int = None
    queue: bool = False
    queue_run_seconds: int = 30
    url: str = None
    verify_ssl: bool = False

class OmbiServer(BaseModel):
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

class OverseerrServer(BaseModel):
    api_key: str = None
    id: int = None
    url: str = None
    verify_ssl: bool = False
    get_request_total_counts: bool = False
    request_total_run_seconds: int = 30
    num_latest_requests_to_fetch: int = 10
    num_latest_requests_seconds: int = 30

class TautulliServer(BaseModel):
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

class SickChillServer(BaseModel):
    api_key: str = None
    get_missing: bool = False
    get_missing_run_seconds: int = 30
    id: int = None
    url: str = None
    verify_ssl: bool = False

class UniFiServer(BaseModel):
    get_usg_stats_run_seconds: int = 30
    id: int = None
    password: str = 'ubnt'
    site: str = None
    url: str = 'unifi.domain.tld:8443'
    username: str = 'ubnt'
    usg_name: str = None
    verify_ssl: bool = False


# Shared
class QueuePages(BaseModel):
    page: int = None
    pageSize: int = None
    sortKey: str = None
    sortDirection: str = None
    totalRecords: str = None
    records: Optional[list] = None


# Ombi Structures
class OmbiRequestCounts(BaseModel):
    approved: int = 0
    available: int = 0
    pending: int = 0


class OmbiIssuesCounts(BaseModel):
    inProgress: int = 0
    pending: int = 0
    resolved: int = 0


class OmbiTVRequest(BaseModel):
    background: str = None
    childRequests: Optional[list] = None
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


class OmbiMovieRequest(BaseModel):
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
    requestedUser: Optional[dict] = None
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
class OverseerrRequestCounts(BaseModel):
    pending: int = None
    approved: int = None
    processing: int = None
    available: int = None
    total: int = None
    movie: int = None
    tv: int = None
    declined: int = None


# Sonarr
class SonarrTVShow(BaseModel):
    added: str = None
    airTime: str = None
    alternateTitles: Optional[list] = None
    certification: str = None
    cleanTitle: str = None
    ended: bool = None
    firstAired: str = None
    genres: Optional[list] = None
    id: int = None
    images: Optional[list] = None
    imdbId: str = None
    languageProfileId: int = None
    monitored: bool = None
    nextAiring: str = None
    network: str = None
    overview: str = None
    path: str = None
    previousAiring: str = None
    qualityProfileId: int = None
    ratings: Optional[dict] = None
    rootFolderPath: str = None
    runtime: int = None
    seasonFolder: bool = None
    seasons: Optional[list] = None
    seriesType: str = None
    sortTitle: str = None
    statistics: Optional[dict] = None
    status: str = None
    tags: Optional[list] = None
    title: str = None
    titleSlug: str = None
    tvdbId: int = None
    tvMazeId: int = None
    tvRageId: int = None
    useSceneNumbering: bool = None
    year: int = None


class SonarrEpisode(BaseModel):
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
    series: Optional[SonarrTVShow] = None
    tvdbId: int = None
    finaleType: str = None
    episodeFile: Optional[dict] = None
    endTime: str = None
    grabTime: str = None
    seriesTitle: str = None
    images: Optional[list] = None


class SonarrQueue(BaseModel):
    downloadClient: str = None
    downloadId: str = None
    episodeId: int = None
    id: int = None
    indexer: str = None
    language: Optional[dict] = None
    protocol: str = None
    quality: Optional[dict] = None
    size: float = None
    sizeleft: float = None
    status: str = None
    statusMessages: Optional[list] = None
    title: str = None
    trackedDownloadState: str = None
    trackedDownloadStatus: str = None
    seriesId: int = None
    errorMessage: str = None
    outputPath: str = None
    series: Optional[SonarrTVShow] = None
    episode: Optional[SonarrEpisode] = None
    timeleft: str = None
    estimatedCompletionTime: str = None


# Radarr
class RadarrMovie(BaseModel):
    added: str = None
    alternateTitles: Optional[list] = None
    certification: str = None
    cleanTitle: str = None
    collection: Optional[dict] = None
    digitalRelease: str = None
    folderName: str = None
    genres: Optional[list] = None
    hasFile: bool = None
    id: int = None
    images: Optional[list] = None
    imdbId: str = None
    inCinemas: str = None
    isAvailable: bool = None
    minimumAvailability: str = None
    monitored: bool = None
    movieFile: Optional[dict] = None
    originalTitle: str = None
    overview: str = None
    path: str = None
    physicalRelease: str = None
    qualityProfileId: int = None
    ratings: Optional[dict] = None
    runtime: int = None
    secondaryYear: int = None
    secondaryYearSourceId: int = None
    sizeOnDisk: float = None
    sortTitle: str = None
    status: str = None
    studio: str = None
    tags: Optional[list] = None
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
    statistics: Optional[dict] = None
    movieFileId: int = None


# Radarr Queue
class RadarrQueue(BaseModel):
    customFormats: Optional[list] = None
    downloadClient: str = None
    downloadId: str = None
    id: int = None
    indexer: str = None
    languages: Optional[list] = None
    movieId: int = None
    protocol: str = None
    quality: Optional[dict] = None
    size: float = None
    sizeleft: float = None
    status: str = None
    statusMessages: Optional[list] = None
    title: str = None
    trackedDownloadState: str = None
    trackedDownloadStatus: str = None
    timeleft: str = None
    estimatedCompletionTime: str = None
    errorMessage: str = None
    outputPath: str = None
    movie: Optional[RadarrMovie] = None
    timeleft: str = None
    customFormatScore: int = None
    indexerFlags: int = None
    added: str = None
    downloadClientHasPostImportCategory: bool = None


# Sickchill
class SickChillTVShow(BaseModel):
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
class TautulliStream(BaseModel):
    actors: Optional[list] = None
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
    collections: Optional[list] = None
    container: str = None
    content_rating: str = None
    current_session: str = None
    date: str = None
    deleted_user: int = None
    device: str = None
    directors: Optional[list] = None
    do_notify: int = None
    duration: str = None
    email: str = None
    extra_type: str = None
    file: str = None
    file_size: str = None
    friendly_name: str = None
    full_title: str = None
    genres: Optional[list] = None
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
    labels: Optional[list] = None
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
    shared_libraries: Optional[list] = None
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
    writers: Optional[list] = None
    year: str = None


# Lidarr
class LidarrQueue(BaseModel):
    artistId: int = None
    albumId: int = None
    language: Optional[dict] = None
    quality: Optional[dict] = None
    size: float = None
    title: str = None
    timeleft: str = None
    sizeleft: float = None
    status: str = None
    trackedDownloadStatus: str = None
    trackedDownloadState: str = None
    statusMessages: Optional[list] = None
    errorMessage: str = None
    downloadId: str = None
    protocol: str = None
    downloadClient: str = None
    indexer: str = None
    outputPath: str = None
    downloadForced: bool = None
    id: int = None
    estimatedCompletionTime: str = None


class LidarrAlbum(BaseModel):
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
    secondaryTypes: Optional[list] = None
    mediumCount: int = None
    ratings: Optional[dict] = None
    releaseDate: str = None
    releases: Optional[list] = None
    genres: Optional[list] = None
    media: Optional[list] = None
    artist: Optional[dict] = None
    images: Optional[list] = None
    links: Optional[list] = None
    statistics: dict = {}
    id: int = None
