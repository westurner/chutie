# -*- coding: utf-8 -*-

"""Main module."""

import datetime
import logging
import os
from pathlib import Path

from pyppeteer import launch

from chutie import monkeypatches


async def _get_browser():
    return launch(headless=False)


def url_to_filename(url):
    """
    Args:
        url (str): a url to convert to a filename
    Returns:
        str: a filesystem-safe filename (with slashes replaced)
    """
    path = url.replace(os.path.sep, "_-_")
    return path


def viewportstr_to_dict(viewportstr):
    """
    Args:
        viewportstr (str): viewport string (e.g. ``1024x768 mobile landscape``)
    Returns:
        dict: dict suitable for use with pyppeteer page.emulate options=
    """
    _viewportstr = viewportstr.lower()
    terms = _viewportstr.split(" ")
    width, height = map(int, terms[0].split("x", 1))
    isMobile = True if "mobile" in terms else False
    isLandscape = True if "landscape" in terms else False
    return dict(
        width=width,
        height=height,
        isMobile=isMobile,
        isLandscape=isLandscape,
        pathstr=_viewportstr.replace(" ", "-"),
    )


async def get_screenshots(urls, viewports, dest_path="."):
    """
    Args:
        urls (list[str]): list of urls to retrieve and take screenshots of
        viewports (list[str]): list of width x height viewports to take screenshots in
    Kwargs:
        dest_path (str): path to store screenshots and metadata in (default: '.')
    Returns:
        dict: result object TODO
    """
    logging.basicConfig()  # TODO
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    browser = await launch()  # _get_browser()

    _viewports = {}
    for viewport in viewports:
        resdict = viewportstr_to_dict(viewport)
        _viewports[resdict["pathstr"]] = resdict

    metadata = {
        "date": datetime.datetime.now().isoformat(),
        "urls": urls,
        "viewports": _viewports,
        "pages": {},
    }
    pages = metadata["pages"]
    log.debug(metadata)

    dest = Path(dest_path)  # .resolve()
    if not dest.exists():
        dest.mkdir(parents=True)
    for url in urls:
        path_filename_prefix = url_to_filename(url)
        for respathstr, resdict in _viewports.items():
            page_options = resdict
            page = await browser.newPage()
            await page.setViewport(
                viewport=page_options
            )  # TODO: is newPage necessary for each viewport?
            await page.goto(url)
            for fullPage in (False, True):
                fullpagestr = "__full" if fullPage else ""
                path_filename = (
                    f"{path_filename_prefix}__{respathstr}{fullpagestr}.png"
                )
                data = {
                    "url": url,
                    "date": datetime.datetime.now().isoformat(),
                    "filename": path_filename,
                }
                screenshot_options = {
                    "path": str(dest / path_filename),
                    "fullPage": fullPage,
                }
                await page.screenshot(screenshot_options)
                data.update(screenshot_options)
                data.update(page_options)
                page_data = dict(
                    url=page.url,
                    title=await page.title(),
                    viewport=page.viewport,
                )
                data["page"] = page_data
                pages.setdefault(url, []).append(data)
                log.debug((url, data))
                print((url, data))
    return metadata


def generate_html(
    context,
    template_dir=None,
    template_name="screenshots.j2",
    write_to_path=None,
):
    import jinja2

    if template_dir is None:
        template_dir = Path(__file__).parent
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader([str(template_dir)]), autoescape=True
    )
    tmpl = env.get_template(template_name)
    html = tmpl.render(context)
    if write_to_path:
        with open(write_to_path, "w") as _file:
            _file.write(html)
    return html
