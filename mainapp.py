from dotenv import load_dotenv
import streamlit as st
import os
import mysql.connector
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure GenerativeAI Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Model and provide queries as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text.strip()

# Function to retrieve query from the MySQL database
def read_sql_query(sql):
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows

# Define your prompt
prompt = [
    """
    You are an expert in converting English questions to SQL queries!
    The SQL database has the name 'university' and contains the following tables:
    - `Departments` with columns `DepartmentID`, `DepartmentName`
    - `Students` with columns `StudentID`, `Name`, `Age`, `Gender`, `DepartmentID`
    - `Instructors` with columns `InstructorID`, `Name`, `DepartmentID`
    - `Courses` with columns `CourseID`, `CourseName`, `Credits`, `DepartmentID`
    - `Enrollments` with columns `EnrollmentID`, `StudentID`, `CourseID`, `Grade`
    - `StudentMarks` with columns `StudentID`, `Marks`, `GPA`, `CGPA`
    For example,    
    Example 1 - How many departments are there in the university?
    The SQL command will be something like this: SELECT COUNT(*) FROM Departments;
    Example 2 - List all students in the 'Students' table.
    The SQL command will be something like this: SELECT * FROM Students;
    Example 3 - Retrieve the names and ages of all students.
    The SQL command will be something like this: SELECT Name, Age FROM Students;
    Example 4 - How many courses are available in the 'Courses' table?
    The SQL command will be something like this: SELECT COUNT(*) FROM Courses;
    Example 5 - Find the details of all instructors.
    The SQL command will be something like this: SELECT * FROM Instructors;
    Example 6 - How many students are enrolled in the 'Computer Science' department?
    The SQL command will be something like this: SELECT COUNT(*) FROM Students JOIN Departments ON Students.DepartmentID = Departments.DepartmentID WHERE Departments.DepartmentName = 'Computer Science';
    Example 7 - List the names of students who have a GPA greater than 8.5.
    The SQL command will be something like this: SELECT Name FROM Students JOIN StudentMarks ON Students.StudentID = StudentMarks.StudentID WHERE StudentMarks.GPA > 8.5;
    Example 8 - Retrieve the average GPA and CGPA for each department.
    The SQL command will be something like this: SELECT Departments.DepartmentName, AVG(StudentMarks.GPA) AS AvgGPA, AVG(StudentMarks.CGPA) AS AvgCGPA FROM Students JOIN StudentMarks ON Students.StudentID = StudentMarks.StudentID JOIN Departments ON Students.DepartmentID = Departments.DepartmentID GROUP BY Departments.DepartmentName;
    Example 9 - Find the details of all courses offered by the 'Mathematics' department.
    The SQL command will be something like this: SELECT * FROM Courses JOIN Departments ON Courses.DepartmentID = Departments.DepartmentID WHERE Departments.DepartmentName = 'Mathematics';
    Example 10 - List the names of instructors who teach 'Database Systems'.
    The SQL command will be something like this: SELECT Instructors.Name FROM Instructors JOIN Courses ON Instructors.DepartmentID = Courses.DepartmentID WHERE Courses.CourseName = 'Database Systems';
    Example 11 - Show the names and grades of students enrolled in 'Organic Chemistry'.
    The SQL command will be something like this: SELECT Students.Name, Enrollments.Grade FROM Enrollments JOIN Students ON Enrollments.StudentID = Students.StudentID JOIN Courses ON Enrollments.CourseID = Courses.CourseID WHERE Courses.CourseName = 'Organic Chemistry';
    Example 12 - Get the number of students in each department.
    The SQL command will be something like this: SELECT Departments.DepartmentName, COUNT(Students.StudentID) AS NumberOfStudents FROM Students JOIN Departments ON Students.DepartmentID = Departments.DepartmentID GROUP BY Departments.DepartmentName;
    Example 13 - List the names of all students along with their GPA and CGPA.
    The SQL command will be something like this: SELECT Students.Name, StudentMarks.GPA, StudentMarks.CGPA FROM Students JOIN StudentMarks ON Students.StudentID = StudentMarks.StudentID;
    Example 14 - Retrieve the list of students who have scored marks above 850.
    The SQL command will be something like this: SELECT Students.Name FROM Students JOIN StudentMarks ON Students.StudentID = StudentMarks.StudentID WHERE StudentMarks.Marks > 850;
    Example 15 - Find the courses with the highest number of enrolled students.
    The SQL command will be something like this: SELECT Courses.CourseName, COUNT(Enrollments.StudentID) AS NumberOfStudents FROM Enrollments JOIN Courses ON Enrollments.CourseID = Courses.CourseID GROUP BY Courses.CourseName ORDER BY NumberOfStudents DESC LIMIT 1;
    The SQL code should not have ``` in the beginning or end and the SQL keyword should not be in the output.
    """
]

# Streamlit App
st.set_page_config(page_title="KARTHIK - TextToSQL")

# Custom CSS to set the background color, header colors, and text colors
st.markdown(
    """
    <style>
    .main {
        background-color: #192641;
        color: #ffffff;
    }
    .block-container {
        background-color: #192641;
        color: #ffffff;
    }
    .css-1d391kg {
        background-color: #192641;
        color: #ffffff;
    }
    .css-1b6a68b {
        background-color: #ffffff;
        color: #ffffff;
    }
    .stTextInput input {
        background-color: #ffffff;
        color: #000000;
    }
    .stButton button {
        background-color: #00FF00;
        color: #192641;
    }
    .custom-header {
        color: #ffffff;  /* White color for specific header */
        text-align: center;
        font-size: 2em;
    }

    .custom-subheader {
        color: #ffffff;
        font-size: 1.5em;
        text-align: center;
    }

    .custom-text-input-label {
        color: #ffffff; /* White color for text input label */
    }

    .custom-results {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# JavaScript to change button color after click
st.markdown(
    """
    <script>
    function changeButtonColor() {
        var button = document.querySelector('button[aria-label="Ask the Question"]');
        button.style.backgroundColor = '#FF0000';
    }
    </script>
    """,
    unsafe_allow_html=True
)

# Use a markdown header with a custom class to apply the style
st.markdown('<h1 class="custom-header">Gemini App To Generate Query & Retrieve Data</h1>', unsafe_allow_html=True)

# Apply custom class to text input label using markdown
st.markdown('<div class="custom-text-input-label">Input:</div>', unsafe_allow_html=True)

question = st.text_input("", key="input")

submit = st.button("Ask the Question", on_click=lambda: st.markdown('<script>changeButtonColor()</script>', unsafe_allow_html=True))

# if submit is clicked
if submit:
    response = get_gemini_response(question, prompt)
    
    if response:
        # Retrieve SQL query results
        results = read_sql_query(response)
        
        # Create columns for the query and results
        query_col, results_col = st.columns(2)
        
        with query_col:
            # Add a custom class to your subheader
            st.markdown('<h2 class="custom-subheader">Generated SQL Query</h2>', unsafe_allow_html=True)
            st.code(response, language='sql')
        
        with results_col:
            st.markdown('<h2 class="custom-subheader">Query Results</h2>', unsafe_allow_html=True)
            if results:
                for row in results:
                    st.markdown(f'<div class="custom-results">{row}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-results">No results found.</div>', unsafe_allow_html=True)
    else:
        st.write("No response generated.")
