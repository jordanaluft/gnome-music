from gi.repository import Gtk, Gio, GObject


class PlaybackPopover:

    def __init__(self, player):
        self._ui = Gtk.Builder()
        self._ui.add_from_resource(
            '/org/gnome/Music/playbackPopover.ui')

        self.player = player

        self.popover = self._ui.get_object('playbackPopover')
        self.popover.set_relative_to(self.player.nowplaying_button)

        self.label = Gtk.Label()
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.popover.add(self.box)

        self.player.connect('playlist-item-changed', self.update_popover)

        self.model = Gio.ListStore()
        self.track_list = Gtk.ListBox()
        self.track_list.bind_model(self.model, self.populate_model)
        self.box.pack_end(self.track_list, False, True, 0)

    def toggle_popover(self):
        if self.popover.get_visible():
            self.popover.hide()
        else:
            self.popover.show_all()

    def update_popover(self, player, playlist, current_track):
        self.model.remove_all()
        self.label.set_label(self.player.playlistType)
        self.box.pack_start(self.label, False, True, 0)
        for music in self.player.playlist:
            song = Song(music, self.player.playlistType)
            self.model.append(song)
        self.track_list.show_all()

    def populate_model(self, song):
        row = Gtk.ListBoxRow()
        box = Gtk.Box()
        row.add(box)
        track_name = Gtk.Label()
        time = Gtk.Label()
        artist = Gtk.Label()
        album = Gtk.Label()

        track_name.set_markup(song.track_name)
        time.set_markup(song.time)
        artist.set_markup(song.artist)
        album.set_markup(song.album)

        box.add(track_name)
        box.add(artist)
        box.add(album)
        box.add(time)
        box.add(song.cover)

        return row


class Song(GObject.Object):

    def __init__(self, music, playlist_type):
        super().__init__()

        self.music = tuple(music)

        self.artist = "Artist"
        self.album = "Album"
        self.cover = Gtk.Image()
        self.time = "Time"
        self.track_name = "Track Name"

        if playlist_type == 'Album':
            self.track_name = self.music[0]
            self.time = self.music[1]

        elif playlist_type == 'Songs':
            self.track_name = self.music[2]
            self.artist = self.music[3]

        elif playlist_type == 'Artist':
            self.track_name = self.music[0]
            self.artist = self.music[1]
            self.cover = self.music[2]
