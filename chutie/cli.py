# -*- coding: utf-8 -*-

"""Console script for chutie."""
import collections
import json
import os
import pprint
import shutil
import sys

from pathlib import Path

import click
from syncer import sync

from chutie import chutie


@click.group()
def main(args=None):
    """Console script for chutie."""
    # click.echo("See the 'screenshots' command.")
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
    'output',
    default="index.html",
    help=(
        "Name of the HTML file to write chutie templated output to."
        " Default: index.html"
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
@click.option(
    "-t",
    "--template",
    "template_name",
    default=None, # == "chutie/screenshots.j2",
    help=(
        "Path to a jinja2 template."
        " Default: chutie/screenshots.j2"
    ),
)
def screenshots(urls, viewports, dest_path, output, configs, template_name):
    """Take screenshots of the URLs with the given resolution strings,
    save them to dest-path,
    and write a chutie.json and a index.html
    """
    if not ((bool(urls) and bool(viewports)) or bool(configs)):
        raise click.UsageError(
            "You must specify urls, viewports, or a config file."
            " See: --help")

    _urls = []
    _viewports = []

    _dest_path = Path(dest_path)
    _dest_path.mkdir(parents=True, exist_ok=True)

    if bool(configs):
        for config in configs:
            _configpath = Path(config)
            if not _configpath.exists() and not _configpath.is_file():
                raise click.BadParameter(
                    "Config file not found: {_configpath}")
            # Copy the config into _dest_path
            shutil.copy2(
                str(_configpath),
                str(_dest_path / _configpath.name))
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
            output = cfg.get('output', output)

    _urls.extend(urls)
    _viewports.extend(viewports)

    cfg = dict(urls=_urls, viewports=_viewports, dest_path=dest_path, output=output)
    click.echo(cfg)

    context = sync(chutie.get_screenshots(_urls, _viewports, dest_path))

    jsonpath = _dest_path / "chutie.json"
    with open(jsonpath, "w") as _file:
        json.dump(context, _file, indent=2)

    if os.path.sep not in output:
        output_path = _dest_path / output
    else:
        output_path = output
    chutie.render_template(
        context,
        template_name=template_name,
        write_to_path=output_path)
    click.echo(f"Successfully rendered to {output_path}.")
    return 0


@click.command()
@click.option(
    "-f",
    "--jsonpath",
    default="chutie.json",
    help=(
        "Path to a chutie.json file to template"
        " Default: chutie.json"
    )
)
@click.option(
    "-t",
    "--template",
    "template_name",
    default=None, # == "chutie/screenshots.j2",
    help=(
        "Name of a jinja2 template in ./chutie/ (TODO FileSystemLoader)"
        " Default: chutie/screenshots.j2"
    ),
)
@click.option(
    "-o",
    "--output",
    default="index.html",
    help=(
        "Name of the file to write rendered template output to."
        " Default: index.html"
    ),
)
def template(jsonpath, template_name, output):
    """Generate an index.html from a chutie.json and a jinja2 template"""
    with open(jsonpath) as _file:
        ctxt = json.load(_file, object_pairs_hook=collections.OrderedDict)
    chutie.render_template(ctxt,
                           template_name=template_name, write_to_path=output)
    click.echo(pprint.pformat(locals()))
    return 0

main.add_command(screenshots)
main.add_command(template)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
