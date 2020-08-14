import os


def make_sure_dir_exist(dir_):
	"""
	Make sure the directory exists.

	If `dir_` does not exist, make it. Otherwise do nothing.

	Arguments:

		dir_ (str): path to the directory.
	"""
	if not os.path.isdir(dir_):
		os.makedirs(dir_)


