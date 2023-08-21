import importlib.util

### Version stuff
class Version:
    def __init__(self, commit = '', date = '', dirty = 0):
        self.commit = commit
        self.date = date
        self.dirty = dirty
    def to_string(self):
        return f'Commit: {self.commit} Date: {self.date} Dirty: { "Yes" if (self.dirty) else "No" }' if (len(self.commit) > 0) else 'Version N/A'
    def to_dict(self):
        return { 'commit' : self.commit,  'date' : self.date, 'dirty': self.dirty } if (len(self.commit) > 0) else {}

version_obj = Version()
if (importlib.util.find_spec('version') is not None):
    version_module = importlib.import_module('version')
    version_obj = Version(version_module.git_commit, version_module.git_date, version_module.git_dirty)

def get_version():
    return version_obj
### End version stuff
