﻿# Copyright 2004-2016 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

init -1100 python in gui:
    from store import config, layout, _preferences, Frame, Null

    config.translate_clean_stores.append("gui")

    _null = Null()

    def init(width, height):
        """
        :doc: gui

        Initializes the gui.

        `width`
            The width of the default window.

        `height`
            The height of the default window.
        """

        config.screen_width = width
        config.screen_height = height

        layout.defaults()

        renpy.call_in_new_context("_style_reset")

        # Defer styles until after translation code runs.
        config.defer_styles = True

        size = (width, height)

        if (_preferences.virtual_size is not None) and (_preferences.virtual_size != size):
            _preferences.physical_size = None

        _preferences.virtual_size = size

        from store import build
        build.include_old_themes = False

    def button_properties(kind):
        """
        :doc: gui

        Given a `kind` of button, returns a dictionary giving standard style
        properties for that button. This sets:

        * The background.
        * Padding, to gui.kind_button_borders.padding (if it exists).
        * Xsize, to gui.kind_button_width (if it exists).
        * Ysize, to gui.kind_button_height (if it exists).

        The background is a frame that takes its background picture from
        the first existing one of:

        * gui/button/kind_[prefix_].background.png
        * gui/button/[prefix_].background.png

        If a borders variables named gui.kind_borders is supplied, it's
        used. Otherwise, button_borders is used.
        """

        g = globals()

        def get(prop):
            if kind + "_button_" + prop in g:
                return g[kind + "_button_" + prop]

            return None

        borders = get("borders")

        tile = get("tile")
        if tile is None:
            tile = button_tile

        rv = {
            "background" : Frame([
                "gui/button/" + kind + "_[prefix_]background.png",
                "gui/button/[prefix_]background.png",
            ], borders or button_borders, tile=tile),
        }

        if borders is not None:
            rv["padding"] = borders.padding

        width = get("width")
        height = get("height")

        if width is not None:
            rv["xsize"] = width

        if height is not None:
            rv["ysize"] = height

        return rv

    def button_text_properties(kind):
        """
        :doc: gui

        Given a `kind` of button, returns a dictionary giving standard style
        properties for that button. This currently sets:

        * Font, to gui.kind_button_font (if it exists).
        * Size, to gui.kind_button_text_size (if it exists).
        """

        g = globals()

        def get(prop):
            print kind + "_button_" + prop

            if kind + "_button_" + prop in g:
                return g[kind + "_button_" + prop]

            return None

        rv = { }

        font = get("font")
        text_size = get("text_size")
        xalign = get("text_xalign")

        if font is not None:
            rv["font"] = font

        if text_size is not None:
            rv["size"] = text_size

        if xalign is not None:
            rv["xalign"] = xalign
            rv["text_align"] = xalign

        return rv


    ############################################################################
    # Strings used by the confirm screen.

    ARE_YOU_SURE = layout.ARE_YOU_SURE
    DELETE_SAVE = layout.DELETE_SAVE
    OVERWRITE_SAVE = layout.OVERWRITE_SAVE
    LOADING = layout.LOADING
    QUIT = layout.QUIT
    MAIN_MENU = layout.MAIN_MENU
    END_REPLAY = layout.END_REPLAY
    SLOW_SKIP = layout.SLOW_SKIP
    FAST_SKIP_UNSEEN = layout.FAST_SKIP_UNSEEN
    FAST_SKIP_SEEN = layout.FAST_SKIP_SEEN

    ############################################################################
    # Image generation. This lives here since it wants to read data from
    # the gui variables.

    # Should we skip backups?
    _skip_backup = False

    def _gui_images():

        import store.gui as gui
        from store import config, Color

        import pygame_sdl2
        import os

        if not config.developer:
            return

        class Image(object):

            def __init__(self, dn, fn, width, height):
                self.s = pygame_sdl2.Surface((width, height), pygame_sdl2.SRCALPHA)
                self.fn = os.path.join(config.gamedir, "gui", dn, fn + ".png")
                self.width = width
                self.height = height

            def save(self):
                s = self.s
                fn = self.fn

                dn = os.path.dirname(fn)

                try:
                    os.makedirs(dn, 0o777)
                except:
                    pass

                if os.path.exists(fn):

                    index = 1

                    while True:
                        bfn = "{}.{}.bak".format(fn, index)

                        if not os.path.exists(bfn):
                            break

                        index += 1

                    if not gui._skip_backup:
                        os.rename(fn, bfn)

                pygame_sdl2.image.save(s, fn)

            def fill(self, color=None):
                if color is None:
                    color = gui.accent_color

                color = tuple(Color(color))

                self.s.fill(color)
                return self

            def fill_rect(self, rect, color=None):
                if color is None:
                    color = gui.accent_color

                color = tuple(Color(color))

                ss = self.s.subsurface(rect)
                ss.fill(color)

                return self

            def fill_left(self, width, color=None):
                self.fill_rect((0, 0, width, self.height))
                return self

        def scale(fixed, scaled):

            if fixed is not None:
                return fixed

            factor = config.screen_height / 720
            return int(scaled * factor)


        # Buttons
        width = scale(gui.button_width, 300)
        height = scale(gui.button_height, 36)

        check_width = gui.check_button_borders.padding[0]
        check_rect = (
            0,
            gui.check_button_borders.padding[1],
            min(check_width, scale(None, 5)),
            height - gui.check_button_borders.padding[1] - gui.check_button_borders.padding[3],
            )

        radio_width = gui.radio_button_borders.padding[0]
        radio_rect = (
            0,
            gui.radio_button_borders.padding[1],
            min(radio_width, scale(None, 5)),
            height - gui.radio_button_borders.padding[1] - gui.radio_button_borders.padding[3],
            )

        Image("button", "idle_background", width, height).save()
        Image("button", "hover_background", width, height).save()

        Image("button", "check_selected_foreground", check_width, height).fill_rect(check_rect).save()
        Image("button", "check_foreground", check_width, height).save()

        Image("button", "radio_selected_foreground", radio_width, height).fill_rect(radio_rect).save()
        Image("button", "radio_foreground", radio_width, height).save()


        # Bars.
        long_size = scale(None, 350)

        Image("bar", "left", long_size, gui.bar_size).fill(gui.hover_color).save()
        Image("bar", "right", long_size, gui.bar_size).fill(gui.muted_color).save()
        Image("bar", "bottom", gui.bar_size, long_size).fill(gui.hover_color).save()
        Image("bar", "top", gui.bar_size, long_size).fill(gui.muted_color).save()

        thumb_size = scale(None, 15)


        Image("slider", "horizontal_idle_bar", long_size, gui.slider_size).fill(gui.muted_color).save()
        Image("slider", "horizontal_idle_thumb", thumb_size, gui.slider_size).fill(gui.accent_color).save()
        Image("slider", "horizontal_hover_bar", long_size, gui.slider_size).fill(gui.hover_muted_color).save()
        Image("slider", "horizontal_hover_thumb", thumb_size, gui.slider_size).fill(gui.hover_color).save()

        Image("slider", "vertical_idle_bar", gui.slider_size, long_size).fill(gui.muted_color).save()
        Image("slider", "vertical_idle_thumb", gui.slider_size, thumb_size).fill(gui.accent_color).save()
        Image("slider", "vertical_hover_bar", gui.slider_size, long_size).fill(gui.hover_muted_color).save()
        Image("slider", "vertical_hover_thumb", gui.slider_size, thumb_size).fill(gui.hover_color).save()


        long_size = scale(None, 700)

        Image("scrollbar", "horizontal_idle_bar", long_size, gui.scrollbar_size).fill(gui.muted_color).save()
        Image("scrollbar", "horizontal_idle_thumb", long_size, gui.scrollbar_size).fill(gui.accent_color).save()
        Image("scrollbar", "horizontal_hover_bar", long_size, gui.scrollbar_size).fill(gui.hover_muted_color).save()
        Image("scrollbar", "horizontal_hover_thumb", long_size, gui.scrollbar_size).fill(gui.hover_color).save()

        Image("scrollbar", "vertical_idle_bar", gui.scrollbar_size, long_size).fill(gui.muted_color).save()
        Image("scrollbar", "vertical_idle_thumb", gui.scrollbar_size, long_size).fill(gui.accent_color).save()
        Image("scrollbar", "vertical_hover_bar", gui.scrollbar_size, long_size).fill(gui.hover_muted_color).save()
        Image("scrollbar", "vertical_hover_thumb", gui.scrollbar_size, long_size).fill(gui.hover_color).save()

        sbp = gui.slot_borders.padding
        tnx = (gui.slot_width - config.thumbnail_width) // 2
        bar_width = scale(None, 5)

        s = Image("button", "slot_idle_background", gui.slot_width, gui.slot_height)
        s.fill_rect((tnx, sbp[1], config.thumbnail_width, config.thumbnail_height), gui.muted_color)
        s.save()

        s = Image("button", "slot_hover_background", gui.slot_width, gui.slot_height)
        s.fill_rect((tnx, sbp[1], config.thumbnail_width, config.thumbnail_height), gui.hover_muted_color)
        s.fill_rect((0, sbp[1], bar_width, config.thumbnail_height))

        s.save()


        return False

    renpy.arguments.register_command("gui_images", _gui_images)








