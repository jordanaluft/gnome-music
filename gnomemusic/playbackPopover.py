from gi.repository import Gtk


class PlaybackPopover:

    def __init__(self, player):
        self._ui = Gtk.Builder()
        self._ui.add_from_resource(
            '/org/gnome/Music/playbackPopover.ui')

        self.player = player

        self.popover = self._ui.get_object('playbackPopover')
        self.popover.set_relative_to(self.player.nowplaying_button)

    def toggle_popover(self):
        if self.popover.get_visible():
            self.popover.hide()
        else:
            self.popover.show()


class Song:
    pass
