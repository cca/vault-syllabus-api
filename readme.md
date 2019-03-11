# VAULT Syllabus API

This is a very small proof-of-concept that adds to VAULT's Syllabus Collection using the openEQUELLA REST APIs.

## Setup

1. Create a Python virtualenv, e.g. `virtualenv -p python3 .`
1. Enter the virtualenv & install dependencies, e.g. `source bin/activate ; pip install -r requirements.txt`
1. Obtain openEQUELLA OAuth access token with, at a minimum, the `CREATE_ITEM` privilege
1. Copy example.config.json and add token under `access_token`
1. Edit app.py with any details you'd like, for instance changing the syllabus `filename` or editing the `metadata` section of `data`
1. Run `python app.py` & the JSON returned on success links to an API representation of your item

# Data Flow

This app could be the basis for middleware used like so:

1. Faculty member views their course in Portal, uploads a syllabus file using UI
1. Portal `POST`s course metadata\*, file to middleware that's probably on libraries.cca.edu
1. Middleware validates (?), structures the metadata
1. Middleware performs 3-step `POST /api/file` -> `PUT /api/file...` -> `POST /api/item...` process to create new VAULT item
1. Middleware tells Portal item creation succeeded by returning item's URL (may take a minute)
1. Portal deletes syllabus file & shows faculty member a link to the VAULT syllabus item

\*Minimum viable metadata:

- semester
- department code
- section code (cannot be derived from above)
- course title

VAULT needs much more but the middleware can derive department title, division, "courseName" (e.g. WRITE-600), and "courseinfo" taxonomy string from these starting data. While VAULT _can_ accept items without a comma-separated list of instructor usernames, they would be included as well. This list makes it possible to add the instructor as the owner of the item in VAULT so that they can make edits afterwards and view the item under **My Resources**.

# Questions/Concerns for the future

- How to support multiple files for a section (increases middleware complexity but doable)
- Show in Portal when a syllabus has been uploaded to VAULT through other means to avoid making faculty think they've not completed the task yet (one possibility: make submission through Portal the only way to upload) e.g. with a different API middleware
- How to support modifying syllabus files after an initial upload
- Inevitable confusion that students cannot see syllabus in Portal
- Pushing syllabus to _other_ platforms like LMS too
