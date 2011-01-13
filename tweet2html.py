#!/usr/bin/env python
"""
Convert Tweet text (as received via an API call) into HTML.

I would have thought this had already been done,
but the closest I could find on Google was this post on SO:
http://stackoverflow.com/questions/720113/find-hyperlinks-in-text-using-python-twitter-related

Written by John Smith           | http://www.john-smith.me
Copyright Menboku Ltd 2010,2011 | http://www.menboku.co.uk
Licenced under GPLv2            | http://www.gnu.org/licenses/gpl-2.0.html
  * Except for chunks posted to StackOverflow, which are (presumably)
    copyright their original authors and licenced under ??? - SO links
    are indicated in comments at the appropriate sections

"""

__author__ = "John Smith - http://www.john-smith.me"

import re
import urllib2
import logging

def is_space(ch):
    return re.match("\s", ch)

def is_nonalphanumeric(ch):
    return re.match("\W", ch)

def invalid_username_char(ch):
    return not re.match("[\w@]", ch)

def find_to_end(text, terminator_func=is_space):
    idx = 0
    retval = ""
    while idx<len(text) and not terminator_func(text[idx]):
        retval += text[idx]
        idx += 1
    return retval

### START OF CODE TAKEN FROM STACK OVERFLOW

# http://stackoverflow.com/questions/107405/how-do-you-send-a-head-http-request-in-python
class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

redirect_location = None
# http://stackoverflow.com/questions/554446/how-do-i-prevent-pythons-urllib2-from-following-a-redirect
class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        global redirect_location # yuk
        if "Location" in headers:
            redirect_location = headers["Location"]
        return urllib2.HTTPRedirectHandler.http_error_302(self, req, 
                                                          fp, code, msg,
                                                          headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_302

### END OF CODE TAKEN FROM STACK OVERFLOW


def check_url(url, timeout = 5):
    """
    Return a tuple for the URL
    The tuple contains (str, str) or (None, None) if unable to HEAD
    First string is the Content_Type, or a guess of "text/html"
      if Content-Type isn't in the headers
    Second string is any Location supplied (e.g. if it's a 301
      or 302 redirect), otherwise it's an echo of the supplied
      URL

    """
    global redirect_location # yuk
    redirect_location = None

    try:
        opener = urllib2.build_opener(MyHTTPRedirectHandler)
        urllib2.install_opener(opener)
        response = urllib2.urlopen(HeadRequest(url), timeout=timeout)

        logging.debug("URL '%s' checked OK" % (url))
        if "Content-Type" in response.headers:
            ct = response.headers["Content-Type"]
        else:
            ct = "text/html"
        if redirect_location:
            loc = redirect_location
        else:
            loc = url

        return ct, loc

    except urllib2.HTTPError, e:
        logging.warning("URL check of '%s' failed [%s/%s]" % 
                        (url, type(e), e.code))
        return None, None
    except urllib2.URLError, e:
        logging.warning("URL check of '%s' failed [%s/%s]" % 
                        (url, type(e), e.reason))
        return None, None
    except Exception, e:
        logging.warning("URL check of '%s' failed [%s/%s]" % 
                        (url, type(e), e))
        return None, None

def format_tweet(text, check_links=False, css_classes=None, 
                 return_images=False,
                 convert_redirects=True):
    
    """
    Return a string of rendered HTML

    Arguments:
    - check_links: Do HTTP HEAD requests to try to get correct
                   working URLs (e.g. to avoid problems if
                   punctuation directly follows the URL)
    - css_classes: Dictionary of CSS classes to inject into
                   the HTML where appropriate.  Keys should be:
                   "url":    for URLs (duh)
                   "person": for @joebloggs
                   "topic":  for #foobar
    - return_images: if True, return tuple of (str, list) instead,
                     the latter being any linked images.
                     NB#1: check_links must be True
                     NB#2: only works if the host allows direct access
                           to the image rather than a webpage
    - convert_redirects: if True and a link is a HTTP, output
                         the redirection address rather than the
                         original.  This only has an effect if
                         check_links=True

    """

    # I'm avoiding regexes for the moment, until I've got
    # a better idea of how to handle stuff like Unicode URLs,
    # avoiding confusion with # in URLs, etc
    # Possibly inefficient, but in the context I'm expecting
    # (140 char Tweets, only a few processed at a time), I'm
    # not concerned about optimizing
    output = ""
    idx = 0

    image_urls = []

    while idx < len(text):
        ch = text[idx]
        if ch.lower() == "h" and idx<len(text)-1:
            if text[idx:].lower().startswith("http://") or \
                    text[idx:].lower().startswith("https://"):
                url = find_to_end(text[idx:])
                if check_links: 
                    url_type, redirect = check_url(url)
                    alt_url = url
                    while not url_type and is_nonalphanumeric(alt_url[-1]):
                        alt_url = alt_url[:-1]
                        url_type, redirect = check_url(alt_url)
                        # Only replace if we get something that works
                        if url_type:
                            url = alt_url
                            break
                    if url_type and url_type.startswith("image"):
                        image_urls.append(url)
                if css_classes and "url" in css_classes:
                    css = " class='" + css_classes["url"] + "'"
                else:
                    css = ""
                if convert_redirects and redirect and url != redirect:
                    logging.debug("%s redirects to '%s'" % 
                                  (url, redirect))
                    url = redirect
                output += "<a href='" + url + "'" + css + ">" + url + "</a>"
                idx += len(url)
            else:
                output += ch
                idx += 1
        elif ch == "@":
            username = find_to_end(text[idx:], invalid_username_char)
            if len(username)>0:
                username = username[1:]
                if css_classes and "person" in css_classes:
                    css = " class='" + css_classes["person"] + "'"
                else:
                    css = ""
                output += "<a href='http://twitter.com/" + username \
                    + "'" + css + ">@" + username + "</a>"
                idx += len(username)+1
            else:
                output += ch
                idx += 1
        elif ch == "#" and idx < len(text)-1:
            topic = find_to_end(text[idx+1:], 
                                terminator_func=is_nonalphanumeric)
            if len(topic)>0:
                if css_classes and "topic" in css_classes:
                    css = " class='" + css_classes["topic"] + "'"
                else:
                    css = ""
                output += "<a href='http://twitter.com/search?q=%23" + topic \
                    + "'" + css + ">#" + topic + "</a>"
                idx += len(topic)+1
            else:
                output += ch
                idx += 1
        else:
            output += ch
            idx += 1
    if return_images:
        return output, image_urls
    else:
        return output


def simple_test_cases():
    css_classes = {
        "url": "my-url-css",
        "person": "my-person-css",
        "topic": "my-topic-css"
        }




    # Images
    print(format_tweet("Image in webpage: http://twitpic.com/3eg7er",
                       True, css_classes))
    print(format_tweet("Image directly accessible "
                       "http://js-test.appspot.com/html/images/smalldot.png",
                       True, css_classes))

    # Unicode
    unicode_tweet = u"Unicode URL http://ja.wikipedia.org/wiki/\u56fd boo"
    ft = format_tweet(unicode_tweet, True, css_classes)
    print(unicode(ft).encode("utf-8"))

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    simple_test_cases()
