import logging
import os
from http.client import BadStatusLine
from urllib.request import urlretrieve

from .. import constants
from .. import util


class BaseMedia(object):

    """ class to represent media file """

    def __init__(self, url, location):
        self._url = url
        self._location = location
        self._title = None
        self._video_id = None

    def download_video(self):
        raise NotImplementedError

    def download_audio(self):
        raise NotImplementedError

    def download_thumb(self):
        image_url = constants.HD_THUMB_URL_FRMT.format(self.video_id)
        thumb_ext = 'jpg'

        new_image_name = '{}.{}'.format(self.video_id, thumb_ext)

        done = False
        attempt = 0
        while not done:
            try:
                urlretrieve(image_url, os.path.join(self.location, constants.IMAGE_TEMP_DIR, new_image_name))
                done = True
            except BadStatusLine as bsl:
                attempt += 1
                if attempt > constants.MAX_ATTEMPT:
                    raise bsl
                logging.info("Error while downloading thumbnail, performing {0} attempt".format(attempt))

        res = {
            'thumb_ext': thumb_ext,
            'thumb_filename': new_image_name
        }

        return res

    def _prepare_video_id(self):
        params = util.get_url_params(self.url)
        self._video_id = params['v']

    @property
    def location(self):
        return self._location

    @property
    def title(self):
        return self._title

    @property
    def video_id(self):
        if not self._video_id:
            self._prepare_video_id()

        return self._video_id

    @property
    def url(self):
        return self._url
