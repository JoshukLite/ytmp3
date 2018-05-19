import argparse
import logging
import os
import re
import sys
import traceback

from youtubeservice import save_mp3
from youtubeservice import get_playlist_info
from youtubeservice import get_playlist_video_info
from youtubeservice import get_single_video_urls
from youtubeservice import get_videos_from_playlist
from youtubeservice import synchronize_audios

from util import clean_temp_dir
from util import create_temp_dir
from util import get_last_track_number


parser = argparse.ArgumentParser(description='This script finds all videos from Youtube given playlist')

parser.add_argument('-k', '--key', dest='key', action='store', required=False, help='Google Data API key.')
parser.add_argument('-f', '--folder', dest='folder', action='store', required=False, help='Working directory, where to download and store files, absolute path')
parser.add_argument('-a', '--album', dest='album', action='store', required=False, help='Album name to save tracks with, also makes sync only with album if exist')

linkIdType = parser.add_mutually_exclusive_group(required=True)
linkIdType.add_argument('-p', '--playlist', dest='playlist', action='store', help='Youtube playlist id to get videos from')
linkIdType.add_argument('-s', '--single', dest='single', action='store', help='Youtube video id to download')

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
    working_dir = os.path.dirname(os.path.abspath(__file__))
else:
    working_dir = re.sub('["|\']+', '', args.folder)


def main():
    try:
        clean_temp_dir(working_dir)
        create_temp_dir(working_dir)

        if args.playlist:
            if not args.key:
                logging.error("Please specify Google Data API key when you're using playlist downloader")
                exit()
            descr = get_playlist_info(args.key, args.playlist)
            all_videos = get_videos_from_playlist(args.key, args.playlist)
            filtered_videos = synchronize_audios(all_videos, working_dir)
            video_info_list = get_playlist_video_info(filtered_videos)
        else:
            video_info_list = get_single_video_urls(args.single)

        if len(video_info_list) < 1:
            logging.info("No audios to download. All items are synchronized.")
            sys.exit()

        last_track_number = get_last_track_number(working_dir=working_dir, album=args.album)
        save_mp3(video_info_list, working_dir, args.album, last_track_number)
    except Exception as e:
        logging.error('Something went wrong, %s', str(e))
        logging.debug(traceback.print_exc())
    finally:
        clean_temp_dir(working_dir)


if __name__ == '__main__':
    logging.basicConfig(
        level=LOG_LEVEL,
        format='[%(asctime)s] [%(levelname)s] - %(message)s',
        datefmt='%H:%M:%S')
    main()
