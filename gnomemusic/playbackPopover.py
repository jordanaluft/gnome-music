from gi.repository import Gtk


class PlaybackPopover:

    def __init__(self, player):
        self._ui = Gtk.Builder()
        self._ui.add_from_resource(
            '/org/gnome/Music/playbackPopover.ui')

        self.player = player

        self.popover = self._ui.get_object('playbackPopover')
        self.popover.set_relative_to(self.player.nowplaying_button)

        self.label = Gtk.Label()
        self.popover.add(self.label)

        self.player.connect('playlist-item-changed', self.update_popover)

    def toggle_popover(self):
        if self.popover.get_visible():
            self.popover.hide()
        else:
            self.popover.show_all()

    def update_popover(self, player, playlist, current_track):
        self.label.set_label(self.player.playlistType)


class Song:
    pass
