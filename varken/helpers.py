from hashlib import md5
from os import makedirs
from os.path import isdir
from logging import getLogger
from ipaddress import IPv4Address
from urllib3 import disable_warnings
from json.decoder import JSONDecodeError
from urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import InvalidSchema, SSLError, ConnectionError, ChunkedEncodingError

logger = getLogger()


def hashit(string):
    encoded = string.encode()
    hashed = md5(encoded).hexdigest()

    return hashed


def rfc1918_ip_check(ip):
    rfc1918_ip = IPv4Address(ip).is_private

    return rfc1918_ip


def connection_handler(session, request, verify, as_is_reply=False):
    air = as_is_reply
    s = session
    r = request
    v = verify
    return_json = False

    disable_warnings(InsecureRequestWarning)

    try:
        get = s.send(r, verify=v)
        if get.status_code == 401:
            if 'NoSiteContext' in str(get.content):
                logger.info('Your Site is incorrect for %s', r.url)
            elif 'LoginRequired' in str(get.content):
                logger.info('Your login credentials are incorrect for %s', r.url)
            else:
                logger.info('Your api key is incorrect for %s', r.url)
        elif get.status_code == 404:
            logger.info('This url doesnt even resolve: %s', r.url)
        elif get.status_code == 200:
            try:
                return_json = get.json()
            except JSONDecodeError:
                logger.error('No JSON response. Response is: %s', get.text)
        if air:
            return get
    except InvalidSchema:
        logger.error("You added http(s):// in the config file. Don't do that.")
    except SSLError as e:
        logger.error('Either your host is unreachable or you have an SSL issue. : %s', e)
    except ConnectionError as e:
        logger.error('Cannot resolve the url/ip/port. Check connectivity. Error: %s', e)
    except ChunkedEncodingError as e:
        logger.error('Broken connection during request... oops? Error: %s', e)

    return return_json


def mkdir_p(path):
    templogger = getLogger('temp')
    try:
        if not isdir(path):
            templogger.info('Creating folder %s ', path)
            makedirs(path, exist_ok=True)
    except Exception as e:
        templogger.error('Could not create folder %s : %s ', path, e)


def clean_sid_check(server_id_list, server_type=None):
    t = server_type
    sid_list = server_id_list
    cleaned_list = sid_list.replace(' ', '').split(',')
    valid_sids = []
    for sid in cleaned_list:
        try:
            valid_sids.append(int(sid))
        except ValueError:
            logger.error("%s is not a valid server id number", sid)
    if valid_sids:
        logger.info('%s : %s', t.upper(), valid_sids)
        return valid_sids
    else:
        logger.error('No valid %s', t.upper())
        return False


def boolcheck(var):
    if var.lower() in ['true', 'yes']:
        return True
    else:
        return False


def itemgetter_with_default(**defaults):
    return lambda obj: tuple(obj.get(k, v) for k, v in defaults.items())
