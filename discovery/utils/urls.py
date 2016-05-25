# Third-party app imports
from urlparse import urlparse


def url_validate(url):
    url = urlparse(url)
    return (
        url.scheme + "://" + url.netloc +
        url.path, url.scheme + "://" + url.netloc
    )
