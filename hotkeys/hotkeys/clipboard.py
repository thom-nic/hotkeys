# This hotkey turns your capslock into a multi-buffered clipboard stack.
# Some helpful links:
# http://www.answermysearches.com/python-how-to-copy-and-paste-to-the-clipboard-in-linux/286/
# http://www.larsen-b.com/Article/184.html
# http://ubuntuforums.org/showthread.php?t=609804

# If using the CapsLock as your hotkey, you probably want to use this as well:
# xmodmap -e "remove lock = Caps_Lock"
# to avoid the 'lock' being turned on when you use your hotkey.
# Or put this next line in a file called .xmodmaprc :
# remove lock = Caps_Lock 
# and source it from your .profile like so:
#	xmodmap ~/.xmodmaprc


# Primary selection automatically contains whatever text is highlighted; 
# this avoids the need to send a ctrl+c/ ctrl+x keystroke
cb = gtk.clipboard_get(gtk.gdk.SELECTION_PRIMARY)
pcb = gtk.clipboard_get()

capslock  = 66

stack = []

def handle_clip_command(evt) :
	print "clip command"
	modifiers = evt.state
	if modifiers & 4: do_copy(1) # ctrl key
	elif modifiers & 1: do_paste() # shift key
	elif modifiers & 64: show_stack_dialog() # win key
	else: do_copy() # no modifier key


register_event_listener( capslock, handle_clip_command )


def do_copy(cut=0):
	key = 'ctrl+c'
	if cut: key= 'ctrl+x'
	print key
	focus = Display().get_input_focus().focus
	wm_class = get_wm_class()
		
	if not wm_class or wm_class == 'xterm': return
	if wm_class == 'gnome-terminal': key='ctrl+shift+c'
	
#	cb.set_text('')
#	time.sleep(.05)
#	if cb.wait_is_text_available(): temp = cb.wait_for_text()
#	simulate_keys(keystroke_to_x11(key))
#	time.sleep(.05)
	if not cb.wait_is_text_available(): return
	text = cb.wait_for_text()
	if not text: return
	if cut: simulate_keys(keystroke_to_x11('BackSpace'))
	cb.set_text('')
	print "got text: " + text
	stack.append( text )
	print stack


def get_text(cb, text, data):
	print 'callback! ' + text
	if text and len( text ) > 0:
		print "got text: " + text
		stack.append(text)


def do_paste():
	key = 'ctrl+v'
	wm_class = get_wm_class()
		
	if not wm_class or wm_class == 'xterm': return
	if wm_class == 'gnome-terminal': key='ctrl+shift+v'	
	if len(stack) < 1: return

	text = stack.pop()
	print 'paste: ' + text
	pcb.set_text(text)
	time.sleep(.1)
	simulate_keys(keystroke_to_x11(key))
#	time.sleep(.5)
#	pcb.clear()


def show_stack_dialog():
#	if dialog: return  # if it's already shown then bugger off.
	
	dialog = gtk.Dialog("Clipboard Stack", None, 0, (gtk.STOCK_OK,gtk.RESPONSE_OK))
	dialog.connect('close', lambda *w: w.destroy())
	dialog.connect('response', lambda w,r: w.destroy())
	dialog.set_default_size(400,300)
	tv = gtk.TextView()
	tv.set_size_request(390,290)
	tv.set_wrap_mode( gtk.WRAP_WORD_CHAR )
	dialog.get_child().add(tv)

	txt = ''
	for t in stack:
		txt += t + '\n\n'
	tv.get_buffer().set_text(txt)

	dialog.show_all()
	dialog.grab_focus()
	dialog.run()
#	dialog.present()


