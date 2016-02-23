
import os

from gi.repository import Gio, GLib, GObject, Grl, Gtk

from gnomemusic.albumArtCache import AlbumArtCache


BASE_UI_RESOURCE = '/org/gnome/Music/playback_popover/'

AlbumArtCache = AlbumArtCache.get_default()

COVER_SIZE = (30, 30)
BIG_COVER_SIZE = (175, 175)


class PlaybackPopover(object):

    def __init__(self, player):
        self.ui = Gtk.Builder()
        self.ui.add_from_resource(os.path.join(BASE_UI_RESOURCE, 'popover.ui'))

        self.player = player
        self.player.connect('playlist-item-changed', self.update_popover)

        self.headerbar = self.ui.get_object('headerbar')

        self.popover = Gtk.Popover()
        self.popover.set_relative_to(self.player.nowplaying_button)
        self.popover.get_style_context().add_class('popover')

        self.box = self.ui.get_object('box_main')
        self.popover.add(self.box)

        self.default_model = Gio.ListStore()
        self.album_model = Gio.ListStore()

        self.default_tracklist = self.ui.get_object('default_tracklist')
        self.default_tracklist.bind_model(
            self.default_model, self.populate_default_tracklist)

        self.album_tracklist = self.ui.get_object('album_tracklist')
        self.album_tracklist.bind_model(
            self.album_model, self.populate_album_tracklist)

        self.stack = self.ui.get_object('stack')

        self.create_playlist_box()

    def create_playlist_box(self):
        self.playlist_box = self.ui.get_object('playlist_box_main')

        self.playlist_previous = PlaylistRow('Previous')
        self.playlist_now = PlaylistRow('Now')
        self.playlist_next = PlaylistRow('Next')

        self.playlist_box.add(self.playlist_previous)
        self.playlist_box.add(self.playlist_now)
        self.playlist_box.add(self.playlist_next)

    def toggle_popover(self):
        if self.popover.get_visible():
            self.popover.hide()
        else:
            self.popover.show()

    def update_popover(self, player, playlist, current_track):
        self.playlist_type = player.playlistType
        self.playlist = playlist
        self.current_track = current_track

        self.headerbar.set_title(self.playlist_type)

        view_name = self.playlist_type
        if view_name == 'Album':
            self.update_album_view()
        elif view_name == 'Playlist':
            self.update_playlist_view()
        else:
            self.update_default_view()
            view_name = 'Default'

        self.stack.set_visible_child_name(view_name)

    def update_album_view(self):
        self.album_model.remove_all()
        for music in self.playlist:
            self.album_model.append(AlbumSong(music, self.player))

        self.set_album_cover()

        album_track_name = self.ui.get_object('album_track_name')
        album_artist = self.ui.get_object('album_artist')
        self.current_album_cover = self.ui.get_object('album_cover_image')

        album_track_name.set_markup(self.get_current_track_name())
        album_artist.set_markup(self.get_current_artist())

        self.album_tracklist.show_all()

    def set_album_cover(self):
        self.album_name, self.album_artist, self.album_media = self.player.currentAlbumData
        AlbumArtCache.lookup(
            self.album_media,
            BIG_COVER_SIZE[0],
            BIG_COVER_SIZE[1],
            self.get_album_cover_callback,
            None,
            self.album_artist,
            self.album_name,
        )

    def get_album_cover_callback(self, cover, path, data=None):
        if not cover:
            cover = self.get_default_cover()
        self.current_album_cover.set_from_pixbuf(cover)

    def get_default_cover(self):
        return AlbumArtCache.get_default_icon(BIG_COVER_SIZE[0], BIG_COVER_SIZE[1], False)

    def update_default_view(self):
        self.default_model.remove_all()

        for music in self.playlist:
            if self.playlist_type == 'Songs':
                song = Song(music)
            elif self.playlist_type == 'Artist':
                song = ArtistSong(music)

            if music.path >= self.player.currentTrack.get_path():
                self.default_model.append(song)

        self.default_tracklist.show_all()

    def update_playlist_view(self):
        self.populate_playlist_tracklist(self.playlist_previous, self.player._get_previous_track())
        self.populate_playlist_tracklist(self.playlist_now, self.player.currentTrack)
        self.populate_playlist_tracklist(self.playlist_next, self.player._get_next_track())

    def populate_playlist_tracklist(self, row, iter):
        if iter is not None:
            path = iter.get_path()
            track = self.player.playlist[path]
            song = PlaylistSong(track)

            row.track_name.set_markup(song.track_name)
            row.artist.set_markup(song.artist)
            row.set_album_cover(song.media)
            row.show_all()
        else:
            row.hide()

    def populate_album_tracklist(self, song):
        return AlbumRow(song, self.get_current_track_name())

    def populate_default_tracklist(self, song):
        return DefaultRow(song, self.get_current_track_name())

    def get_current_artist(self):
        return self.player._currentArtist

    def get_current_track_name(self):
        return self.player._currentTitle


class DefaultRow(Gtk.ListBoxRow):

    def __init__(self, song, current_track):
        super().__init__()
        self.ui = Gtk.Builder()
        self.ui.add_from_resource(
            os.path.join(BASE_UI_RESOURCE, 'row_default.ui'))

        self.song = song
        self.track_name = self.ui.get_object('track_name')
        self.artist = self.ui.get_object('artist')
        self.cover = self.ui.get_object('image')

        self.track_name.set_markup(song.track_name)
        self.artist.set_markup(song.artist)

        self.box = self.ui.get_object('box')
        self.add(self.box)

        self.set_album_cover()

        if song.track_name == current_track:
            self.playing = self.ui.get_object('playing')
            self.playing.set_from_icon_name("media-playback-start", 1)

    def set_album_cover(self):
        AlbumArtCache.lookup(
            self.song.media,
            COVER_SIZE[0],
            COVER_SIZE[1],
            self.get_album_cover_callback,
            None,
            self.song.media.get_artist(),
            self.song.media.get_album(),
            first=False,
        )

    def get_album_cover_callback(self, cover, path, data=None):
        if not cover:
            cover = self.get_default_cover()
        self.cover.set_from_pixbuf(cover)

    def get_default_cover(self):
        return AlbumArtCache.get_default_icon(COVER_SIZE[0], COVER_SIZE[1], False)


class AlbumRow(Gtk.ListBoxRow):

    def __init__(self, song, current_track):
        super().__init__()
        self.ui = Gtk.Builder()
        self.ui.add_from_resource(
            os.path.join(BASE_UI_RESOURCE, 'row_album.ui'))

        self.track_name = self.ui.get_object('track_name')
        self.time = self.ui.get_object('time')

        if song.played:
            self.track_name.set_markup('<span color=\'grey\'>%s</span>' % song.track_name)
            self.time.set_markup('<span color=\'grey\'>%s</span>' % song.time)
        else:
            self.track_name.set_markup(song.track_name)
            self.time.set_markup(song.time)

        self.box = self.ui.get_object('box')

        if song.track_name == current_track:
            self.playing = self.ui.get_object('playing')
            self.playing.set_from_icon_name("media-playback-start", 1)

        self.add(self.box)


class PlaylistRow(Gtk.Box):

    def __init__(self, state):
        super().__init__()
        self.ui = Gtk.Builder()
        self.ui.add_from_resource(
            os.path.join(BASE_UI_RESOURCE, 'row_playlist.ui'))

        self.state = self.ui.get_object('state')
        self.track_name = self.ui.get_object('track_name')
        self.artist = self.ui.get_object('artist')
        self.cover = self.ui.get_object('album_image')

        self.state.set_text(state)

        self.box = self.ui.get_object('box')
        self.add(self.box)

    def set_album_cover(self, media):
        AlbumArtCache.lookup(
            media,
            COVER_SIZE[0],
            COVER_SIZE[1],
            self.get_album_cover_callback,
            None,
            media.get_artist(),
            media.get_album(),
        )

    def get_album_cover_callback(self, cover, path, data=None):
        if not cover:
            cover = self.get_default_cover()
        self.cover.set_from_pixbuf(cover)

    def get_default_cover(self):
        return AlbumArtCache.get_default_icon(COVER_SIZE[0], COVER_SIZE[1], False)



class BaseSong(GObject.Object):

    def __init__(self, music):
        super().__init__()

        self._music = music
        self.music = tuple(music)
        self.media = self.music[5]

        self.set_track_time()
        self.set_track_name()
        self.set_track_artist()
        self.set_cover()

        self.set_played()

    def set_track_artist(self):
        self.artist =  GLib.markup_escape_text(self.media.get_string(
            Grl.METADATA_KEY_ARTIST) or \
            self.media.get_author() or \
            'Unknown Artist')

    def set_track_name(self):
        pass

    def set_track_time(self):
        pass

    def set_played(self):
        pass

    def set_cover(self):
        pass


class AlbumSong(BaseSong):

    def __init__(self, music, player):
        self.player = player
        super().__init__(music)

    def set_track_name(self):
        self.track_name = GLib.markup_escape_text(self.music[5].get_title())

    def set_track_time(self):
        self.time =  GLib.markup_escape_text(self.music[1])

    def set_played(self):
        if self._music.path < self.player.currentTrack.get_path():
            self.played = True

        else:
            self.played = False

class Song(BaseSong):

    def set_track_name(self):
        self.track_name =  GLib.markup_escape_text(self.music[2])


class ArtistSong(BaseSong):

    def set_track_name(self):
        self.track_name =  GLib.markup_escape_text(self.music[0])


class PlaylistSong(BaseSong):

    def set_track_name(self):
        self.track_name =  GLib.markup_escape_text(self.music[2])
