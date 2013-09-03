def _format_path(self, path):
    """returns a reduced path"""
    newpath = path.replace(self._librarypath, "")
    if newpath[0] == "/":
        return newpath[1:]
    else:
        return newpath
