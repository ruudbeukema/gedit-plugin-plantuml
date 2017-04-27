#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

import os
from gettext import gettext as _

# All UI-strings marked for translation are listed here for convenience
BTN_TXT_SAVE						= _("Save")
BTN_TOOLTIP_SAVE					= _("Save visualization as PNG")
BTN_TXT_COPY						= _("Copy")
BTN_TOOLTIP_COPY					= _("Copy visualization to clipboard")
BTN_TXT_ZOOMFIT						= _("Zoom fit")
BTN_TOOLTIP_ZOOMFIT					= _("Make visualization fit its container")
BTN_TXT_UNDOCK						= _("Undock")
BTN_TOOLTIP_UNDOCK					= _("Undock visualization from panel")
BTN_TXT_DOCK						= _("Dock")
BTN_TOOLTIP_DOCK					= _("Dock visualization in panel")

FILECHOOSER_TITLE					= _("Store as PNG")
FILECHOOSER_FILTER_NAME				= _("PNG files")
FILECHOOSER_FAILURE_DIALOG_TITLE	= _("Failed to store image")
FILECHOOSER_FAILURE_DIALOG_MSG		= _("Failure message:")


class GtkPlantumlWidget(Gtk.VBox):
	def __init__(self):
		Gtk.VBox.__init__(self)
		
		self.diagram_collection = DiagramCollection()
		self.menubar = MenuBar(self.__on_copy_image_clicked,
		                       self.__on_save_image_clicked,
		                       self.__on_zoom_fit_toggled)

		self.pack_start(self.diagram_collection, True, True, 0)
		self.pack_start(self.menubar, False, False, 0)

	def __on_copy_image_clicked(self, widget):
		painting = self.diagram_collection.get_active_diagram()

		clip = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		clip.set_image(painting.get_image_pixbuf())

	def __on_save_image_clicked(self, widget):
		file_dialog = Gtk.FileChooserDialog(FILECHOOSER_TITLE, None, Gtk.FileChooserAction.SAVE,
		                                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE,
		                                     Gtk.ResponseType.OK))

		filter_png = Gtk.FileFilter()
		filter_png.set_name(FILECHOOSER_FILTER_NAME)
		filter_png.add_mime_type("image/*.png")
		file_dialog.add_filter(filter_png)
		response = file_dialog.run()

		if response == Gtk.ResponseType.OK:
			file_name, file_extension = os.path.splitext(file_dialog.get_filename())

			# Make sure to add .png
			if file_extension != ".png":
				file_name += '.png'

			file_dialog.destroy()

			painting = self.diagram_collection.get_active_diagram()
			pixbuf = painting.get_image_pixbuf()
			try:
				pixbuf.savev(file_name, 'png', [], [])
			except Exception as e_msg:
				msg_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
				                               FILECHOOSER_FAILURE_DIALOG_TITLE)
				msg_dialog.format_secondary_text(FILECHOOSER_FAILURE_DIALOG_MSG + "\n" + e_msg)
				msg_dialog.run()
				msg_dialog.destroy()
		else:
			file_dialog.destroy()

	def __on_zoom_fit_toggled(self, widget):
		self.diagram_collection.set_zoom_fit(widget.get_active())
		
	def set_uml_generation_in_progress(self, source_filepath):
		painting = self.diagram_collection.get_active_diagram()

		painting.set_in_progress()

	def update_diagram(self, source_filepath, output_filepath):
		self.get_parent().show()

		self.diagram_collection.update(source_filepath, output_filepath)

	def add_diagram(self, source_filepath, title):
		painting = Diagram(source_filepath)
		return self.diagram_collection.add_diagram(painting, source_filepath, title)

	def remove_diagram(self, source_filepath):
		self.diagram_collection.remove_diagram(source_filepath)

	def set_active_diagram(self, source_filepath):
		return self.diagram_collection.set_active_diagram(source_filepath)


class MenuBar(Gtk.HBox):
	def __init__(self, on_btn_copy_clicked_callback, on_btn_save_clicked_callback, on_zoom_fit_toggled_callback):
		Gtk.HBox.__init__(self)
		self.set_border_width(3)

		btn = Gtk.Button(None, None)
		btn.add(MenuBarItem(Gtk.Image(stock=Gtk.STOCK_SAVE), BTN_TXT_SAVE))
		btn.set_tooltip_text(BTN_TOOLTIP_SAVE)
		btn.connect("clicked", on_btn_save_clicked_callback)
		self.pack_start(btn, False, False, 2)

		btn = Gtk.Button(None, None)
		btn.add(MenuBarItem(Gtk.Image(stock=Gtk.STOCK_COPY), BTN_TXT_COPY))
		btn.set_tooltip_text(BTN_TOOLTIP_COPY)
		btn.connect("clicked", on_btn_copy_clicked_callback)
		self.pack_start(btn, False, False, 2)

		btn = Gtk.ToggleButton(None, None)
		btn.add(MenuBarItem(Gtk.Image(stock=Gtk.STOCK_ZOOM_FIT), BTN_TXT_ZOOMFIT))
		btn.set_tooltip_text(BTN_TOOLTIP_ZOOMFIT)
		btn.connect("clicked", on_zoom_fit_toggled_callback)
		self.pack_start(btn, False, False, 2)

	def set_zoom_fit(self, zoom_fit_enable=False):
		pass


class MenuBarItem(Gtk.HBox):
	def __init__(self, gtk_image=None, title=None):
		Gtk.HBox.__init__(self)

		self.image = None
		self.label = None

		self.set_item(gtk_image, title)

	def set_item(self, gtk_image, title):
		if self.image:
			self.remove(self.image)
		if self.label:
			self.remove(self.label)

		self.image = gtk_image
		self.label = Gtk.Label(title)

		self.pack_start(self.image, False, False, 2)
		self.pack_start(self.label, False, False, 2)


class DiagramCollection(Gtk.Notebook):
	def __init__(self):
		Gtk.Notebook.__init__(self)

		self.set_show_tabs(True)
		self.set_scrollable(False)

		self.connect('size-allocate', self.__on_resize)
		self.connect('switch-page', self.__on_tab_changed)

	def __on_resize(self, widget, data):
		self.refresh_current_diagram()

	def __on_tab_changed(self, widget, page, page_n):
		pass

	def add_diagram(self, diagram, source_filepath, title):
		diagram_exists, reference = self.get_diagram_exists(source_filepath)
		if not diagram_exists:
			label = Gtk.Label(title)
			label.set_tooltip_text(source_filepath)

			self.append_page(diagram, label)
			self.refresh_current_diagram()

	def remove_diagram(self, source_filepath):
		diagram_exists, reference = self.get_diagram_exists(source_filepath)
		if diagram_exists:
			self.remove_page(reference)

	def update(self, source_filepath, output_filepath):
		diagram_exists, reference = self.get_diagram_exists(source_filepath)
		if diagram_exists:
			self.get_nth_page(reference).update(output_filepath)
			self.set_current_page(reference)

	def get_active_diagram(self):
		reference = self.get_current_page()
		if reference >= 0:
			return self.get_nth_page(reference)
		else:
			return None

	def set_active_diagram(self, source_filepath):
		diagram_exists, reference = self.get_diagram_exists(source_filepath)
		if diagram_exists:
			self.set_current_page(reference)
			self.refresh_current_diagram()

		return diagram_exists

	def get_diagram_exists(self, source_filepath):
		reference = -1
		diagram_exists = False
		for i in range(self.get_n_pages()):
			item = self.get_nth_page(i)
			if source_filepath == item.get_source_filepath():
				reference = i
				diagram_exists = True

		return diagram_exists, reference

	def refresh_current_diagram(self):
		reference = self.get_current_page()
		if reference >= 0:
			self.get_nth_page(reference).refresh_image()

	def set_zoom_fit(self, zoom_fit_enable=False):
		diagram = self.get_active_diagram()
		diagram.set_zoom_fit(zoom_fit_enable)
		self.refresh_current_diagram()

	def get_zoom_fit(self):
		diagram = self.get_active_diagram()
		return diagram.get_zoom_fit()



class Diagram(Gtk.VBox):
	"""
	The Diagram class takes care of rendering the UML diagram and displaying its status information
	"""

	def __init__(self, source_filepath):
		"""
		Constructs a Diagram instance (which is a Gtk Widget)
		
		:param source_filepath: the path to the source file
		"""
		Gtk.VBox.__init__(self)

		self.source_filepath = source_filepath
		self.diagram_filepath = None
		self.is_zoomed_to_fit = False
		self.is_grabbed = False
		self.is_in_progress = False
		self.prev_pointer = self.get_pointer()

		self.diagram = Gtk.Image()
		event_box = Gtk.EventBox()
		event_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(255, 255, 255, 1))
		event_box.add(self.diagram)

		event_box.connect('enter-notify-event', self.__on_enter_diagram)
		event_box.connect('leave-notify-event', self.__on_leave_diagram)
		event_box.connect('button-press-event', self.__on_grab_diagram)
		event_box.connect('button-release-event', self.__on_release_diagram)
		event_box.connect('motion-notify-event', self.__on_move_diagram)

		self.scrolled_window = Gtk.ScrolledWindow()
		self.scrolled_window.add_with_viewport(event_box)
		self.pack_start(self.scrolled_window, True, True, 0)

		self.spinner = Gtk.Spinner()
		self.spinner.set_size_request(32, 32)
		self.spinner_area = Gtk.HBox()
		self.spinner_area.pack_start(self.spinner, False, False, 4)
		self.spinner_area.pack_start(Gtk.Label("Generating diagram..."), False, False, 2)
		self.pack_start(self.spinner_area, False, False, 2)
		self.spinner_area.hide()

	def __on_enter_diagram(self, event, data):
		""" Changes the mouse cursor into a hand when the 
			user starts hovering over the diagram """
		cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
		data.window.set_cursor(cursor)

	def __on_leave_diagram(self, event, data):
		""" Reverts the mouse cursor back to what it was before 
			the user started hovering over the diagram """
		data.window.set_cursor(None)

	def __on_grab_diagram(self, event, data):
		""" Handle the grabbing of the diagram """
		self.is_grabbed = True
		self.prev_pointer = self.scrolled_window.get_pointer()

	def __on_release_diagram(self, event, data):
		""" Abort the grabbing of the diagram """
		self.is_grabbed = False

	def __on_move_diagram(self, context, data):
		""" Handles the moving (swiping as it were) of the diagram (only if it is grabbed) """
		if self.is_grabbed:
			pointer = self.scrolled_window.get_pointer()

			dX = pointer[0] - self.prev_pointer[0]
			hor = self.scrolled_window.get_hadjustment()
			X = hor.get_value() - float(dX) / 8
			hor.set_value(X)

			dY = pointer[1] - self.prev_pointer[1]
			ver = self.scrolled_window.get_vadjustment()
			Y = ver.get_value() - float(dY) / 8
			ver.set_value(Y)

	def set_zoom_fit(self, zoom_fit_enable=False):
		""" Enable the zoom-fit behaviour """
		self.is_zoomed_to_fit = zoom_fit_enable

	def get_zoom_fit(self):
		""" Disable the zoom-fit behaviour """
		return self.is_zoomed_to_fit

	def set_in_progress(self):
		self.is_in_progress = True
		self.spinner_area.show()
		self.spinner.start()

	def update(self, diagram_filepath):
		self.diagram_filepath = diagram_filepath

		self.is_in_progress = False

		self.spinner.stop()
		self.spinner_area.hide()

		self.refresh_image()

	def refresh_image(self):
		if self.diagram_filepath and not self.is_in_progress:
			try:
				pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.diagram_filepath)
				if self.is_zoomed_to_fit:
					pixbuf = self.zoom_fit(pixbuf)

				self.diagram.clear()
				self.diagram.set_from_pixbuf(pixbuf)
			except GLib.Error:
				print("OhOh!")

	def get_source_filepath(self):
		return self.source_filepath

	def zoom_fit(self, pixbuf):
		parent = self.scrolled_window.get_children()[0]
		par_w = parent.get_allocation().width
		par_h = parent.get_allocation().height
		pix_w = pixbuf.get_width()
		pix_h = pixbuf.get_height()
		if (pix_w > par_w) or (pix_h > par_h):
			sf_w = par_w / pix_w
			sf_h = par_h / pix_h
			sf = min(sf_w, sf_h)
			sc_w = round(pix_w * sf, -1)
			sc_h = round(pix_h * sf, -1)
			if (sc_w > 0) and (sc_h > 0):
				return pixbuf.scale_simple(sc_w, sc_h, GdkPixbuf.InterpType.HYPER)
			else:
				return pixbuf
		else:
			return pixbuf

	def get_image_pixbuf(self):
		return self.diagram.get_pixbuf()
