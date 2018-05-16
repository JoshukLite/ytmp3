import constants
import httplib
import logging
import os
import urllib
import urlparse


class BaseMedia(object):

    """ class to represent media file """

    def __init__(self, url, location):
        self._url = url
        self._location = location
        self._title = None
        self._video_id = None

        self.fetch_info()

    def fetch_info(self):
        raise NotImplementedError

    def download_video(self):
        raise NotImplementedError

    def download_audio(self):
        raise NotImplementedError

    def download_thumb(self):
        image_url = constants.HD_THUMB_URL_FRMT.format(self.video_id)

        new_image_name = '{}.{}'.format(self.video_id, 'jpg')

        done = False
        attempt = 0
        while not done:
            try:
                urllib.urlretrieve(image_url, os.path.join(self.location, constants.IMAGE_TEMP_DIR, new_image_name))
                done = True
            except httplib.BadStatusLine as bsl:
                attempt += 1
                if attempt > constants.MAX_ATTEMPT:
                    raise bsl
                logging.info("Error while downloading thumbnail, performing {0} attempt".format(attempt))

    def _prepare_video_id(self):
        parsed = urlparse.urlparse(self.url)
        query_params = urlparse.parse_qs(parsed.query)
        self._video_id = query_params['v'][0]

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
