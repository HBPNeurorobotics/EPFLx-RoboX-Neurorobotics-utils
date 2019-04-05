"""
Base HTTP Client class used so that no matter what http client is used
the interface to do the request will always be the same
"""


class HTTPClient(object):
    """ Base HTTP Client class """

    def get(self, url):
        """
        Get method placeholder
        :param url: The url to do a request on
        """
        raise NotImplementedError()

    def post(self, url, body):
        """
        Post method placeholder
        :param url: The url to do a post to
        :param body: The content to post to the url
        """
        raise NotImplementedError()

    def put(self, url, body):
        """
        Put method placeholder
        :param url: The url to do a request to
        :param body: The content to put to
        """
        raise NotImplementedError()

    def delete(self, url, body):
        """
        Delete method placeholder
        :param url: The url to do a request on
        :param body: The content to delete
        """
        raise NotImplementedError()
