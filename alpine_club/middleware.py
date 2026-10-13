from django.db import connections
from django.db.utils import OperationalError
from django.db.shortcuts import render

class DatabaseConnectionMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		try:
			db_conn = connections['default']
			db_conn.cursor()
		except OperationalError:
			return render(request, 'db_error.html', status=503)
		
		response = self.get_response(request)
		return response
