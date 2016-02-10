class PlaybackPopover:

    def __init__(self):
        self._ui = Gtk.Builder()
        self._ui.add_from_resource('/org/gnome/Music/playbackPopover.ui')


class Song:
    pass
