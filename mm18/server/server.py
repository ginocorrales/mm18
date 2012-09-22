from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

import re
import json

from urls import urlpatterns
from client_manager import MMClientManager
from mm18.game.game_controller import init_game

global_client_manager = MMClientManager()

class MMHandler(BaseHTTPRequestHandler):
	"""HTTP request handler for Mechmania"""

	def respond(self, status_code, data):
		"""
		Responds by sending JSON data back.

		status_code -- string containting HTTP status code.
		data -- dictionary to encode to JSON
		"""

		self.send_response(int(status_code))
		output = json.dumps(data)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(output)

	def match_path(self, method):
		"""Tries to match a path with every url in urlpatterns.

		Searches through the urlpatterns to find a URL matching the given path.
		If it finds one, it tries to call it.  Then it breaks out, so it will
		only call the first pattern it matches.  This method calls the
		corresponding function in urlpatterns from urls.py, so expect side
		effects from the game controller.  It also handles serializtion of JSON
		and will send a 400 error if given invalid JSON.  Wil send a 404 if no
		matching URL is found and a 405 if a URL is found but with the wrong
		method.

		method -- string containing the HTTP request method
		"""

		invalid_method = False

		# Special case connection. Shut up I know it's ugly.
		connect_match = re.match(r'/connect', self.path)
		if connect_match:
			self._connect_client()
			return

		for url in urlpatterns:
			match = re.match(url[0], self.path)

			# check if match is found
			if match:

				# if method is same, process
				if method == url[1]:
					invalid_method = False

					try:
						data = self._process_POST_data(method)
					except ValueError:
						# Invalid JSON
						self.send_error(400)
						return

					# url[2] is the function referenced in the url to call
					# It is called with the group dictionary from the regex
					# and the unrolled JSON data as keyworded arguments
					# A two-tuple is returned, which is unrolled and passed as
					# arguments to respond
					self.respond(*url[2](match.groupdict(), **data))

					break

				else:
					# Bad method, but valid URL, used for sending 405s
					invalid_method = True

		# Error Handling Below
		# URL found, but not for that method, sending 405 error
		if invalid_method:
			self.send_error(405)
			return

		# no url match found, send 404
		self.send_error(404)
		return

	def do_GET(self):
		"""Handle all GET requests.
		
		On GET request, parse URLs and map them to the API calls."""

		self.match_path("GET")

	def do_POST(self):
		"""Handle all POST requests.
		
		On POST request, parse URLs and map them to the API calls."""

		self.match_path("POST")

	def _process_POST_data(self, method):
		"""Processes the POST data from a request. Private method.

		Reads in a request and returns a dictionary based on whether or not the
		request is a POST request and what POST data the request contains if it
		is.
		
		Throws ValueError on invalid JSON.

		Returns POST data in a dictionary, or empty dictionary on GET.
		"""

		if method == 'POST':
			# POST data should be catured
			length = int(self.headers['Content-Length'])
			input = self.rfile.read(length)
			data = json.loads(input)

		else:
			# GET method, so empty dictionary
			data = {}

		return data

	def _connect_client(self):
		"""Connect a new client to the game.

		When a client attempts to connect we connect them to the game if
		allowed (not already connected, server is not full).
		"""

		print "Connecting client"
		client = global_client_manager.add_client()
		if client is None:
			# Server is full, no connection for you!
			self.respond(403, {'error': 'Server is full'})
			return

		# Prepare the dictionary to send back to the user
		reply = {}
		reply['id'] = client[0]
		reply['auth'] = client[1]
		self._wait_for_game_init(reply)

	def _wait_for_game_init(self, reply):
		"""Wait for the game to start before returning to the client.

		After a client has joined the game, we wait for the game to start
		before sending them back information about the game.
		"""
		# Get the run lock on the client manager
		global_client_manager.game_condition.acquire()
		if global_client_manager.is_full():
			print "Game is full, starting"
			# Start the game and let everyone know we started it
			_start_game()
			global_client_manager.game_condition.notify_all()
			# Release the run lock
			global_client_manager.game_condition.release()
		else:
			print "Game is still not full, waiting on more players"
			# Spin waiting for the server to fill up. This releases the
			# run lock and waits for the game to start
			global_client_manager.game_condition.wait()

		# TODO: Game has started, add any info given in start
		self.respond(200, reply)

	def _validate_client(self, json):
		"""Validate a client's request to proceed.

		Checks with the client manager that a client is who they say they are.
		Kicks anyone out who doesn't meet the bouncer's minimum requirements.
		"""

		if global_client_manager.auth.authorize_client(client_id, token):
			return
		else:
			# Bad call to client, bail us out
			self.respond(401, {'error': 'Bad id or auth code'})

	def _start_game(self):
		init_game()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""A basic threaded HTTP server."""

	# Inheriting from ThreadingMixIn automatically gives us the default
	# functions we need for a threaded server.
	pass
