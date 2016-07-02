#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gettext import gettext as _
from gi.repository import Gtk, Gdk, GdkPixbuf
from .gallery import Gallery
from .painting import Painting
import os


# All UI-strings marked for translation are listed here for convenience
BTN_TXT_SAVE						= _("Save")
BTN_TOOLTIP_SAVE					= _("Save visualization as PNG")
BTN_TXT_COPY						= _("Copy")
BTN_TOOLTIP_COPY					= _("Copy visualization to clipboard")
BTN_TXT_ZOOMFIT						= _("Zoom fit")
BTN_TOOLTIP_ZOOMFIT					= _("Make visualization fit its container")
#BTN_TXT_ZOOMFIT					= _("Zoom in")
#BTN_TOOLTIP_ZOOMFIT				= _("Zoom in on visualization")
#BTN_TXT_ZOOMFIT					= _("Zoom out")
#BTN_TOOLTIP_ZOOMFIT				= _("Zoom out from visualization")
BTN_TXT_UNDOCK						= _("Undock")
BTN_TOOLTIP_UNDOCK					= _("Undock visualization from panel")
BTN_TXT_DOCK						= _("Dock")
BTN_TOOLTIP_DOCK					= _("Dock visualization in panel")

FILECHOOSER_TITLE					= _("Store as PNG")
FILECHOOSER_FILTER_NAME				= _("PNG files")
FILECHOOSER_FAILURE_DIALOG_TITLE	= _("Failed to store image")
FILECHOOSER_FAILURE_DIALOG_MSG		= _("Failure message:")


class ToolsMenu_Item(Gtk.HBox):
	m_image = None
	m_label = None

	def __init__(self, in_image, in_text):
		Gtk.HBox.__init__(self)

		self.m_image = in_image
		self.m_label = Gtk.Label(in_text)

		self.pack_start(self.m_image, False, False, 2)
		self.pack_start(self.m_label, False, False, 2)
		self.show_all()


	def update(self, in_image, in_text):
		self.remove(self.m_image)
		self.remove(self.m_label)

		self.m_image = in_image
		self.m_label = Gtk.Label(in_text)

		self.pack_start(self.m_image, False, False, 2)
		self.pack_start(self.m_label, False, False, 2)
		self.show_all()


class ToolsMenu(Gtk.HBox):
	m_has_dock_icon = False

	def __init__(self, in_on_btn_copy_clicked, in_on_btn_save_clicked, in_on_zoom_fit_toggle, in_on_dock_toggle):
		Gtk.HBox.__init__(self)
		self.set_border_width(3)
		
		btn = Gtk.Button(None, None)
		btn.add(ToolsMenu_Item( Gtk.Image(stock=Gtk.STOCK_SAVE), BTN_TXT_SAVE ) )
		btn.set_tooltip_text( BTN_TOOLTIP_SAVE )
		btn.connect("clicked", in_on_btn_save_clicked)		
		self.pack_start(btn, False, False, 2)

		btn = Gtk.Button(None, None)
		btn.add(ToolsMenu_Item( Gtk.Image(stock=Gtk.STOCK_COPY), BTN_TXT_COPY ) )
		btn.set_tooltip_text( BTN_TOOLTIP_COPY )
		btn.connect("clicked", in_on_btn_copy_clicked)
		self.pack_start(btn, False, False, 2)
		
#		btn = Gtk.Button(None, None)
#		btn.add(ToolsMenu_Item( Gtk.Image(stock=Gtk.STOCK_ZOOM_IN), BTN_TXT_ZOOMIN ) )
#		btn.set_tooltip_text( BTN_TOOLTIP_ZOOMIN )
#		btn.connect("clicked", in_on_zoom_in_toggle)
#		self.pack_start(btn, False, False, 2)
		
#		btn = Gtk.Button(None, None)
#		btn.add(ToolsMenu_Item( Gtk.Image(stock=Gtk.STOCK_ZOOM_OUT), BTN_TXT_ZOOMOUT ) )
#		btn.set_tooltip_text( BTN_TOOLTIP_ZOOMOUT ))
#		btn.connect("clicked", in_on_zoom_out_toggle)
#		self.pack_start(btn, False, False, 2)
		
		btn = Gtk.ToggleButton(None, None)
		btn.add(ToolsMenu_Item( Gtk.Image(stock=Gtk.STOCK_ZOOM_FIT), BTN_TXT_ZOOMFIT ) )
		btn.set_tooltip_text( BTN_TOOLTIP_ZOOMFIT )
		btn.connect("clicked", in_on_zoom_fit_toggle)
		self.pack_start(btn, False, False, 2)

		if in_on_dock_toggle != None:
			self.m_has_dock_icon = True

			empty_box = Gtk.Box()
			self.pack_start(empty_box, True, False, 2)

			btn = Gtk.Button(None, None)
			btn.add(ToolsMenu_Item( Gtk.Image(stock=Gtk.STOCK_FULLSCREEN), BTN_TXT_UNDOCK ) )
			btn.set_tooltip_text( BTN_TOOLTIP_UNDOCK )
			btn.connect("clicked", in_on_dock_toggle)			
			self.pack_start(btn, False, False, 2)

	
	def set_dock_state(self, in_is_docked):
		if self.m_has_dock_icon:
			button = self.get_children()[4]
			menu_item = button.get_children()[0]
			if in_is_docked:
				image = Gtk.Image( stock=Gtk.STOCK_FULLSCREEN )
				menu_item.update(image, BTN_TXT_UNDOCK )
				button.set_tooltip_text( BTN_TOOLTIP_UNDOCK )
			else:
				image = Gtk.Image( stock=Gtk.STOCK_LEAVE_FULLSCREEN )
				menu_item.update(image, BTN_TXT_DOCK )
				button.set_tooltip_text( BTN_TOOLTIP_DOCK )


class Viewer(Gtk.VBox):	
	m_gallery = None
	m_toolsmenu = None

		
	def __init__(self, in_on_dock_toggle):
		Gtk.VBox.__init__(self)
		
		self.m_gallery = Gallery()		
		self.m_toolsmenu = ToolsMenu(self.on_copy_image, self.on_save_image, self.on_zoom_fit, in_on_dock_toggle)

		self.pack_start(self.m_gallery, True, True, 0)
		self.pack_start(self.m_toolsmenu, False, False, 0)
		
		#self.connect('size-allocate', self.on_resize)
		self.show_all()

		
	def set_dock_state(self, in_is_docked):
		self.m_toolsmenu.set_dock_state(in_is_docked)
		self.m_gallery.set_dock_state(in_is_docked)


	def uml_update(self, in_uml_filepath):
		return self.m_gallery.painting_update(in_uml_filepath)


	def uml_exists(self, in_uml_filepath):
		return self.m_gallery.painting_exists(in_uml_filepath)


	def uml_add(self, in_uml_filepath, in_img_filepath, in_title):
		painting = Painting(in_uml_filepath, in_img_filepath)
		return self.m_gallery.painting_add(painting, in_title)


	def uml_remove(self, in_uml_filepath):
		self.m_gallery.painting_remove(in_uml_filepath)


	def uml_set_active(self, in_uml_filepath):
		return self.m_gallery.painting_set_active(in_uml_filepath)


	def on_copy_image(self, widget):
		painting = self.m_gallery.painting_get_active()

		clip = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		clip.set_image(painting.get_image_pixbuf())

		
	def on_save_image(self, widget):
		file_dialog = Gtk.FileChooserDialog(FILECHOOSER_TITLE, None, Gtk.FileChooserAction.SAVE, 
											(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE, 
											Gtk.ResponseType.OK))
	    
		filter_png = Gtk.FileFilter()
		filter_png.set_name( FILECHOOSER_FILTER_NAME )
		filter_png.add_mime_type("image/*.png")
		file_dialog.add_filter(filter_png)
		response = file_dialog.run()
	    
		if response == Gtk.ResponseType.OK:
			file_name, file_extension = os.path.splitext(file_dialog.get_filename())
		
			# Make sure to add .png
			if file_extension != ".png":
				file_name += '.png'
		
			file_dialog.destroy()

			painting = self.m_gallery.painting_get_active()
			pixbuf = painting.get_image_pixbuf()
			try:
				pixbuf.savev(file_name, 'png', [], [])
			except Exception as e_msg:
				msg_dialog = Gtk.MessageDialog( None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
												FILECHOOSER_FAILURE_DIALOG_TITLE )
				msg_dialog.format_secondary_text( FILECHOOSER_FAILURE_DIALOG_MSG + "\n" + e_msg)
				msg_dialog.run()
				msg_dialog.destroy()
		else:
			file_dialog.destroy()


	def on_zoom_fit(self, in_widget):
		painting = self.m_gallery.painting_get_active()
		zoom_fit = painting.get_zoom_fit()
		painting.set_zoom_fit(not zoom_fit)
		painting.refresh_image()
		
