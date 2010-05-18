# Bring the terminal into focus when F12 is pressed.
#
# GTK only lists windows in a single app, so gtk.Window.present() isn't useful.
# GDK can't list all windows...  gtk.gdk.window_lookup(id) doesn't like the Xlib window.id
# So we use Xlib window.raise_window().  Which by the way, isn't documented here:
# http://python-xlib.sourceforge.net/doc/html/python-xlib_21.html
def handle_show_term(evt):
	print "term command"
	for w in display.screen(0).root.query_tree().children:
		wm_class= w.get_wm_class()
		if wm_class and wm_class[0] == 'Gnome-terminal':
			w.raise_window()
			break

F12 = 96
register_event_listener( F12, handle_show_term)
