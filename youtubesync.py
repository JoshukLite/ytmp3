import argparse
import logging
import os
import re
import traceback

from youtubeservice import download_audio_from_video
from youtubeservice import get_playlist_info
from youtubeservice import get_playlist_videos_url
from youtubeservice import get_videos_from_playlist
from youtubeservice import synchronize_audios

from util import clean_temp_dir
from util import convert_all_files_to_mp3


parser = argparse.ArgumentParser(description='This script finds all videos from Youtube given playlist')

parser.add_argument('-k', '--key', dest='key', action='store', required=True, help='Google Data API key.')
parser.add_argument('-p', '--playlist', dest='playlist', action='store', required=True, help='Youtube playlist id to get videos from')
parser.add_argument('-f', '--folder', dest='folder', action='store', required=False, help='Working directory, where to download and store files, absolute path')

outputDetailLevel = parser.add_mutually_exclusive_group()
outputDetailLevel.add_argument('-q', '--quiet', dest='quiet', action='store_true', default=False, help='Print out minimum result information, errors')
outputDetailLevel.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=True, help='Print out detailed information about work progress')
outputDetailLevel.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Print out all messages and details')

args = parser.parse_args()


if args.debug:
	LOG_LEVEL=logging.DEBUG
elif args.verbose:
	LOG_LEVEL=logging.INFO
elif args.quiet:
	LOG_LEVEL=logging.ERROR
else:
	LOG_LEVEL=logging.WARN

if args.folder is None:
	workingdir = os.path.abspath(__file__)
else:
	workingdir = re.sub('["|\']+', '', args.folder)

tempworkingdir = os.path.join(workingdir, 'temp')


def main():
	try:
		descr = get_playlist_info(args.key, args.playlist)
		all_videos = get_videos_from_playlist(args.key, args.playlist)
		filtered_videos = synchronize_audios(all_videos, workingdir)
		urls = get_playlist_videos_url(filtered_videos)
		download_audio_from_video(urls, dir=tempworkingdir)
		convert_all_files_to_mp3(dir=workingdir, tempdir=tempworkingdir)
		clean_temp_dir(tempworkingdir)
	except Exception as e:
		logging.error('Something went wrong, %s', str(e))
		logging.debug(traceback.print_exc())


if __name__ == '__main__':
	logging.basicConfig(
		level=LOG_LEVEL,
		format='[%(asctime)s] [%(levelname)s] - %(message)s', 
		datefmt='%H:%M:%S')
	main()
