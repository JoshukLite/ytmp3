import glob
import httplib
import json
import logging
import mutagen
import os
import urllib

from pydub import AudioSegment

# supported_extensions = ['webm', 'm4a', 'wav']
special_chars = ['<', '>', ':', '"', '\'', '/', '\\', '|', '?', '*', '.']
MAX_ATTEMPT = 5


def get_local_audios(dir):
    logging.info("Gethering all local audios from '%s'", dir)

    local_audios = set()

    os.chdir(dir)
    # get only mp3 files
    for local_audio in glob.glob(u'*.mp3'):
        filename, extension = get_filename_with_extension(local_audio)
        local_audios.add(filename)

    return local_audios


def get_last_track_number(working_dir, album=None):
    logging.info('Searching for last track number in album')

    os.chdir(working_dir)
    files = glob.glob(u'*.mp3')
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


def convert_all_files_to_mp3(working_dir, video_tempdir, image_tempdir, album=None, track_number=0):
    logging.info('Converting files to mp3, working directory - "%s"', os.path.abspath(working_dir))

    os.chdir(video_tempdir)
    files = glob.glob(u'*.*')
    files.sort(key=os.path.getmtime)
    for audio in files:
        track_number += 1
        convert_to_mp3(audio, working_dir, image_tempdir, album, track_number)

    logging.info('Finished converting files to mp3')


def convert_to_mp3(audio_file, working_dir, cover_dir, album_name=None, track_number=None):
    logging.info('Converting %s', audio_file)

    filename, extension = get_filename_with_extension(audio_file)

    audio = AudioSegment.from_file(audio_file, extension)

    abs_filename = os.path.join(working_dir, filename + '.mp3')

    audio_tags = dict()

    if album_name:
        audio_tags['album'] = album_name
        audio_tags['track'] = track_number

    cover_name = get_image_name(audio_file)
    cover_path_name = os.path.join(cover_dir, str(cover_name))
    image_path = glob.glob('{}.*'.format(cover_path_name))[0]

    audio.export(abs_filename, format='mp3', tags=audio_tags, cover=image_path)


def create_temp_dir(root, *args):
    logging.info('Creating temp dirs')

    # if dir is None, use 'temp' dir to store videos and images
    if root is None:
        root = os.path.join(os.getcwd(), 'temp')

    os.makedirs(root)

    for temp_subdir in args:
        os.makedirs(os.path.join(root, temp_subdir))

    logging.info('Finished creating temp dirs')


def clean_temp_dir(root, *args):
    logging.info('Cleaning temp files')

    if os.path.exists(root):
        os.chdir(root)

        for temp_subdir in args:
            for temp_file in glob.glob(u'./{}/*.*'.format(temp_subdir)):
                os.remove(temp_file)
            os.rmdir(temp_subdir)

        os.chdir('..')
        os.rmdir(root)

        logging.info('Finished cleaning temp files')
    else:
        logging.info('Skipping ...')


def get_filename_with_extension(file):
    filename, dot, extension = file.partition('.')
    return filename, extension


def generate_video_title(video_title, video_id, extension=None):
    # use unicode video title (pafy can't recognize this by default) + videoId to avoid duplicate errors
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


def download_image(temp_dir, url, video_full_name):
    image_full_name = url[url.rfind('/') + 1:]

    url_image_name, image_extension = get_filename_with_extension(image_full_name)

    image_name = get_image_name(video_full_name)
    new_image_name = '{}.{}'.format(image_name, image_extension)

    done = False
    attempt = 0
    while not done:
        try:
            urllib.urlretrieve(url, os.path.join(temp_dir, new_image_name))
            done = True
        except httplib.BadStatusLine as bsl:
            attempt += 1
            if attempt > MAX_ATTEMPT:
                raise bsl
            logging.info("Error while downloading thumbnail, performing {0} attempt".format(attempt))


def get_image_name(str_input):
    return hash(str_input)
