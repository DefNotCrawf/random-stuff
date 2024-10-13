import sqlite3
from employee import Employee

# conn = sqlite3.connect("sql\\employee.db") # refering to the file in the folder
conn = sqlite3.connect(":memory:")  # for running a database in memory

c = conn.cursor()  # cursor object to interact with the database

c.execute(
    """CREATE TABLE employees (
		first text,		-- first name of the employee
		last text,		-- last name of the employee
		pay integer		-- pay of the employee (integer)
		)"""
)  # creating a table in the database


def insertEmp(emp):  # inserting data into the table
    with conn:
        c.execute(
            "INSERT into employees VALUES (:first, :last, :pay)",
            {
                "first": emp.first,
                "last": emp.last,
                "pay": emp.pay,
            },  # inserting the first name, last name and pay of the employee
        )


def getEmpsByLastName(lastName):  # getting data from the table
    c.execute(
        "SELECT * FROM employees WHERE last=:last", {"last": lastName}
    )  # using the last name to get the employee
    return c.fetchall()


def updatePay(emp, pay):  # updating data (i.e. pay) in the table
    with conn:
        c.execute(
            """UPDATE employees SET pay = :pay
					WHERE first = :first AND last = :last""",  # using the first and last name to update the pay
            {"first": emp.first, "last": emp.last, "pay": pay},
        )


def removeEmp(emp):  # removing data (i.e. an employee) from the table
    with conn:
        c.execute(
            "DELETE from employees WHERE first = :first AND last = :last",
            {
                "first": emp.first,
                "last": emp.last,
            },  # using the first and last name to delete the employee
        )


emp1 = Employee("John", "Doe", 80000)
emp2 = Employee("Jane", "Doe", 90000)

insertEmp(emp1)
insertEmp(emp2)

print(getEmpsByLastName("Doe"))
updatePay(emp2, 95000)
removeEmp(emp1)

print(getEmpsByLastName("Doe"))

conn.close()
