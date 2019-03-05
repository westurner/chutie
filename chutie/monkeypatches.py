#!/usr/bin/env python
"""
https://github.com/miyakogi/pyppeteer/issues/175#issuecomment-448886063
https://github.com/miyakogi/pyppeteer/pull/160#issuecomment-446183722
https://bugs.chromium.org/p/chromium/issues/detail?id=865002
- set ping_interval to None (!)
- set ping_timeout to None(!)
"""
def patch_pyppeteer():
    import pyppeteer.connection
    original_method = pyppeteer.connection.websockets.client.connect

    def new_method(*args, **kwargs):
        kwargs['ping_interval'] = None
        kwargs['ping_timeout'] = None
        return original_method(*args, **kwargs)

    pyppeteer.connection.websockets.client.connect = new_method
patch_pyppeteer()
