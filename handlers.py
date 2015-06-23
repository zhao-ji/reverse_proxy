#!/usr/bin/env python
# utf8

import re

from flask import Flask
from flask import request

import logbook
from requests import get

app = Flask(__name__)

TED_PREFIX = "https://embed-ssl.ted.com"
YOUTUBE_PREFIX = "https://www.youtube.com"


@app.route("/ted/<path:ted_path>", methods=["GET"])
def ted(ted_path):
    headers = {}
    headers["Accept-Encoding"] = ""
    headers["User-Agent"] = request.headers.get("User-Agent")
    headers["X-Real-IP"] = request.remote_addr
    headers["X-Forwarded-For"] = request.remote_addr
    headers["X-Forwarded-Proto"] = "https"
    logbook.info(request.access_route[-1])
    logbook.info(request.remote_addr)
    logbook.info(request.headers.get("User-Agent"))

    ted_ret = get(
        "{}/{}".format(TED_PREFIX, ted_path),
        headers=headers,
    )
    logbook.info(ted_ret.status_code)
    logbook.info("{}/{}".format(TED_PREFIX, ted_path))
    assert ted_ret.ok

    ted_content = ted_ret.content
    return ted_content.replace(
        "ajax.googleapis.com", "cdnjs.cloudflare.com",
    ).replace(
        r'"/images', r'"{}/images'.format(TED_PREFIX),
    ).replace(
        r'"/css/i/ted-logo.png',
        r'"{}/css/i/ted-logo.png'.format(TED_PREFIX),
    ).replace(
        r'"/js/ZeroClipboard.min.js',
        r'"{}/js/ZeroClipboard.min.js'.format(TED_PREFIX),
    )


@app.route("/youtube/<path:proxy_path>", methods=["GET"])
def youtube(proxy_path):
    headers = {}
    headers["Accept-Encoding"] = ""
    headers["User-Agent"] = request.headers.get("User-Agent")
    headers["X-Real-IP"] = request.remote_addr
    headers["X-Forwarded-For"] = request.remote_addr
    headers["X-Forwarded-Proto"] = "https"

    ret = get(
        "{}/{}".format(YOUTUBE_PREFIX, proxy_path),
        headers=headers,
    )
    logbook.info(ret.status_code)
    logbook.info("{}/{}".format(YOUTUBE_PREFIX, proxy_path))
    assert ret.ok

    ret_back = re.sub(
        r"//s.ytimg.com/.*/html5player.js",
        "/static/js/html5player.js",
        ret.content,
    )
    ret_back = re.sub(
        r"//s.ytimg.com/.*/www-embed-player.js",
        "/static/js/www-embed-player.js",
        ret_back,
    )
    ret_back = re.sub(
        r"//www.google.com/js/bg/.*.js",
        "/static/js/bg.js",
        ret_back,
    )
    ret_back = re.sub(
        r"//s.ytimg.com/.*/www-embed-player.*.css",
        "/static/css/www-embed-player.css",
        ret_back,
    )
    ret_back = re.sub(
        r'<style name="www-roboto">.*</style>',
        '',
        ret_back,
    )

    return ret_back


if __name__ == "__main__":
    from os.path import abspath, exists, dirname, join

    server_log_file = join(dirname(abspath(__file__)), "logs", "runtime.log")
    if not exists(server_log_file):
        open(server_log_file, "w").close()

    local_log = logbook.FileHandler(server_log_file)
    local_log.format_string = (
        u'[{record.time:%H:%M:%S}] '
        u'lineno:{record.lineno} '
        u'{record.level_name}:{record.message}')
    local_log.push_application()

    app.run(host="127.0.0.1", port=6666, debug=True)
