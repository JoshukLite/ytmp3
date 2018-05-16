import constants
import os
import youtube_dl

from base import BaseMedia


class YtdlMedia(BaseMedia):

    """ class to represent youtube-dl media file """

    _opts = {'quiet': True, 'prefer_insecure': True, 'no_warnings': True}

    def __init__(self, url, location=None, **kwargs):
        global_opts = dict(constants.YTDL_OPTS)
        global_opts.update(self._opts)
        self._opts = global_opts
        # set options to youtube-dl
        for key, value in kwargs.items():
            self._opts.update({key: value})
        if location:
            self._opts.update({'outtmpl': os.path.join(location, constants.VIDEO_TEMP_DIR, constants.YTDL_OUTP_FRMT)})
        # set download path with filename template youtube-dl option
        self._ytdl = youtube_dl.YoutubeDL(self._opts)

        self._info = self.ytdl.extract_info(url, download=False, process=False)

        super(YtdlMedia, self).__init__(url, location)

    def fetch_info(self):
        self._title = self.info['title']

    def download_video(self):
        self.ytdl.params.update({'format': 'best', 'quiet': False})
        self.ytdl.process_ie_result(self.info, download=True, extra_info={})

    def download_audio(self):
        self.ytdl.params.update({'format': 'bestaudio', 'quiet': False})
        res = self.ytdl.process_ie_result(self.info, download=True, extra_info={})
        return self.ytdl.prepare_filename(res)

    @property
    def info(self):
        return self._info

    @property
    def ytdl(self):
        return self._ytdl