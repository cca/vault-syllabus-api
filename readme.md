# VAULT Syllabus API

This is a very small proof-of-concept that adds to VAULT's Syllabus Collection using the openEQUELLA REST APIs.

## Setup

1. Create a Python virtualenv, e.g. `virtualenv -p python3 .`
1. Enter the virtualenv & install dependencies, e.g. `source bin/activate ; pip install -r requirements.txt`
1. Obtain (ask Systems Librarian for it) openEQUELLA OAuth access token with, at a minimum, the `CREATE_ITEM` privilege
1. Copy example.config.json to config.json and add token under `ACCESS_TOKEN`
1. Edit app.py details, for instance changing the syllabus filename or the `section` dict
1. Run `python app.py` & the JSON returned on success links to an API representation of your item

# Data Flow

This app could be the basis for middleware used like so:

1. Faculty member views their course in Portal, uploads a syllabus file using UI
1. Portal `POST`s course metadata\* & file to middleware that's probably on libraries.cca.edu
1. Middleware validates (?), structures the metadata
1. Middleware performs 3-step `POST /api/file` -> `PUT /api/file...` -> `POST /api/item...` process to create new VAULT item

\*Minimum viable metadata per section:

- semester (in "Spring 2019" form)
- department code (five capitalized letters, not necessarily the first five of below)
- section code ("ABCDE-123-12" form)
- course title

VAULT also _wants_ a comma-separated string of instructor names and usernames (they do not need to match or be in the same order) but those are not strictly necessary to create a valid Syllabus Collection item. The usernames make it possible to add the instructor as the owner of the item in VAULT so that they can make edits afterwards and view the item under **My Resources**.

# Questions/Concerns for the future

- Pushing syllabus to _other_ platforms like LMS too
- How/whether to validate course information
    + Already somewhat dealing with this problem by translating department codes

We made a few decisions to solve previous problems, including supporting only a single file per section and supporting uploads _only through Portal_ so that we don't have a situation where a faculty member uploads to VAULT and then we have to communicate that back to Portal. We've also decided that faculty members can update their syllabus in Portal by re-uploading it, in which case we'll just create a totally new item in VAULT. This will create duplicates for some sections but not cause any true problems, plus it will be evident that the latter submission is the updated one.
