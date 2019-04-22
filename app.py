from vault import submit_syllabus

section = {
    "semester": "Spring 2019",
    "department": "ANIMA",
    "code": "ANIMA-101-05",
    "title": "Test VAULT API",
    "faculty_string": "Person Two, People McThree",
    "faculty_usernames": "ephetteplace, ahaar"
}
response = submit_syllabus(section, 'syllabus.pdf')

print(response.headers)
print(response.text)
