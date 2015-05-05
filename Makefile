setup:
	if [ ! -d "python-instagram" ]; then git clone git@github.com:Instagram/python-instagram.git; fi
	if ! python -c "import jsonpickle"; then sudo pip install jsonpickle; fi
