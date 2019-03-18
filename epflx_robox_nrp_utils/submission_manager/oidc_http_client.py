""" Class which uses the BBP oidc client to do http calls """

from hbp_nrp_virtual_coach.http_client import HTTPClient
import json


class OIDCHTTPClient(HTTPClient):
    """ Class which uses the BBP oidc client to do http calls """

    def __init__(self, oidc_username):
        """
        :param oidc_username: The HBP oidc username
        """
        from bbp_client.oidc.client import BBPOIDCClient
        self.__oidc_client = BBPOIDCClient.implicit_auth(oidc_username)
        self.__headers = None

    def get(self, url):
        """
        :param url: The url to do a request on
        :return: the status of the get request and the content
        :rtype: integer, string
        """
        response, content = self.__oidc_client.request(url, headers=self.__headers)
        return int(response['status']), content

    def post(self, url, body):
        """
        :param url: The url to do a post to
        :param body: The content to post to the url
        :return: the status of the post request and the content
        :rtype: integer, string
        """

        if (type(body) == dict):
            response, content = self.__oidc_client.request(
                url, method='POST', body=json.dumps(body), headers=self.__headers
            )
        else:
            response, content = self.__oidc_client.request(
                url, method='POST', body=body, headers=self.__headers
            )
        return int(response['status']), content

    def put(self, url, body):
        """
        :param url: The url to do a request to
        :param body: The content to put to
        :return: the status of the put request and the content
        :rtype: integer, string
        """
        if (type(body) == dict):
            response, content = self.__oidc_client.request(
                url, method='PUT', body=json.dumps(body), headers=self.__headers
            )
        else:
            response, content = self.__oidc_client.request(
                url, method='PUT', body=body, headers=self.__headers
            )
        return int(response['status']), content

    def delete(self, url, body):
        """
        :param url: The url to do a request on
        :param body: The content to delete
        :return: the status of the delete request
        :rtype: integer
        """
        response, _ = self.__oidc_client.request(
            url, method='DELETE', body=json.dumps(body), headers=self.__headers
        )
        return int(response['status'])

    def set_headers(self, headers):
        """
        :param headers: The content of the headers
                        Can only be set after authentication
        """
        self.__headers = headers

    def get_auth_header(self):
        """
        :return: the authorization header
        """
        return self.__oidc_client.get_auth_header()
