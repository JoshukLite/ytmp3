import logging
import os
import youtube_dl

import core.constants as constants
import core.util as util

from base import BaseMedia


class YtdlMedia(BaseMedia):

    """ class to represent youtube-dl media file """

    def __init__(self, url, location=None, **kwargs):
        self._opts = dict(constants.YTDL_OPTS)

        # set options to youtube-dl
        for key, value in kwargs.items():
            self.opts.update({key: value})
        if location:
            # set download path with filename template youtube-dl option
            self.opts.update({'outtmpl': os.path.join(location, constants.VIDEO_TEMP_DIR, constants.YTDL_OUTP_FRMT)})

        super(YtdlMedia, self).__init__(url, location)

    def download_video(self):
        ytdl = youtube_dl.YoutubeDL(self.opts)
        ytdl.params.update({'format': 'best', 'quiet': False})
        ytdl.extract_info(self.url, download=True, process=False)

    def download_audio(self, post_format=None, output_dir=None):
        c_opts = dict(self.opts)
        # local options for audio only
        c_opts.update({
            'format': 'bestaudio',
            'quiet': False
        })

        # add postprocessor to convert result if format was set
        if post_format:
            if post_format in constants.AUDIO_FORMATS:
                postprocessors = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': post_format,
                    'preferredquality': '5',
                    'nopostoverwrites': False,
                }]
                c_opts.update({'postprocessors': postprocessors})
            else:
                raise ValueError('youtube-dl unsupported converting audio format - {0}'.format(post_format))

        ytdl = youtube_dl.YoutubeDL(c_opts)
        ytdl_res = ytdl.extract_info(self.url, download=True, process=True)

        audio_filename_full = ytdl.prepare_filename(ytdl_res)

        if post_format:
            nf_format = post_format
            audio_filename, audio_extension = util.get_filename_with_extension(audio_filename_full)
            audio_filename_full = audio_filename + '.' + nf_format
        else:
            # ext
            nf_format = ytdl_res.get('ext')

        audio_base_filename = os.path.basename(audio_filename_full)

        res = {
            'audio_ext': nf_format,
            'audio_filename': audio_base_filename,
            'id': ytdl_res.get('display_id'),
            'title': ytdl_res.get('title')
        }

        logging.info(u'Audio done: {0}'.format(ytdl_res.get('title')))

        return res

    @property
    def opts(self):
        return self._opts
