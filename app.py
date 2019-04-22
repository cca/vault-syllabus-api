import json
import sys
import requests

with open('config.json') as f:
    config = json.load(f)

filename = 'syllabus.pdf'

headers = {
    'X-Authorization': 'access_token=' + config["access_token"],
}

# Steps:
# 1) POST /api/file (obtain a file area UUID for next step)
# 2) PUT /api/file/[file area UUID]/content/filename.pdf
# 3) POST /api/item?file=[file area UUID]


# Step 1) File Area

filearea = requests.post(config["api_root"] + "/file", headers=headers)
# example response JSON:
# {'type': 'root', 'filename': '', 'files': [], 'folders': [], 'uuid': '83914a3e-ab74-4534-967c-958f94ec5017', 'links': {'self': 'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/dir', 'dir': 'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/dir', 'content': 'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/content'}}
filearea_uuid = filearea.json()["uuid"]


# Step 2) File Upload
with open(filename, 'rb') as data:
    attachment = requests.put("{}/file/{}/content/{}".format(config["api_root"], filearea_uuid, filename), data=data, headers=headers)
# example response JSON:
# {'type': 'file', 'filename': 'syllabus.pdf', 'size': 911753, 'links': {'self': 'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/dir/syllabus.pdf', 'dir': 'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/dir/syllabus.pdf', 'content': 'https://vault.cca.edu/api/file/83914a3e-ab74-4534-967c-958f94ec5017/content/syllabus.pdf'}}


# Step 3) Item Upload

# metadata XML spaced for readability purposes
# NOTE: uuid:[temp ID] is a special function that will be replaced with the
# attachment's UUID once it's generated (we don't know it until it's attached
# to an item)
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
        "uuid": config["collection_uuid"]
    },
    "metadata": """<xml>
        <local>
            <courseInfo>
                <semester>Spring 2019</semester>
                <department>TESTS</department>
                <course>Test Course</course>
                <faculty>Eric Phetteplace</faculty>
                <section>WRITE-600-02</section>
                <courseName>WRITE-600</courseName>
                <facultyID>ephetteplace</facultyID>
                <courseinfo>Spring 2019\\TESTS\\Test Course\\Eric Phetteplace\\WRITE-600-02</courseinfo>
            </courseInfo>
            <department>Writing (MFA)</department>
            <division>Humanities &amp; Sciences Division</division>
        </local>
        <mods>
            <part>
                <number>uuid:{}</number>
            </part>
            <titleInfo>
                <title>Spring 2019 | WRITE-600 | Test Course</title>
            </titleInfo>
        </mods>
    </xml>""".format(filename),
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
response = requests.post(config["api_root"] + '/item?file=' + filearea_uuid, data=json.dumps(data), headers=headers)

print(response.headers)
print(response.text)
