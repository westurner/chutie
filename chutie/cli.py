# -*- coding: utf-8 -*-

"""Console script for chutie."""
import collections
import json
import sys

from pathlib import Path

import click
from syncer import sync

from chutie import chutie


@click.group()
def main(args=None):
    """Console script for chutie."""
    click.echo("See the 'screenshots' command.")
    return 0


@click.command()
@click.option(
    "-u",
    "--url",
    "urls",
    help=(
        "URL to retrieve screenshots of."
        " This can be specified multiple times."
    ),
    multiple=True,
)
@click.option(
    "-r",
    "--viewports",
    help=(
        'Viewport config string (e.g. "1024x768 mobile landscape devname7").'
        " This can be specified multiple times"
    ),
    multiple=True,
)
@click.option(
    "-o",
    "--dest-path",
    default=".",
    help=(
        "Directory to write images and JSON metadata into"
        " Default: '.'"
    ),
)
@click.option(
    "--dest-html",
    default="chutie.html",
    help=(
        "Name of the HTML file to write chutie templated output to."
        " Default: chutie.html"
    ),
)
@click.option(
    '-c',
    '--config',
    'configs',
    help=(
        "Path to a .json or .yaml config file."
        " If not specified, urls and viewports must be specified."
        " This can be specified multiple times."
    ),
    multiple=True
)
def screenshots(urls, viewports, dest_path, dest_html, configs):
    """Take screenshots of the URLs with the given resolution strings,
    save them to dest-path,
    and write a chutie.json and a chutie.html
    """
    if not ((bool(urls) and bool(viewports)) or bool(configs)):
        raise click.UsageError(
            "You must specify urls, viewports, or a config file."
            " See: --help")

    _urls = []
    _viewports = []

    if bool(configs):
        for config in configs:
            if config.endswith('.json'):
                with open(config) as _file:
                    cfg = json.load(_file)
            elif config.endswith('.yaml') or config.endswith('.yml'):
                import yaml
                with open(config) as _file:
                    cfg = yaml.safe_load(_file)
            else:
                raise click.BadParameter(
                    "The config file must end in one of "
                    ".json, .yaml, or .yml")

            _urls.extend(cfg.get('urls', []))
            _viewports.extend(cfg.get('viewports', []))
            dest_path = cfg.get('dest_path', dest_path)
            dest_html = cfg.get('dest_html', dest_html)

    _urls.extend(urls)
    _viewports.extend(viewports)

    cfg = dict(urls=_urls, viewports=_viewports, dest_path=dest_path, dest_html=dest_html)
    click.echo(cfg)

    output = sync(chutie.get_screenshots(_urls, _viewports, dest_path))

    jsonpath = Path(dest_path) / "chutie.json"
    with open(jsonpath, "w") as _file:
        json.dump(output, _file, indent=2)

    chutie.generate_html(output, write_to_path=dest_html)


@click.command()
@click.option(
    "--jsonpath",
    default="chutie.json",
    help="Path to a chutie.json file to template"
)
@click.option(
    "--template",
    default="screenshots.j2",
    help="Name of a jinja2 template in ./chutie/ TODO",
)
@click.option(
    "--dest-html",
    default="chutie.html",
    help=(
        "Name of the HTML file to write chutie templated output to."
        " Default: chutie.html"
    ),
)
def template(jsonpath, template, dest_html):
    with open(jsonpath) as _file:
        ctxt = json.load(_file, object_pairs_hook=collections.OrderedDict) # collections.OrderedDict)
    chutie.generate_html(ctxt, write_to_path=dest_html)

main.add_command(screenshots)
main.add_command(template)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
