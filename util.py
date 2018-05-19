import constants
import glob
import json
import logging
import mutagen
import os
import urllib
import urlparse

from pydub import AudioSegment

# supported_extensions = ['webm', 'm4a', 'wav']
special_chars = ['<', '>', ':', '"', '\'', '/', '\\', '|', '?', '*', '.']


def get_local_audios(working_dir):
    logging.info("Gethering all local audios from '%s'", dir)

    working_dir = os.path.join(working_dir, '')

    local_audios = set()

    # get only mp3 files
    for local_audio in glob.glob(u'{0}/*.mp3'.format(working_dir)):
        filename_only = local_audio[len(working_dir):]
        filename, extension = get_filename_with_extension(filename_only)
        local_audios.add(filename)

    return local_audios


def get_last_track_number(working_dir, album=None):
    logging.info('Searching for last track number in album')

    files = glob.glob(u'{0}/*.mp3'.format(working_dir))
    if album:
        max_track_number = 0
        for audio in files:
            info = mutagen.File(audio)

            audio_album = None
            mutagen_audio_album = info.get('TALB')
            if mutagen_audio_album:
                audio_album = mutagen_audio_album.text[0]

            mutagen_track_number = info.get('TRCK')

            try:
                if mutagen_track_number:
                    track_number = int(mutagen_track_number.text[0])
            except:
                logging.debug('Track number error, must be integer, current value is "%s"', info.get('TRCK'))
                track_number = 0

            if audio_album == album and track_number > max_track_number:
                max_track_number = track_number
    else:
        max_track_number = 0

    return max_track_number


def get_filename_with_extension(filename):
    filename, dot, extension = filename.partition('.')
    return filename, extension


def get_image_name(str_input):
    return hash(str_input)


def get_temp_subdirs():
    temp_subdirs = [
        constants.IMAGE_TEMP_DIR,
        constants.VIDEO_TEMP_DIR
    ]

    return temp_subdirs


def get_url_params(url):
    parameters = dict()

    parse_res = urlparse.urlparse(url)
    if parse_res.query:
        qsl_res = urlparse.parse_qsl(parse_res.query)
        for param in qsl_res:
            parameters[param[0]] = param[1]

    return parameters


def convert_to_mp3(audio_title, video_id, working_dir, album_name=None, track_number=None):
    logging.info('Converting %s', audio_title)

    video_tempdir = os.path.join(working_dir, constants.ROOT_TEMP_DIR, constants.VIDEO_TEMP_DIR)
    cover_dir = os.path.join(working_dir, constants.ROOT_TEMP_DIR, constants.IMAGE_TEMP_DIR)

    raw_audio_path_name = os.path.join(video_tempdir, video_id)
    raw_audio_path = glob.glob('{0}.*'.format(raw_audio_path_name))[0]

    filename, extension = get_filename_with_extension(raw_audio_path)

    audio = AudioSegment.from_file(raw_audio_path, extension)

    abs_filename = os.path.join(working_dir, generate_video_title(audio_title, video_id, 'mp3'))

    audio_tags = dict()

    if album_name:
        audio_tags['album'] = album_name
        audio_tags['track'] = track_number

    cover_path_name = os.path.join(cover_dir, str(video_id))
    image_path = glob.glob('{0}.*'.format(cover_path_name))[0]

    audio.export(abs_filename, format='mp3', tags=audio_tags, cover=image_path)


# root - absolute path to working directory
def create_temp_dir(root):
    logging.info('Creating temp dirs')

    temp_subdirs = get_temp_subdirs()

    root_temp = os.path.join(root, constants.ROOT_TEMP_DIR)

    os.makedirs(root_temp)

    for temp_subdir in temp_subdirs:
        os.makedirs(os.path.join(root_temp, temp_subdir))

    logging.info('Finished creating temp dirs')


# root - absolute path to working directory
def clean_temp_dir(root):
    logging.info('Cleaning temp files')

    root_temp = os.path.join(root, constants.ROOT_TEMP_DIR)
    temp_subdirs = get_temp_subdirs()

    if os.path.exists(root_temp):

        for temp_subdir in temp_subdirs:
            temp_subdir_path = os.path.join(root_temp, temp_subdir)
            if os.path.exists(temp_subdir_path):
                for temp_file in glob.glob(u'{0}/*.*'.format(temp_subdir_path)):
                    os.remove(temp_file)
                os.rmdir(temp_subdir_path)

        os.rmdir(root_temp)

        logging.info('Finished cleaning temp files')
    else:
        logging.info('Skipping ...')


def generate_video_title(video_title, video_id, extension=None):
    # use unicode video title + videoId to avoid duplicate errors
    video_title = unicode(video_title) + ' [{}]'.format(video_id)

    for char in special_chars:
        video_title = video_title.replace(char, '')

    if extension is not None:
        video_title += '.{0}'.format(extension)

    return video_title


def json_url_open(url):
    logging.debug('Request to: %s', url)

    logging.debug('Performing request')
    response = urllib.urlopen(url)

    logging.debug('Parsing response')
    json_response = json.load(response)

    response.close()

    logging.debug('Response as json: %s', json.dumps(json_response, indent=4))

    return json_response
