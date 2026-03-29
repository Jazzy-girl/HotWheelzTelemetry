import cantools
from pprint import pprint

import cantools.database;

PATH = 'Experimentation/ReadingData/TestData/dbcTest.dbc'
db = cantools.database.load_file(PATH)
db.messages
example_message = db.get_message_by_name('ExampleMessage')
pprint(example_message.signals)