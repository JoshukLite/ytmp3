import glob
import json
import logging
import os
import urllib

from pydub import AudioSegment

# supported_extensions = ['webm', 'm4a', 'wav']
specialchars = ['<', '>', ':', '"', '\'', '/', '\\', '|', '?', '*', '.']


def get_local_audios(dir):
	logging.info("Gethering all local audios from '%s'", dir)

	local_audios = []

	os.chdir(dir)
	# get only mp3 files
	for local_audio in glob.glob(u'*.mp3'):
		filename, extension = get_filename_with_extension(local_audio)
		local_audios.append(filename)

	return local_audios


def convert_all_files_to_mp3(dir, tempdir):
	logging.info('Converting files to mp3, working directory - "%s"', os.path.abspath(dir))

	os.chdir(tempdir)
	for audio in glob.glob(u'*.*'):
		convertToMp3(audio, dir)

	logging.info('Finished converting files to mp3')


def convertToMp3(file, dir):
	logging.info('Converting %s', file)

	filename, extension = get_filename_with_extension(file)

	audio = AudioSegment.from_file(file, extension)

	abs_filename = os.path.join(dir, filename + '.mp3')
	
	audio.export(abs_filename, format='mp3')


def clean_temp_dir(tempdir):
	logging.info('Cleaning temp files')

	os.chdir(tempdir)
	for file in glob.glob(u'*.*'):
		os.remove(file)

	os.chdir('..')

	os.rmdir(tempdir)

	logging.info('Finished cleaning temp files')


def get_filename_with_extension(file):
	filename, dot, extension = file.partition('.')
	return filename, extension


def generate_video_title(videoTitle, videoId, extension=None):
	# use unicode video title (pafy can't recognize this by default) + videoId to avoid duplicate errors
	videoTitle = unicode(videoTitle) + ' [{}]'.format(videoId)

	for char in specialchars:
		videoTitle = videoTitle.replace(char, '')

	if extension is not None:
		videoTitle += '.{0}'.format(extension)

	return videoTitle


def json_url_open(url):
	logging.debug('Request to: %s', url)

	logging.debug('Performing request')
	response = urllib.urlopen(url)

	logging.debug('Parsing response')
	jsonResponse = json.load(response)

	response.close()

	logging.debug('Response as json: %s', json.dumps(jsonResponse, indent=4))

	return jsonResponse
