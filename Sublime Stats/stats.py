import sublime
import sublime_plugin


class StatsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		html = """<h1>Sublime Text Statistics</h1>
		<p>Total Keys: {}</p>
		<p>Letters: {}</p>
		<p>Spaces: {}</p>
		<p>Symbols: {}</p>
		<p>Lines: {}</p>
		<p>Other: {}</p>
		""".format(storage.count, storage.letters, storage.spaces, storage.symbols, storage.lines, storage.other)

		## Show a popup with our html above
		self.view.show_popup(html, max_width=512)

class ChangeListener(sublime_plugin.EventListener):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	## Called when anything is modified
	def on_modified(self, view):
		## If the popup is visible when we start working or clicking, we need to hide it
		if view.is_popup_visible():
			view.hide_popup()
		## Returns a list of regions in current view from Sublime
		selectedRegions = view.sel()
		## Variable to store our special characters to compare against
		special_characters = """!@#$%^&*()-+?_=,<>/|`~	:;'."""
		## Iterate through all regions in view
		for region in selectedRegions:
			##Get the last character from the region
			lastCharacterRegion = sublime.Region(region.a - 1, region.a)
			lastCharacter = view.substr(lastCharacterRegion)
			## Increase the overall count and the type of character count
			storage.count += 1
			if lastCharacter.isalpha():
				storage.letters += 1
			elif lastCharacter in special_characters:
				storage.symbols += 1
			elif lastCharacter == '\n':
				storage.lines += 1
			elif lastCharacter == " ":
				storage.spaces += 1
			else:
				storage.other += 1
     
## Class for our counts to be reset after plugin is restarted
class Storage(object):
	count = 0
	letters = 0
	spaces = 0
	symbols = 0
	lines = 0
	other = 0
storage = Storage()
		
