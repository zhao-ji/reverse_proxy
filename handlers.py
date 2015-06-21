#!/usr/bin/env python
# utf8

from flask import Flask
from flask import request

import logbook
from requests import get

app = Flask(__name__)

TED_PREFIX = "https://embed-ssl.ted.com"


@app.route("/ted/<path:ted_path>", methods=["GET"])
def ted(ted_path):
    headers = {}
    headers["Accept-Encoding"] = ""
    headers["User-Agent"] = request.headers.get("User-Agent")
    headers["X-Real-IP"] = request.remote_addr
    headers["X-Forwarded-For"] = request.remote_addr
    headers["X-Forwarded-Proto"] = "https"
    local_log.info(request.remote_addr)
    local_log.info(request.headers.get("User-Agent"))

    ted_ret = get(
        "{}/{}".format(TED_PREFIX, ted_path),
        headers=headers,
    )
    assert ted_ret.ok

    ted_content = ted_ret.content
    ted_content.replace(
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

    return ted_content

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

    app.run(port=6666)
