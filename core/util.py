import constants
import glob
import json
import logging
import mutagen
import mutagen.id3
import os
import shutil
import urllib
import urlparse

# supported_extensions = ['webm', 'm4a', 'wav']
special_chars = ['<', '>', ':', '"', '\'', '/', '\\', '|', '?', '*', '.']


def add_audio_metainfo(file_path, **kwargs):
    if not os.path.exists(file_path):
        raise IOError(u'Add audio metainfo failed, audio file not found - {0}'.format(file_path))
    if not os.path.isfile(file_path):
        raise IOError(u'Add audio metainfo failed, specified path is not file - {0}'.format(file_path))

    audio = mutagen.File(file_path)

    cover_path = kwargs.get('cover_path')
    album = kwargs.get('album')
    track_num = kwargs.get('track_num')

    # add image cover
    if cover_path:
        with open(cover_path, 'rb') as image_file:
            image_data = image_file.read()
        audio.tags.add(mutagen.id3.APIC(
            encoding=3,
            mime='image/jpeg',
            type=0,
            data=image_data
        ))
    # add album name
    if album:
        audio.tags.add(mutagen.id3.TALB(
            encoding=3,
            text=album
        ))
    # add track number
    if track_num:
        audio.tags.add(mutagen.id3.TRCK(
            encoding=3,
            text=str(track_num)
        ))

    audio.save()

    pass


def get_local_audios(working_dir):
    logging.info("Gethering all local audios from '%s'", working_dir)

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
            except ValueError:
                logging.debug('Track number error, must be integer, current value is "%s"', info.get('TRCK'))
                track_number = 0

            if audio_album == album and track_number > max_track_number:
                max_track_number = track_number
    else:
        max_track_number = 0

    return max_track_number


def get_filename_with_extension(filename):
    filename, dot, extension = filename.rpartition('.')
    return filename, extension


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


def copy(input_file, output_file, remove_old=False):
    if os.path.exists(input_file):
        if os.path.isfile(input_file):
            if not os.path.exists(os.path.dirname(output_file)):
                os.makedirs(os.path.dirname(output_file))
            shutil.copy2(input_file, output_file)
            if remove_old:
                os.remove(input_file)
        else:
            raise IOError('Copy failed, input path is not file - {0}'.format(input_file))
    else:
        raise IOError('Copy failed, input file not found - {0}'.format(input_file))


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


def generate_video_title(video_title, video_id, extension=None, clean=None):
    # use unicode video title + videoId to avoid duplicate errors
    video_title = unicode(video_title) + ' [{}]'.format(video_id)

    if clean:
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
