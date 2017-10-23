import argparse
import logging
import os
import re
import traceback

from youtubeservice import download_data_from_video
from youtubeservice import get_playlist_info
from youtubeservice import get_playlist_videos_url
from youtubeservice import get_videos_from_playlist
from youtubeservice import synchronize_audios

from util import clean_temp_dir
from util import create_temp_dir
from util import convert_all_files_to_mp3
from util import get_last_track_number


parser = argparse.ArgumentParser(description='This script finds all videos from Youtube given playlist')

parser.add_argument('-k', '--key', dest='key', action='store', required=True, help='Google Data API key.')
parser.add_argument('-p', '--playlist', dest='playlist', action='store', required=True, help='Youtube playlist id to get videos from')
parser.add_argument('-f', '--folder', dest='folder', action='store', required=False, help='Working directory, where to download and store files, absolute path')
parser.add_argument('-a', '--album', dest='album', action='store', required=False, help='Album name to save tracks with, also makes sync only with album if exist')

outputDetailLevel = parser.add_mutually_exclusive_group()
outputDetailLevel.add_argument('-q', '--quiet', dest='quiet', action='store_true', default=False, help='Print out minimum result information, errors')
outputDetailLevel.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=True, help='Print out detailed information about work progress')
outputDetailLevel.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Print out all messages and details')

args = parser.parse_args()


if args.debug:
    LOG_LEVEL = logging.DEBUG
elif args.verbose:
    LOG_LEVEL = logging.INFO
elif args.quiet:
    LOG_LEVEL = logging.ERROR
else:
    LOG_LEVEL = logging.WARN

if args.folder is None:
    working_dir = os.path.abspath(__file__)
else:
    working_dir = re.sub('["|\']+', '', args.folder)


VIDEO_TEMP_DIR = 'video'
IMAGE_TEMP_DIR = 'image'

temp_working_dir = os.path.join(working_dir, 'temp')
video_tempdir = os.path.join(temp_working_dir, VIDEO_TEMP_DIR)
image_tempdir = os.path.join(temp_working_dir, IMAGE_TEMP_DIR)


def main():
    try:
        clean_temp_dir(temp_working_dir, VIDEO_TEMP_DIR, IMAGE_TEMP_DIR)
        create_temp_dir(temp_working_dir, VIDEO_TEMP_DIR, IMAGE_TEMP_DIR)
        descr = get_playlist_info(args.key, args.playlist)
        all_videos = get_videos_from_playlist(args.key, args.playlist)
        filtered_videos = synchronize_audios(all_videos, working_dir)
        urls = get_playlist_videos_url(filtered_videos)
        download_data_from_video(urls, video_tempdir, image_tempdir)
        last_track_number = get_last_track_number(working_dir=working_dir, album=args.album)
        convert_all_files_to_mp3(working_dir=working_dir, video_tempdir=video_tempdir,
                                 image_tempdir=image_tempdir, track_number=last_track_number)
        clean_temp_dir(temp_working_dir, VIDEO_TEMP_DIR, IMAGE_TEMP_DIR)
    except Exception as e:
        logging.error('Something went wrong, %s', str(e))
        clean_temp_dir(temp_working_dir, VIDEO_TEMP_DIR, IMAGE_TEMP_DIR)
        logging.debug(traceback.print_exc())


if __name__ == '__main__':
    logging.basicConfig(
        level=LOG_LEVEL,
        format='[%(asctime)s] [%(levelname)s] - %(message)s',
        datefmt='%H:%M:%S')
    main()
