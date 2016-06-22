'''
    PPCLFunctions.py is a PPCL plugin for the Sublime Text 3 text editor.
    Copyright (C) 2016  Brien Blandford (Smith Engineering, PLLC)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''



import sublime, sublime_plugin
import re


class InsertCommentCommand(sublime_plugin.TextCommand):
	'''
	This command will insert a comment (01000 tab C ) when ctrl+/ is pressed over all
	the selected lines. 
	'''
	def run(self, edit):
		rows = set()
		counter = 1

		# determine all the rows in the selection
		for region in self.view.sel():
			lines_tuple = self.view.split_by_newlines(region)
			for region in lines_tuple:
				rows.add(int(self.view.rowcol(region.begin())[0]))

		commented_rows = self.determine_toggle(rows)
		if all(commented_rows[0] == item for item in commented_rows):
			switch_all = True
		else:
			switch_all = False

		for row in rows:
			if (((switch_all==True) and (commented_rows[0]==False))
				or switch_all==False):
				line = self.view.substr(self.view.line(
						sublime.Region(self.view.text_point(row, 0))))
				commentedLine = self.toggle_on(line)
				self.view.replace(edit, self.view.line(
					sublime.Region(self.view.text_point(row, 0))),
									commentedLine)
			elif (switch_all==True) and (commented_rows[0]==True):
				line = self.view.substr(self.view.line(
						sublime.Region(self.view.text_point(row, 0))))
				commentedLine = self.toggle_off(line)
				self.view.replace(edit, self.view.line(
						sublime.Region(self.view.text_point(row, 0))),
										commentedLine)


	def determine_toggle(self, rows):
		'''
		make a boolean list to determine which lines need to have
		comments added and/or removed.
		'''
		commented_rows = []
		for row in rows:
			line = self.view.substr(self.view.line(
					sublime.Region(self.view.text_point(row, 0))))
			lineNum = re.search(r'(^[0-9]+)([\t]|[ ]+)(C ?)?', line)
			if (lineNum.groups()[-1] == 'C') or (lineNum.groups()[-1] == 'C '):
				commented_rows.append(1)
			else:
				commented_rows.append(0)
		return commented_rows


	def toggle_on(self,line):
		'''
		add a comment to the beginning.
		'''
		try:
			lineNum = re.search(r'(^[0-9]+)([\t]|[ ]+)(C ?)?', line)
			return (line.replace(lineNum.groups()[0] + lineNum.groups()[1],
						lineNum.groups()[0] + lineNum.groups()[1] + 'C '))
		except:
			pass


	def toggle_off(self,line):
		'''
		remove a comment from the beginning.
		'''
		try:
			lineNum = re.search(r'(^[0-9]+)([\t]|[ ]+)(C ?)', line)
			tempstring = ''
			for group in lineNum.groups():
				tempstring += str(group)
			return (line.replace(tempstring, 
					tempstring.replace('C ', '').replace('C', '')))
		except:
			pass


class ToggleDefineCommand(sublime_plugin.TextCommand):
	'''
	This function will toggle the DEFINE statement strings.
	Toggle OFF will replace all the %..% with the assocaited string.
	Toggle OFF will replace all occurences of the assocaited string with %..%.
	'''

	def run(self, edit, toggle):
		# print ("made it =", kwargs)
		content = self.view.substr(sublime.Region(0, self.view.size()))
		define_map, define_lines = self.get_defines(content)

		if toggle == 'off':
			newcontent = self.toggle_off(content, define_map)

		if toggle == 'on':
			newcontent = self.toggle_on(content, define_map, define_lines)

		# print (newcontent)
		# replace the existing text with the modified text
		selections = sublime.Region(0, self.view.size())
		self.view.replace(edit, selections, newcontent)


	def get_defines(self, content):
		'''
		regex search for all the define statements, return a dict of the associations
		with the %X% as the key, return the line numbers associated
		'''
		# compile for regex, find DEFINE lines, parameters, and associated strings
		p = re.compile(r'(^[0-9]+)([\t]|[ ]+)(DEFINE\()([A-Z0-9]*)(\,")(.*)"',
						re.MULTILINE)
		define_terms = re.findall(p, content)
		define_map = {}
		define_lines = []
		for item in define_terms:
			define_map['%'+item[3]+'%'] = item[5]
			define_lines.append(item[0])

		return define_map, define_lines


	def toggle_on(self, content, define_map, define_lines):
		'''
		toggle on the define statements, meaning put the %X% back
		'''
		newcontent = ''
		p = re.compile(r'(^[0-9]+)([\t]|[ ]+)')
		first_line=True
		for line in content.split('\n'):
			nextline = line
			# index the regex search to get just the number
			try:
				# this means the line has a line number
				linenum = re.findall(p, line)[0][0]
			except:
				break

			if any(word in nextline for word in define_map.values()) and linenum not in define_lines:
				for key in define_map.keys():
					nextline = nextline.replace(define_map[key], key)
			# this is silly, but necessary
			# we don't wanna add a \n to the end of the last line
			if first_line:
				newcontent += nextline
			else:
				newcontent += '\n' + nextline
			first_line=False

		return newcontent


	def toggle_off(self, content, define_map):
		'''
		toggle off the define statements, meaning replace %X%
		'''
		for key in define_map.keys():
			content = content.replace(key, define_map[key])
		return content