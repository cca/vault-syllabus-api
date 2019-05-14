from vault import submit_syllabus

section = {
    "semester": "Spring 2019",
    "department": "DSMBA",
    "code": "DSMBA-640-01",
    "title": "Strategic Foresight (test)",
    "faculty_string": "Person Two, People McThree",
    "faculty_usernames": "ephetteplace, ahaar",
    "uploaded_by": "ephetteplace"
}
response = submit_syllabus(section, 'syllabus.pdf')

print(response.headers)
print(response.text)
