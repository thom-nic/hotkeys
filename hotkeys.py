#!/usr/bin/env python
# Hotkeys script for Linux
# Tom Nichols

# USAGE
#
# First, create a python script file under 'hotkeys/' (relative to this file).
# Write a function that will do what you want do.  You can do a lot 
# with the pyGTK, Xlib and virtkey libraries. (Refer to their documentation.)
# After the function is defined (along with any global varables used to keep 
# state), call 
# register_event_listener( keyCode, myFunc )
# You can use the command-line program 'xev' to find the correct 'keycode' 
# that you want to use.
# 
# Now you just need to run this script (hotkeys.py) which will source your
# custom scripts and register your event listeners.
# If you want to run the script at login, use this in your .profile:
# nice python ~/bin/hotkeys.py > hotkeys.log &
# Remember that in this case, your scripts would be in ~/bin/hotkeys/

import Xlib
from Xlib.display import Display
from Xlib import X
import sys,os
import pygtk
pygtk.require('2.0')
import gtk
import virtkey
import re
#import inspect
import time
import threading #, thread

gtk.check_version(2,4,0)


# Exit if we are not in a graphical environment:
try:
	Display()
except Xlib.error.DisplayNameError:
	exit(1)

# The user script path is relative to the location of this file.  
# Change if you want to modify where user scripts are kept:
scriptDir = sys.path[0] + '/hotkeys/' # os.path.dirname(__file__)
print "scriptDir: " + scriptDir


# Commonly used:
display = Display()
# Holds keycode : handler mappings.
keys = {}


def import_scripts():
# source any .py files
	files = filter( lambda f: re.search('\.py$',f), os.listdir(scriptDir) )
	for f in files :
		print "Sourcing user script: " + f
# Adds user-defined functions and vars to the main global scope
		execfile( scriptDir+f, globals() )


def register_event_listener( keyCode, func ):
	keys[keyCode] = func


def get_wm_class():
	"""get the window class of the currently focused window"""
	focus = display.get_input_focus().focus
	wm_class = focus.get_wm_class()
	while focus and not wm_class:  # look for a window class
		focus = focus.query_tree().parent
		wm_class = focus.get_wm_class()
	return wm_class[0]  # get_wm_class returns a tuple


# http://ubuntuforums.org/showthread.php?t=609804
def simulate_keys(keys):
	""" simulate the keys using python-virtkey
		  :param keys: (modifiers, keysym); returned by keystroke_to_x11
	"""
	modifiers, key = keys

	v = virtkey.virtkey()
	if modifiers:
		v.lock_mod(modifiers)
	try:
		v.press_keysym(key)
		v.release_keysym(key)
	finally:
		if modifiers:
			v.unlock_mod(modifiers)


def keystroke_to_x11(keystroke):
	""" convert "ctrl+shift+T" to (1<<2 | 1<<0, 28)
		  :param keystroke: The keystroke string.
		                   - can handle at least one 'real' key
		                   - only ctrl, shift and alt supported yet (case-insensitive)
		  :returns: tuple: (modifiers, keysym)
	"""
	modifiers = 0
	key = ""
	splitted = keystroke.split("+")
	for stroke in splitted:
		lstroke = stroke.lower()
		if lstroke == "ctrl":
			modifiers |= (1 << 2)
		elif lstroke == "shift":
			modifiers |= (1 << 0)
		elif lstroke == "alt":
			modifiers |= (1 << 3) # TODO: right?
		else: # is a ordinary key (Only one)
			key = gtk.gdk.keyval_from_name(stroke)
	return (modifiers, key)


def handle_event(evt):
	'''Event handler callback'''
	if not evt.type == X.KeyPress: return
	keycode = evt.detail
	modifiers = evt.state
	if keycode not in keys : return
	print str(keycode) + ": " + str(modifiers)
	keys[keycode](evt)
		

runGtk = True
class GtkMain( threading.Thread ):
	def run( self ):
		print 'running GTK event loop...'
#		gtk.main()
		while runGtk:
			if gtk.events_pending():
				gtk.main_iteration()
			else: time.sleep(1.5)
		print 'GTK main loop exiting...'
		

def main():
	import_scripts()
	# current display
	root = Display().screen().root

	# we tell the X server we want to catch keyPress event
	root.change_attributes(event_mask = X.KeyPressMask)

	for keycode in keys:
		root.grab_key(keycode, X.AnyModifier, 1,X.GrabModeAsync, X.GrabModeAsync)
	
	try:
		GtkMain().start()
#		thread.start_new_thread( gtk.main, () )
		while 1:
#			gtk.main_iteration()
#			if root.display.pending_events():
			event = root.display.next_event()
			handle_event(event)
	except Exception, inst:
		print 'Error: %s' % inst
	finally:
		print "cleaning up...."
		runGtk = False
#		gtk.main_quit()
		time.sleep(1) # Give the GTK thread time to exit
		exit()
		

if __name__ == '__main__':
	main()
	

