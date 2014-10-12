Installing Apache on Windows Server 2012 with auto-restart
**********************************************************************

..  Note:: Author JA Cole

These instructions are for installing OpenREM under Apache on Windows as 
a developers alternative to the built-in HTTP server. They have been written 
using Windows Server 2012, and feature automatic restarts of the Apache server
when the code changes, much as the built-in server does.

Get and Install Apache
======================
    
+ Download the zip of the appropriate version from https://www.apachelounge.com/
+ Extract the zip somewhere useful. For this guide we will assume ``C:\apache24\``

Get and Install MOD_WSGI
========================

+ Download mod_wsgi that matches your Windows, Apache and Python versions from http://www.lfd.uci.edu/~gohlke/pythonlibs/#mod_wsgi
+ Extract the mod_wsgi.so file to ``C:\apache24\modules\``
+ Add the following module  ``C:\apache24\conf\httpd.conf``::

	LoadModule wsgi_module modules/mod_wsgi.so
	
+ At the end of ``C:\apache24\conf\httpd.conf`` add the following::

	WSGIScriptAlias / "c:/Python27/Lib/site-packages/openrem/openrem/wsgi.py"
	WSGIPythonPath "c:/Python27/Lib/site-packages/openrem"

	<Directory "c:/Python27/Lib/site-packages/openrem/openrem">
	<Files wsgi.py>
	Order deny,allow
	Require all granted
	</Files>cd c:\py	
	</Directory>


Get and Install wsgi.py and monitor.py
======================================

Detailed instructions are available here: https://code.google.com/p/modwsgi/wiki/ReloadingSourceCode

+ Change wsgi.py in the openrem/openrem folder to the following

.. code-block:: python

	"""
	WSGI config for OpenREM project.

	This module contains the WSGI application used by Django's development server
	and any production WSGI deployments. It should expose a module-level variable
	named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
	this application via the ``WSGI_APPLICATION`` setting.

	Usually you will have the standard Django WSGI application here, but it also
	might make sense to replace the whole Django WSGI application with a custom one
	that later delegates to the Django one. For example, you could introduce WSGI
	middleware here, or combine a Django application with an application of another
	framework.

	"""
	import os
	import sys

	path = 'C:/Python27/Lib/site-packages/openrem'
	if path not in sys.path:
        sys.path.append(path)

	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openrem.settings")

	# Apply WSGI middleware here.

	import django.core.handlers.wsgi
	application = django.core.handlers.wsgi.WSGIHandler()

	import openrem.monitor
	openrem.monitor.start(interval=1.0)
	
+ Create a file monitor.py in the openrem/openrem folder with the following contents

.. code-block:: python

	# Code from the modwsgi wiki at https://code.google.com/p/modwsgi/wiki/ReloadingSourceCode
	# Copyright 2007-2011 GRAHAM DUMPLETON
	#
	# Licensed under the Apache License, Version 2.0 (the "License");
	# you may not use this file except in compliance with the License.
	# You may obtain a copy of the License at
	#     http://www.apache.org/licenses/LICENSE-2.0
	# Unless required by applicable law or agreed to in writing, software
	# distributed under the License is distributed on an "AS IS" BASIS,
	# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	# See the License for the specific language governing permissions and
	# limitations under the License.
	#


	import os
	import sys
	import time
	import signal
	import threading
	import atexit
	import Queue

	_interval = 1.0
	_times = {}
	_files = []

	_running = False
	_queue = Queue.Queue()
	_lock = threading.Lock()

	def _restart(path):
	    _queue.put(True)
	    prefix = 'monitor (pid=%d):' % os.getpid()
	    print >> sys.stderr, '%s Change detected to \'%s\'.' % (prefix, path)
	    print >> sys.stderr, '%s Triggering Apache restart.' % prefix
	    import ctypes
	    ctypes.windll.libhttpd.ap_signal_parent(1)

	def _modified(path):
	    try:
	        # If path doesn't denote a file and were previously
	        # tracking it, then it has been removed or the file type
	        # has changed so force a restart. If not previously
	        # tracking the file then we can ignore it as probably
	        # pseudo reference such as when file extracted from a
	        # collection of modules contained in a zip file.

	        if not os.path.isfile(path):
	            return path in _times

	        # Check for when file last modified.

	        mtime = os.stat(path).st_mtime
	        if path not in _times:
	            _times[path] = mtime

	        # Force restart when modification time has changed, even
	        # if time now older, as that could indicate older file
	        # has been restored.
	
	        if mtime != _times[path]:
	            return True
	    except:
	        # If any exception occured, likely that file has been
	        # been removed just before stat(), so force a restart.
	
	        return True
	
	    return False
	
	def _monitor():
	    while 1:
	        # Check modification times on all files in sys.modules.
	
	        for module in sys.modules.values():
	            if not hasattr(module, '__file__'):
	                continue
	            path = getattr(module, '__file__')
	            if not path:
	                continue
	            if os.path.splitext(path)[1] in ['.pyc', '.pyo', '.pyd']:
	                path = path[:-1]
	            if _modified(path):
	                return _restart(path)
	
	        # Check modification times on files which have
	        # specifically been registered for monitoring.
	
	        for path in _files:
	            if _modified(path):
	                return _restart(path)
	
	        # Go to sleep for specified interval.
	
	        try:
	            return _queue.get(timeout=_interval)
	        except:
	            pass

	_thread = threading.Thread(target=_monitor)
	_thread.setDaemon(True)

	def _exiting():
	    try:
	        _queue.put(True)
	    except:
	        pass
	    _thread.join()

	atexit.register(_exiting)

	def track(path):
	    if not path in _files:
	        _files.append(path)

	def start(interval=1.0):
	    global _interval
	    if interval < _interval:
	        _interval = interval

	    global _running
	    _lock.acquire()
	    if not _running:
	        prefix = 'monitor (pid=%d):' % os.getpid()
	        print >> sys.stderr, '%s Starting change monitor.' % prefix
	        _running = True
	        _thread.start()
    	_lock.release()

Install Micosoft C++ Distributable
==================================

Install the microsoft C++ distributable making sure the version number matches the version number for the apache and mod_wsgi downloads.
`<http://www.microsoft.com/en-us/download/details.aspx?id=30679#>`_



Optional: Install apache as a service
=====================================
Run a terminal as administrator.::

    c:\apache24\bin\httpd -k install


Setup the URLs
==============

Add the following to the openrem urls.py file::

	from django.conf import settings
	if settings.DEBUG:
	    urlpatterns += patterns('django.contrib.staticfiles.views',
	        url(r'^static/(?P<path>.*)$', 'serve'),
	    )

Collect the static files
========================

Collect your static files by running::

	python manage.py collectstatic

If this fails because openrem lacks a static folder either copy the static folder from remapp to the openrem directory, adjust the openrem settings or set up a link.
To setup a link run::

	mklink /D c:\python27\lib\site-packages\openrem\static c:\python27\lib\site-packages\openrem\remapp\static
