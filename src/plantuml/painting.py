#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gi.repository import Gtk, Gdk, GdkPixbuf

class Painting(Gtk.ScrolledWindow):
	m_eventbox = None
	m_old_pointer = None
	m_uml_filepath = None
	m_img_filepath = None
	m_img = None
	m_is_grabbed = False

	
	def __init__(self, in_uml_filepath, in_img_filepath):
		Gtk.ScrolledWindow.__init__(self)
		self.m_old_pointer = self.get_pointer()
		self.m_uml_filepath = in_uml_filepath
		self.m_img_filepath = in_img_filepath
		
		self.m_img = Gtk.Image()
		self.m_img.set_from_file(self.m_img_filepath)

		self.m_event_box = Gtk.EventBox()
		self.m_event_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(255, 255, 255, 1))		
		self.m_event_box.add(self.m_img)
		self.m_event_box.connect('enter-notify-event', self.on_image_enter)
		self.m_event_box.connect('leave-notify-event', self.on_image_leave)
		self.m_event_box.connect('button-press-event', self.on_image_grab)
		self.m_event_box.connect('button-release-event', self.on_image_release)
		self.m_event_box.connect('motion-notify-event', self.on_image_move)
		
		self.add_with_viewport(self.m_event_box)


	def update(self, in_zoom_fit):
		self.refresh_image(in_zoom_fit)

		
	def refresh_image(self, in_zoom_fit):
		self.m_img.clear()

		pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.m_img_filepath)
		if in_zoom_fit:
			pixbuf = self.zoom_fit(pixbuf)
			
		self.m_img.set_from_pixbuf(pixbuf)


	def get_uml_filepath(self):
		return self.m_uml_filepath
		

	def zoom_fit(self, in_pixbuf):
		parent = self.get_children()[0]
		par_w = parent.get_allocation().width
		par_h = parent.get_allocation().height
		pix_w = in_pixbuf.get_width()
		pix_h = in_pixbuf.get_height()
		if (pix_w > par_w) or (pix_h > par_h):
			sf_w = par_w / pix_w
			sf_h = par_h / pix_h
			sf = min(sf_w, sf_h)
			sc_w = round(pix_w * sf, -1)
			sc_h = round(pix_h * sf, -1)
			if (sc_w > 0) and (sc_h > 0):
				return in_pixbuf.scale_simple(sc_w, sc_h, GdkPixbuf.InterpType.HYPER)
			else:
				return in_pixbuf
		else:
			return in_pixbuf
		
		
	def get_image_pixbuf(self):
		return self.m_img.get_pixbuf()
		
		
	def on_image_move(self, context, data):
		if self.m_is_grabbed:
			pointer = self.get_pointer()

			dX = pointer[0] - self.m_old_pointer[0]
			hor = self.get_hadjustment()
			X = hor.get_value() - float(dX)/8
			hor.set_value(X)

			dY = pointer[1] - self.m_old_pointer[1]			
			ver = self.get_vadjustment()
			Y = ver.get_value() - float(dY)/8
			ver.set_value(Y)
			

	def on_image_enter(self, event, data):
		cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
		data.window.set_cursor(cursor)
		

	def on_image_leave(self, event, data):
		data.window.set_cursor(None)
		

	def on_image_grab(self, event, data):
		self.m_is_grabbed = True
		self.m_old_pointer = self.get_pointer()
		

	def on_image_release(self, event, data):
		self.m_is_grabbed = False
