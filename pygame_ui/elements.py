"""
blabla
"""

import os
import sys

import pygame.font as pygfont
import pygame.rect as pygrect
import pygame.draw as pygdraw
import pygame.display as pygdisplay
import pygame.surface as pygsurface

from pygame_ui.constants import *


sys.path.append(os.getcwd())

pygfont.init()


class UI_Element:
	is_visible = True
	is_hoverable = False
	is_clickable = False
	position = [0,0]
	position_anchor = "top left"
	position_relative = False
	position_unit = "pixels" # or "percentage" (doesn't work yet)
	size = [0,0]
	size_units = "pixels" # or "percentage" (doesn't work yet)
	auto_size = False
	background_color = None

	def __init__(self, initial_data, kwargs):
		for dictionary in initial_data:
			for key in dictionary:
				setattr(self, key, dictionary[key])
		self.parent = kwargs.pop('parent')
		for key in kwargs:
			setattr(self, key, kwargs[key])

		self.change_position(self.position)

	def change_position(self, new_position):
		"""
		You can figure this one out yourself. If you can't then... *sigh*
		"""
		position_zero = [0,0]
		if self.position_relative:
			position_zero = [position_zero[i] + self.parent.position[i] for i in [0,1]]
		if self.position_anchor == 'center':
			anchor = [0,0]
		else:
			anchor = [ANCHORS[self.position_anchor.split(' ')[i]] for i in [1,0]]
		self.position = [new_position[i] - (anchor[i]/2+.5)*self.size[i] + position_zero[i] for i in [0,1]]
		self.rectangle = pygrect.Rect(self.position, self.size)

	def change_size(self, new_size):
		"""
		You can figure this one out yourself. If you can't then... *sigh*
		"""
		self.size = new_size
		self.change_position(self.position)
	
	def draw_bg(self, pygame_window):
		draw_surface = pygsurface.Surface(pygdisplay.get_surface().get_size()).convert_alpha()
		draw_surface.fill((0,0,0,0))

		if self.auto_size:
			if isinstance(self, label):
				auto_rect = pygrect.Rect(self.position, self.font.size(self.text))
			pygdraw.rect(draw_surface, self.background_color, auto_rect)
		else:
			pygdraw.rect(draw_surface, self.background_color, self.rectangle)
		
		if len(self.background_color) < 4:
			draw_surface.set_alpha(255)

		pygame_window.blit(draw_surface, [0,0])


class frame(UI_Element):
	"""
	The UI element that works as a sort of bundle or group.

	Yes, frame-ception is a thing.
	"""
	
	contents = {}

	def __init__(self, *initial_data, **kwargs):
		self.elements = {}
		super().__init__(initial_data, kwargs)
		for name, data in self.contents.items():
			element_type = data.pop('type')
			self.elements[name] = globals()[element_type](data, parent=self)
	
	def get_text_input_elements(self):
		text_input_elements = []
		for name, element in self.elements.items():
			if element.is_visible:
				if isinstance(element, frame):
					text_input_elements.extend(element.get_text_input_elements())
				elif isinstance(element, text_input):
					text_input_elements.append(element)
		return text_input_elements

	def get_interactive_elements(self):
		interactives = []
		for name, element in self.elements.items():
			if element.is_visible:
				if isinstance(element, frame) and not isinstance(element, button):
					interactives.extend(element.get_interactive_elements())
				elif element.is_hoverable or element.is_clickable:
					interactives.append(element)
		return interactives
	
	def draw(self, pygame_window):
		for i in self.elements.values():
			if i.is_visible:
				if i.background_color != None:
					i.draw_bg(pygame_window)
				i.draw(pygame_window)


class label(UI_Element):
	"""
	The UI element for text.

	Anything with letters will use this class.
	"""
	
	text = "Empty Label"
	text_color = (255,255,255)
	text_aa = True
	font_name = 'Arial'
	font_size = 10
	font_bold = False
	font_italic = False

	def __init__(self, *initial_data, **kwargs):
		super().__init__(initial_data, kwargs)
		self.font = pygfont.SysFont(self.font_name, self.font_size, self.font_bold, self.font_italic)
	
	def change_font(self, **kwargs):
		"""
		Used to change attributes of the font.

		The keyword arguments must exist in the following list:
		>>> ['font_name', 'font_size', 'font_bold', 'font_bold']
		"""

		for key in kwargs:
			if key in FONT_ATTRIBUTES:
				setattr(self, key, kwargs[key])
			else:
				raise KeyError(key+' is not a font attribute. '+MUST_BE+FONT_ATTRIBUTES+'\n'+ISSUE_REPORT)
		self.font = pygfont.SysFont(self.font_name, self.font_size, self.font_bold, self.font_italic)

	def draw(self, pygame_window):
		text_surface = self.font.render(self.text, self.text_aa, self.text_color, self.background_color)
		pygame_window.blit(text_surface, self.position)


class text_input(label):
	"""
	The UI element for an input field.

	My quote-bucket is empty :(
	"""
	is_clickable = True
	click_start = False
	click_end = False
	click_held = False
	typing_start_on_click = True
	typing_end_on_enter = True
	typing = False
	text = "Your input here"
	caret = False
	caret_timer = 0

	def draw(self, pygame_window):
		text_to_render = self.text
		if self.caret:
			text_to_render += '|'
		text_surface = self.font.render(text_to_render, self.text_aa, self.text_color, self.background_color)
		pygame_window.blit(text_surface, self.position)


class button(frame):
	"""
	The UI element for a button.

	What does this button do?
	"""
	is_clickable = True
	is_hoverable = True
	click_start = False
	click_end = False
	click_held = False
	hover_start = False
	hover_end = False
	hover_held = False


class switch(UI_Element):
	"""
	The UI element for a switch.

	Switcharoo!
	"""
	is_clickable = True
	is_hoverable = True
	click_start = False
	click_end = False
	click_held = False
	hover_start = False
	hover_end = False
	hover_held = False
	state = False
	preset = None

	def __init__(self, *initial_data, **kwargs):
		super().__init__(initial_data, kwargs)

	def draw(self, pygame_window):
		if self.preset == 'simple':
			size = [self.size[0]/2-5, self.size[1]-10]
			position = [self.position[0]+5+size[0]*int(self.state), self.position[1]+5]
			pygdraw.rect(pygame_window, (200,200,200), pygrect.Rect(position, size))


class slider(UI_Element):
	"""
	The UI element that slides.

	Sliiide to the left, sliiide to the right, criss cross!
	"""
	is_clickable = True
	is_hoverable = True
	click_start = False
	click_end = False
	click_held = False
	hover_start = False
	hover_end = False
	hover_held = False
	value_min = 0
	value_max = 1
	value = 0
	preset = None

	def __init__(self, *initial_data, **kwargs):
		super().__init__(initial_data, kwargs)

	def set_value_from_pos(self, position):
		if self.preset == 'simple':
			self.value/(self.value_max-self.value_min)
			x = (self.value_max - self.value_min) * (position[0]-self.size[1]/2 - self.position[0])/(self.size[0]-self.size[1])
			self.value = max(min(self.value_max, x), self.value_min)

	def draw(self, pygame_window):
		if self.preset == 'simple':
			size = [self.size[1]-10, self.size[1]-10]
			position = [self.position[0]+5+(self.size[0]-self.size[1])*self.value/(self.value_max-self.value_min), self.position[1]+5]
			pygdraw.rect(pygame_window, (200,200,200), pygrect.Rect(position, size))


class dropdown(UI_Element):
	"""
	Unfinished
	"""
	is_clickable = True

	def __init__(self, *initial_data, **kwargs):
		super().__init__(initial_data, kwargs)

	def draw(self, pygame_window):
		pass