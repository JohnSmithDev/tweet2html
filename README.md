tweet2html
==========

OVERVIEW
--------

A small Python library to take tweet text and convert it to
HTML, with marked up links etc.

FUNCTIONALITY
-------------

The following conversions take place:

1. @foo is converted to a hyperlink to that person's Twitter page
2. #foo is converted to a search link on Twitter for that hashtag
3. Anything beginning http:// or https:// is converted to a
   proper link.
4. URLs can optionally be tested, this is recommended to avoid
   any confusion if punctuation directly follows the URL e.g.
   "http://www.google.com," will be converted to a link to
   "http://www.google.com" followed by a comma
5. Optionally URLs that are redirects can be converted to
   the destination link, e.g. for t.co or bit.ly URLs
6. Optionally you can define in a dictionary to map each type
   of link (@foo, #foo, regular link) to different CSS classes,
   which would be of use if you want to style them differently.
7. Optionally return a list of the URLs which link to images;
   useful if you want to display them alongside the tweet text.
   (NB: sites such as twitpic.com 

The library doesn't actually interface to the Twitter API, it's
up to your own code to pull down the tweet text.

USAGE
-----

Have a look at the unit tests in test_tweet2html.py, I've hopefully
got examples of every different type of usage.

Super simple form:

    import tweet2html
    html = tweet2html.format("@fred: Visit http://john-smith.me #blah")

A more involved example:

    import tweet2html
    html, images = tweet2html.format("@fred: Visit http://john-smith.me #blah",
                     check_links=True,
                     css_classes={ "url": "my-url-css-class",
                                   "person": "my-tweeter-class",
                                   "topic": "my-hashtag-css-class" },
                     return_images=True,
                     convert_redirects=True)

FURTHER NOTES
-------------

You should set check_links=True, unless you're processing in real-time
and/or you have time constraints such as App Engine's 30-second limit
for requests.  Currently it defaults to not checking by default, although
this may change - see point 6 in the next section.

BUGS/TODO (as of 2011/01/13)
----------------------------

1. The parsing is a bit simplistic, might be better done with
   regexes?
2. Unicode URLs should probably be converted to escaped
   characters
3. The Unicode URL unit test doesn't work (the actual code
   does produce the correct output, I just couldn't get the
   comparison to work - lame, lame, lame)
4. The Unicode stuff probably needs more test cases in
   any event
5. The code to handle redirects uses a global variable and
   so isn't thread safe.  I can think of a dumb solution
   using a dict to map the original URL to the redirect which
   would solve that, but I'd rather spend some time getting
   my head around how urllib2 works and do it properly.
   However, thread-safety isn't a concern in the context I'm
   using this, so don't expect a quick solution...
6. I might have a rethink on the boolean argument defaults,
   I suspect they not as logical as they might ideally be
7. I've not come across any definition of what the valid
   characters are for Twitter usernames or hashtags (haven't
   looked to be perfectly honest), so there could be some cases
   where the wrong thing happens - not noticed any as yet
   though.
8. I've not had need to use the 'return_images' functionality
   personally, so it might well be less reliable than the rest
   of the code

ALTERNATIVES
------------

I'm sure someone else must have written code to do this sort of
thing - it strikes me as a fairly common itch to be scratched.
However, my Google-fu failed to find anything suitable.

CREDITS
-------

Written by John Smith 2010/2011, apart from some urllib2-related
bits copied/adapted from posts on Stack Overflow - links to the
SO posts are in the code.

My blog (which uses this code): http://www.john-smith.me

My Twitter: JohnMMIX

LICENCE
-------

GPL v2 - http://www.gnu.org/licenses/gpl-2.0.html

