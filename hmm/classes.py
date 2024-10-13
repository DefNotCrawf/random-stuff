class Person:
    def __init__(self, firstName, lastName):
        self.firstName = firstName
        self.lastName = lastName

    def printFullName(self):
        pass
        # def get_text(self):
        #     return self._text

        # def set_text(self, value):
        #     self._text = value

        # def get_font(self):
        #     return self._font

        # def set_font(self, value):
        #     self._font = value


class Student(Person):
    def __init__(self, firstName, lastName, studentID, homeroom):
        Person.__init__(firstName, lastName)
        try:
            self.studentID = int(studentID)
        except ValueError:
            print(f"'{studentID}' is not a number. Please try again.")
            exit(1)
        self.homeroom = homeroom

    def enrolClass():
        pass


class Subject(Student):
    def __init__(self, studentID, subjectName):

        self.subjectName = subjectName

    def printStudentList(self):
        pass

        # def get_text(self):
        #     return self._text

        # def set_text(self, value):
        #     self._text = value
