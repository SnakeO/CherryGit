#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, signal
from subprocess import Popen, PIPE

import cherrypy

import sys
import subprocess
import random
import time
import threading
import Queue
import logging

LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 2321

my_path = os.path.dirname(os.path.realpath(__file__ + '/../')) + '/'

class AsynchronousFileReader(threading.Thread):
	'''
	Helper class to implement asynchronous reading of a file
	in a separate thread. Pushes read lines on a queue to
	be consumed in another thread.
	'''

	def __init__(self, fd, queue):
		assert isinstance(queue, Queue.Queue)
		assert callable(fd.readline)
		threading.Thread.__init__(self)
		self._fd = fd
		self._queue = queue

	def run(self):
		'''The body of the tread: read lines and put them on the queue.'''
		for line in iter(self._fd.readline, ''):
			self._queue.put(line)

	def eof(self):
		'''Check whether there is no more content to expect.'''
		return not self.is_alive() and self._queue.empty()

def file_get_contents(filename):
	with open(filename) as f:
		return f.read()

class FabWeb(object):

	@cherrypy.expose
	def index(self):
		return "Git hooks be lurkin' here."

	@cherrypy.expose
	def githook(self, project):

		if project.find('..') + project.find('/') != -2 :
			return "You are not allowed to traverse other directories"

		command = 'fab -f {0}{1}/githook.py update'.format(
			my_path, project)
		
		return self.deploy(command)

	# Enable streaming for the deploy method.  Without this it won't work.
	githook._cp_config = {'response.stream': True}
	
	def deploy(self, command, msg='', **kw):

		print command

		# This javascript just scrolls the iframe to the bottom
		scroll_to_bottom = '<script type="text/javascript">window.scrollBy(0,2000);</script>'
		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
				shell=True, close_fds=True, preexec_fn=os.setsid)

		# Launch the asynchronous readers of the process' stdout and stderr.
		stdout_queue = Queue.Queue()
		stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
		stdout_reader.start()
		stderr_queue = Queue.Queue()
		stderr_reader = AsynchronousFileReader(process.stderr, stderr_queue)
		stderr_reader.start()

		# Save the pid in the user's session (a thread-safe place)
		cherrypy.session['pid'] = process.pid
		cherrypy.session.save()

		def run_command():
			# The yeilds here are the key to keeping things streaming
			yield '<style>body {font-family: monospace;}</style><p>OK, Here we go... ' + command + ' ' + msg + '</p>'

			logging.info(command)
			i = 1
			while not stdout_reader.eof() or not stderr_reader.eof(): # While the process is still running...

				out = ''
				
				# Show what we received from standard output.
				while not stdout_queue.empty():
					out += stdout_queue.get().replace("\n", "<br/>")
					i +=1

				# Show what we received from standard error.
				while not stderr_queue.empty():
					out += stderr_queue.get().replace("\n", "<br/>")
					i +=1

				time.sleep(.1)
				yield out # Stream it to the browser

			# Now write out anything left in the buffer...
			out = ""
			for char in process.stdout.read():
				if char == "\n":
					out += "\nDONE!<br />%s" % scroll_to_bottom
					out += "<script type='text/javascript'>$('body').append( '<embed src=\'http://www.eventsounds.com/wav/donesold.wav\'></embed>');"
				else:
					out += char
			yield out

		return run_command()
	
logfile = my_path + 'logs/cherrygit.log'

cherrypy.config.update({
	'log.screen'		: True,
	'tools.sessions.on'	: True,
	'checker.on'		: False,
	'log.access_file'	: logfile,
	'log.error_file'	: logfile,	
})

cherrypy.config.update({
	'server.socket_host': LISTEN_HOST,
	'server.socket_port': LISTEN_PORT
})

cherrypy.quickstart(FabWeb())
