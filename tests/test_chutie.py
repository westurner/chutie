#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `chutie` package."""


import unittest
from pathlib import Path

from click.testing import CliRunner
from syncer import sync

from chutie import chutie
from chutie import cli


class TestChutie(unittest.TestCase):
    """Tests for `chutie` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_010_viewportstr_to_dict(self):
        i, o = (
            "1024x768",
            dict(
                width=1024,
                height=768,
                isMobile=False,
                isLandscape=False,
                pathstr="1024x768",
            ),
        )
        self.assertEqual(chutie.viewportstr_to_dict(i), o)
        i, o = (
            "1024x768 mobile",
            dict(
                width=1024,
                height=768,
                isMobile=True,
                isLandscape=False,
                pathstr="1024x768-mobile",
            ),
        )
        self.assertEqual(chutie.viewportstr_to_dict(i), o)
        i, o = (
            "1024x768 mobile landscape",
            dict(
                width=1024,
                height=768,
                isMobile=True,
                isLandscape=True,
                pathstr="1024x768-mobile-landscape",
            ),
        )
        self.assertEqual(chutie.viewportstr_to_dict(i), o)
        i, o = (
            "1024x768 mobile landscape devicename",
            dict(
                width=1024,
                height=768,
                isMobile=True,
                isLandscape=True,
                pathstr="1024x768-mobile-landscape-devicename",
            ),
        )
        self.assertEqual(chutie.viewportstr_to_dict(i), o)

    def test_100_get_screenshots(self):

        urls = ["about:blank"]
        viewports = [
            "1024x768",
            "800x600",
            "1024x768 mobile landscape devname",
        ]

        context = sync(chutie.get_screenshots(urls, viewports))
        assert context
        for key in ["date", "urls", "viewports", "pages"]:
            self.assertIn(key, context)
        self.assertIn("about:blank", context["urls"])
        self.assertIn("about:blank", context["pages"])
        for url, pages in context["pages"].items():
            for page in pages:
                # from pprint import pformat
                # print(("page",))
                # print(pformat(page))
                imgpath = Path(page["path"])
                self.assertTrue(imgpath.exists())
                imgpath.unlink()
                self.assertFalse(imgpath.exists())

    def test_render_template(self):
        template_name = Path(__file__).parent.parent / 'chutie' / 'screenshots.j2'
        context = dict(pages={}, viewports={})
        output = chutie.render_template(context, template_name=template_name)
        self.assertIn('<html', output)
        self.assertIn('<span>Made with', output)

    def test_cli_help(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        #assert "chutie.cli.main" in result.output
        assert "screenshots" in result.output
        help_result = runner.invoke(cli.main, ["--help"])
        assert help_result.exit_code == 0
        assert "--help  Show this message and exit." in help_result.output

        result = runner.invoke(cli.main, ["screenshots", "--help"])
        self.assertEqual(result.exit_code, 0)
        assert "Take screenshots of the URLs" in result.output

        result = runner.invoke(cli.main, ["template", "--help"])
        self.assertEqual(result.exit_code, 0)
        assert "from a chutie.json and a jinja2 template" in result.output

    def test_cli_nothing_specified(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, [])
        self.assertEqual(result.exit_code, 2)
        assert "You must specify" in result.output

        result = runner.invoke(cli.main, ["screenshots"])
        self.assertEqual(result.exit_code, 2)
        assert "You must specify" in result.output

        result = runner.invoke(cli.main, ["template"])
        self.assertEqual(result.exit_code, 2)
        assert "You must specify" in result.output

    def test_cli_screenshots(self):
        runner = CliRunner()
        result = runner.invoke(
            cli.main,
            ["screenshots", "-u", "about:blank",
             "-r", "1024x768 mobile landscape devname"])
        self.assertEqual(result.exit_code, 0)
        assert "Successfully rendered to" in result.output

    def test_cli_config_file(self):
        runner = CliRunner()
        basepath = Path(__file__).parent
        cfg_viewports_json = basepath / 'example_viewports.json'
        cfg_viewports_yaml = basepath / 'example_viewports.yaml'
        cfg_url_json = basepath / 'example_url.json'
        cfg_url_yaml = basepath / 'example_url.yaml'

        result = runner.invoke(
            cli.main, ["screenshots",
             "-c", cfg_viewports_json,
             "-c", cfg_url_json,
             "-r", "1x1 mobile landscape devname"])
        self.assertEqual(result.exit_code, 0)
        # TODO: test that all URLs and resolutions are identified
        assert "Successfully rendered to" in result.output

        result = runner.invoke(
            cli.main, ["screenshots",
             "-c", cfg_url_yaml,
             "-c", cfg_viewports_yaml,
             "-r", "1x1 mobile landscape devname"])
        self.assertEqual(result.exit_code, 0)
        # TODO: test that all URLs and resolutions are identified
        assert "Successfully rendered to" in result.output
