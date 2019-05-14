import json
import sys
from xml.sax.saxutils import escape

import requests

# in a Django app these would be replaced with a dict of settings named VAULT
with open('config.json') as f:
    settings = json.load(f)


def submit_syllabus(section, filename):
    """ Submit a syllabus to VAULT using its REST API.

    Args:
        section: a dict of all necessary course information, of form:
        { "semester": "Spring 2019", "department": "ANIMA", "code": "ANIMA-101-05",
        "title": "Animation 1", "faculty_string": "Person Two, People McThree",
        "faculty_usernames": "ptwo, pmcthree"}
            It is better to supply empty strings or placeholder data than to leave
            anything null, but ideally we would have every piece of data.
        filename: a string of the path to the syllabus file to be uploaded

    Returns:
        An HTTP response object from VAULT. If successful, the body will be empty
        and the HTTP headers will be similar to this:
        {'Date': 'Mon, 22 Apr 2019 18:11:53 GMT', 'Server': 'Apache-Coyote/1.1',
        ...
        'Content-Length': '0', 'Connection': 'close', 'Location':
        'https://vault.cca.edu/api/item/4f7e3993-dc9d-41fb-81cc-e546b2f7e6ee/1/' }

        Note that the "Location" header is the API URL for the newly created
        item. A link to the item's web page within VAULT can be obtained by
        removing the "/api" portion from this URL's path:
        https://vault.cca.edu/item/4f7e3993-dc9d-41fb-81cc-e546b2f7e6ee/1/

        If unsuccessful, the body will be JSON describing the error, for instance:
        { "code":500, "error":"Internal Server Error",
          "error_description":"Error parsing XML" }

    Raises:
        Any of the HTTP exceptions from requests might be raised:
        https://2.python-requests.org/en/master/_modules/requests/exceptions/
    """
    headers = {
        'X-Authorization': 'access_token=' + settings["ACCESS_TOKEN"],
    }

    # Steps to contributing an item via the openEQUELLA REST API:
    # 1) POST /api/file (obtain a file area UUID for the next step)
    # 2) PUT /api/file/[file area UUID]/content/filename.pdf
    # 3) POST /api/item?file=[file area UUID]

    # Step 1) File Area
    filearea = requests.post(settings["API_ROOT"] + "/file", headers=headers)
    """ example response JSON:
    { 'type': 'root', 'filename': '', 'files': [], 'folders': [], 'uuid':
    '83914a3e-ab74-4534-967c-958f94ec5017', 'links': { 'self'
    'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/dir',
    'dir': 'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/dir',
    'content':
    'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/content' } }
    """
    filearea_uuid = filearea.json()["uuid"]

    # Step 2) File Upload
    with open(filename, 'rb') as data:
        attachment = requests.put("{}/file/{}/content/{}"
            .format(settings["API_ROOT"], filearea_uuid, filename),
            data=data, headers=headers)
    """ example response JSON:
     { 'type': 'file', 'filename': 'syllabus.pdf', 'size': 911753, 'links':
     { 'self': 'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/dir/syllabus.pdf',
     'dir': 'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/dir/syllabus.pdf',
     'content': 'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/content/syllabus.pdf' } }
     """

    """ Step 3) Item Upload

    metadata XML is spaced just for readability
    NOTE: uuid:[temp ID] is a special function that will be replaced with the
    attachment's UUID once it's generated (we don't know it until it's attached
    to an item)
    """
    strings = section
    strings["filename"] = filename
    strings["course_name"] = section["code"][:9]
    # escape everything
    strings = { key: escape(value) for key, value in strings.items() }
    data = {
        "attachments": [
            {
                "type": "file",
                "description": filename,
                "filename": filename,
                "uuid": "uuid:" + filename,
            }
        ],
        "collection": {
            "uuid": settings["SYLLABUS_COLLECTION_UUID"]
        },
        # note that VAULT's expert save script constructs mods/title/titleInfo,
        # local/department, and local/division fields
        "metadata": """<xml>
            <local>
                <courseInfo>
                    <semester>{semester}</semester>
                    <department>{department}</department>
                    <course>{title}</course>
                    <faculty>{faculty_string}</faculty>
                    <section>{code}</section>
                    <courseName>{course_name}</courseName>
                    <facultyID>{faculty_usernames}</facultyID>
                    <courseinfo>{semester}\\{department}\\{title}\\{faculty_string}\\{code}</courseinfo>
                </courseInfo>
            </local>
            <mods>
                <part>
                    <number>uuid:{filename}</number>
                </part>
            </mods>
        </xml>""".format(**strings),
        "navigation": {
          "hideUnreferencedAttachments": False,
          "showSplitOption": False,
          "nodes": [
            {
                "name": "Node 1",
                "tabs": [
                    {
                        "name": "Tab 1",
                        "attachment": { "$ref": "uuid:" + filename, }
                    },
                ],
            },
          ],
        },
    }

    # this is necessary or EQUELLA throws an Unsupported Media Type error
    headers["Content-Type"] = 'application/json'
    response = requests.post(settings["API_ROOT"] + '/item?file=' + filearea_uuid,
        data=json.dumps(data), headers=headers)

    return response
