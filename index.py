#!C:/Python35/python.exe
from wsgiref.handlers import CGIHandler
import application

CGIHandler().run(application.app)
