setup:
	for pkg in "jsonpickle" "PyRSS2Gen" "jinja2"; do \
	  if ! python -c "import $$pkg"; then sudo -H pip install $$pkg; fi; done
	if ! python -c "import instagram"; then sudo -H pip install python-instagram; fi
