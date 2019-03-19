import json


class Config:
    def __init__(self, filepath: str):
        """Load the .json from an existent file. Throws if couldn't open/read
        the file"""

        self.filepath = filepath
        self.data = None
        self.load(filepath)

    # IO methods
    def load(self, filepath: str):
        """Load the .json file as a dictionary that Python can work with"""

        with open(filepath) as json_file:
            self.data = json.load(json_file)

    def save(self):
        """Write the changes made in the dictionary to the .json file"""

        with open(self.filepath, 'w') as json_file:
            json.dump(self.data, json_file)

    @property
    def token(self) -> str:
        return self.data['token']

    @property
    def name(self) -> str:
        return self.data['name']

    @property
    def email(self) -> str:
        return self.data['email']

    def get_subsection_names(self, start_route=None):
        subsections = self.data['structure']

        if start_route:
            for route_var in start_route:
                for i, subsection in enumerate(
                    [n['name'] for n in subsections]):
                    if subsection == route_var:
                        subsections = subsections[i]['sections']

        if type(subsections[0]) is dict:
            sections = [n['name'] for n in subsections]

        return sections


cf = Config("config/config.json")

print(cf.token)
print(cf.name)
print(cf.email)

for subsection in cf.get_subsection_names(['ULL']):
    print(subsection)
