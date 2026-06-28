from pydantic import BaseModel


class StudentImportItem(BaseModel):
    student_no: str
    name: str
    phone: str
    college: str
    major: str
    grade: str
    class_name: str
    dormitory: str
    dormitory_longitude: float | None = None
    dormitory_latitude: float | None = None
    dormitory_address: str | None = None
    internship_company: str | None = None
    internship_longitude: float | None = None
    internship_latitude: float | None = None
    internship_address: str | None = None
    password: str | None = None


class StudentImportRequest(BaseModel):
    students: list[StudentImportItem]


class TeacherImportItem(BaseModel):
    teacher_no: str
    name: str
    phone: str | None = None
    department: str | None = None


class TeacherImportRequest(BaseModel):
    teachers: list[TeacherImportItem]


class GroupImportItem(BaseModel):
    name: str
    group_type: str = "class"


class GroupImportRequest(BaseModel):
    groups: list[GroupImportItem]


class RuleTemplateUpdateRequest(BaseModel):
    name: str
    rules_snapshot: dict
