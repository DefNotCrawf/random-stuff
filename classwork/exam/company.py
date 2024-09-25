print()


class Employee:
    def __init__(self, name, employee_id):
        self.name = name
        try:
            self.employee_id = employee_id
        except ValueError:
            print("Invalid input")

    def display_info(self):
        print(f"Name: {self.name} \t Employee ID: {self.employee_id}")


class Developer(Employee):
    def __init__(self, name, employee_id, specialisation):
        super().__init__(name, employee_id)
        self.specialisation = specialisation

    def display_info(self):
        print(
            f"Name: {self.name} \t Employee ID: {self.employee_id} \t Specialisation: {self.specialisation}"
        )


class Manager(Employee):
    def __init__(self, name, employee_id, budget):
        super().__init__(name, employee_id)
        try:
            self.budget = budget
        except ValueError:
            print("Invalid input")
        self.subordinates = []

    def display_info(self):
        print(
            f"Name: {self.name} \t Employee ID: {self.employee_id} \t Budget: {self.budget}"
        )

    def add_subordinate(self, employee):
        self.subordinates.append(employee.name)

    def display_subordinates(self):
        print(f"\nSubordinate List:\n", end=" ")
        for per in self.subordinates:
            print(f"\t{per}")


Luke = Developer("Luke", 1234, "Python")
John = Developer("John", 5187, "C++")

Luke.display_info()
John.display_info()

Mark = Manager("Mark", 155115, 1000)

Mark.display_info()
Mark.add_subordinate(Luke)
Mark.add_subordinate(John)
Mark.display_subordinates()
