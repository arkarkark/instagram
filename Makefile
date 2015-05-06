setup:
	for pkg in "instagram" "jsonpickle" "PyRSS2Gen" "jinja2"; do \
	  if ! python -c "import $$pkg"; then sudo pip install $$pkg; fi; done
