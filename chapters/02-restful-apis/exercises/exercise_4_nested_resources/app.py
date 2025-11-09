"""
Exercise 4: Nested Resources - School Management API

OBJECTIVE:
Design and implement properly nested resources showing parent-child relationships.

WHAT YOU'LL BUILD:
- Multi-level resource hierarchy (Schools → Classes → Students → Grades)
- Nested endpoints for related resources
- Parent resource validation
- Cascading operations
- Alternative flat endpoints for convenience

LEARNING GOALS:
- Hierarchical resource design
- Parent-child relationship validation
- When to nest vs when to keep flat
- URL structure for nested resources
- Cascading deletes and updates

RESOURCE HIERARCHY:
Schools
  └── Classes
        └── Students
              └── Grades

TODO CHECKLIST:
[ ] Implement Schools endpoints (GET, POST, DELETE)
[ ] Implement Classes nested under Schools
[ ] Implement Students nested under Classes
[ ] Implement Grades nested under Students
[ ] Validate parent resources exist before creating children
[ ] Implement cascading deletes (deleting school deletes classes and students)
[ ] Add flat alternative endpoints for convenience
[ ] Auto-update student counts
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
from datetime import datetime

def create_app():
    """
    Create the School Management API.

    This API demonstrates nested resources and hierarchical design.
    """
    app = Flask(__name__)
    CORS(app)

    api = Api(
        app,
        version='4.0',
        title='School Management API',
        description='Exercise 4: Master Nested Resources',
        doc='/swagger'
    )

    # ============================================================================
    # DATA MODELS
    # ============================================================================

    schools_ns = Namespace('schools', description='School operations')

    school_model = schools_ns.model('School', {
        'id': fields.Integer(readonly=True, description='School ID'),
        'name': fields.String(required=True, description='School name'),
        'address': fields.String(required=True, description='School address'),
        'principal': fields.String(description='Principal name'),
        'student_count': fields.Integer(description='Total students')
    })

    class_model = schools_ns.model('Class', {
        'id': fields.Integer(readonly=True, description='Class ID'),
        'school_id': fields.Integer(required=True, description='School ID'),
        'name': fields.String(required=True, description='Class name'),
        'subject': fields.String(required=True, description='Subject taught'),
        'teacher': fields.String(required=True, description='Teacher name'),
        'student_count': fields.Integer(description='Number of students')
    })

    student_model = schools_ns.model('Student', {
        'id': fields.Integer(readonly=True, description='Student ID'),
        'class_id': fields.Integer(required=True, description='Class ID'),
        'school_id': fields.Integer(required=True, description='School ID'),
        'name': fields.String(required=True, description='Student name'),
        'email': fields.String(required=True, description='Student email'),
        'enrollment_date': fields.String(description='Enrollment date'),
        'gpa': fields.Float(description='Grade Point Average')
    })

    grade_model = schools_ns.model('Grade', {
        'id': fields.Integer(readonly=True, description='Grade ID'),
        'student_id': fields.Integer(required=True, description='Student ID'),
        'subject': fields.String(required=True, description='Subject'),
        'grade': fields.String(required=True, description='Letter grade'),
        'score': fields.Float(required=True, description='Numeric score'),
        'date': fields.String(description='Grade date')
    })

    # ============================================================================
    # IN-MEMORY DATA STORAGE
    # ============================================================================

    schools = [
        {
            'id': 1,
            'name': 'Lincoln High School',
            'address': '123 Main St',
            'principal': 'Dr. Sarah Smith',
            'student_count': 2
        }
    ]

    classes = [
        {
            'id': 1,
            'school_id': 1,
            'name': 'Grade 10A',
            'subject': 'Mathematics',
            'teacher': 'Mr. Johnson',
            'student_count': 2
        }
    ]

    students = [
        {
            'id': 1,
            'class_id': 1,
            'school_id': 1,
            'name': 'Alice Wilson',
            'email': 'alice@example.com',
            'enrollment_date': '2024-01-15',
            'gpa': 3.8
        },
        {
            'id': 2,
            'class_id': 1,
            'school_id': 1,
            'name': 'Bob Chen',
            'email': 'bob@example.com',
            'enrollment_date': '2024-01-15',
            'gpa': 3.6
        }
    ]

    grades = [
        {
            'id': 1,
            'student_id': 1,
            'subject': 'Math',
            'grade': 'A',
            'score': 95.0,
            'date': '2024-03-01'
        }
    ]

    # ============================================================================
    # HELPER FUNCTIONS
    # ============================================================================

    def find_school_by_id(school_id):
        """Find school by ID."""
        # TODO: Implement this helper
        pass

    def find_class_by_id(class_id):
        """Find class by ID."""
        # TODO: Implement this helper
        pass

    def find_student_by_id(student_id):
        """Find student by ID."""
        # TODO: Implement this helper
        pass

    def find_grade_by_id(grade_id):
        """Find grade by ID."""
        # TODO: Implement this helper
        pass

    def get_classes_for_school(school_id):
        """Get all classes belonging to a school."""
        # TODO: Return list of classes where class['school_id'] == school_id
        pass

    def get_students_for_class(class_id):
        """Get all students in a class."""
        # TODO: Return list of students where student['class_id'] == class_id
        pass

    def get_grades_for_student(student_id):
        """Get all grades for a student."""
        # TODO: Return list of grades where grade['student_id'] == student_id
        pass

    def update_class_student_count(class_id):
        """Update student count for a class."""
        # TODO: Count students in this class and update class['student_count']
        # HINT: Find the class, count students with matching class_id
        pass

    def update_school_student_count(school_id):
        """Update total student count for a school."""
        # TODO: Count all students in all classes of this school
        # HINT: Get all classes for school, then count students with matching school_id
        pass

    def validate_parent_child_relationship(school_id, class_id):
        """
        Validate that a class belongs to a school.

        TODO: Implement relationship validation
        STEPS:
        1. Find the class by class_id
        2. Check if class['school_id'] == school_id
        3. Return True if match, False otherwise

        WHY?: For nested endpoints like /schools/{school_id}/classes/{class_id}/students,
        we need to verify the class actually belongs to that school.
        """
        # TODO: Implement validation
        pass

    # ============================================================================
    # SCHOOLS ENDPOINTS
    # ============================================================================

    @schools_ns.route('/')
    class SchoolList(Resource):
        """Schools collection."""

        @schools_ns.doc('list_schools')
        @schools_ns.marshal_list_with(school_model)
        def get(self):
            """List all schools."""
            # TODO: Return schools list
            pass

        @schools_ns.doc('create_school')
        @schools_ns.expect(school_model)
        @schools_ns.marshal_with(school_model, code=201)
        def post(self):
            """
            Create a new school.

            TODO: Implement school creation
            STEPS:
            1. Get request data
            2. Validate required fields (name, address)
            3. Generate new ID
            4. Set student_count to 0
            5. Add to schools list
            6. Return school with 201
            """
            # TODO: Implement POST /schools
            pass

    @schools_ns.route('/<int:school_id>')
    @schools_ns.param('school_id', 'School identifier')
    class SchoolItem(Resource):
        """Single school."""

        @schools_ns.doc('get_school')
        @schools_ns.marshal_with(school_model)
        def get(self, school_id):
            """Get school by ID."""
            # TODO: Find school, return 404 if not found
            pass

        @schools_ns.doc('delete_school')
        @schools_ns.response(204, 'School deleted')
        def delete(self, school_id):
            """
            Delete school and cascade to classes and students.

            TODO: Implement cascading delete
            STEPS:
            1. Find school (404 if not found)
            2. Get all classes in this school
            3. For each class, delete all students in that class
            4. Delete all classes in this school
            5. Delete the school
            6. Return 204

            CASCADING DELETE: When you delete a school, all related
            classes and students should also be deleted.
            """
            # TODO: Implement DELETE /schools/{id} with cascade
            pass

    # ============================================================================
    # CLASSES ENDPOINTS (Nested under Schools)
    # ============================================================================

    @schools_ns.route('/<int:school_id>/classes')
    @schools_ns.param('school_id', 'School identifier')
    class ClassList(Resource):
        """Classes in a school."""

        @schools_ns.doc('list_classes_in_school')
        @schools_ns.marshal_list_with(class_model)
        def get(self, school_id):
            """
            List all classes in a school.

            TODO: Implement nested GET
            STEPS:
            1. Verify school exists (404 if not)
            2. Get all classes for this school
            3. Return classes list
            """
            # TODO: Implement GET /schools/{school_id}/classes
            pass

        @schools_ns.doc('create_class_in_school')
        @schools_ns.expect(class_model)
        @schools_ns.marshal_with(class_model, code=201)
        def post(self, school_id):
            """
            Create a class in a school.

            TODO: Implement nested POST
            STEPS:
            1. Verify school exists (404 if not) - PARENT VALIDATION
            2. Get request data
            3. Validate required fields (name, subject, teacher)
            4. Generate new ID
            5. Set school_id from URL parameter
            6. Set student_count to 0
            7. Add to classes list
            8. Return class with 201

            KEY CONCEPT: We automatically set school_id from the URL,
            ensuring the class belongs to the correct school.
            """
            # TODO: Implement POST /schools/{school_id}/classes
            pass

    @schools_ns.route('/<int:school_id>/classes/<int:class_id>')
    @schools_ns.param('school_id', 'School identifier')
    @schools_ns.param('class_id', 'Class identifier')
    class ClassItem(Resource):
        """Single class in a school."""

        @schools_ns.doc('get_class')
        @schools_ns.marshal_with(class_model)
        def get(self, school_id, class_id):
            """
            Get a specific class.

            TODO: Implement nested GET with validation
            STEPS:
            1. Verify school exists (404 if not)
            2. Find class (404 if not found)
            3. Verify class belongs to school (404 if mismatch)
            4. Return class

            VALIDATION: We check that the class actually belongs to
            the specified school, preventing access to /schools/1/classes/999
            if class 999 belongs to school 2.
            """
            # TODO: Implement GET /schools/{school_id}/classes/{class_id}
            pass

        @schools_ns.doc('update_class')
        @schools_ns.expect(class_model)
        @schools_ns.marshal_with(class_model)
        def put(self, school_id, class_id):
            """
            Update a class.

            TODO: Implement nested PUT
            HINT: Similar to GET but update fields
            HINT: Validate parent-child relationship
            """
            # TODO: Implement PUT /schools/{school_id}/classes/{class_id}
            pass

        @schools_ns.doc('delete_class')
        @schools_ns.response(204, 'Class deleted')
        def delete(self, school_id, class_id):
            """
            Delete a class and its students.

            TODO: Implement delete with cascade
            STEPS:
            1. Verify school exists
            2. Find class and verify it belongs to school
            3. Delete all students in this class
            4. Delete the class
            5. Update school's student count
            6. Return 204
            """
            # TODO: Implement DELETE /schools/{school_id}/classes/{class_id}
            pass

    # ============================================================================
    # STUDENTS ENDPOINTS (Nested under Classes)
    # ============================================================================

    @schools_ns.route('/<int:school_id>/classes/<int:class_id>/students')
    @schools_ns.param('school_id', 'School identifier')
    @schools_ns.param('class_id', 'Class identifier')
    class StudentList(Resource):
        """Students in a class."""

        @schools_ns.doc('list_students_in_class')
        @schools_ns.marshal_list_with(student_model)
        def get(self, school_id, class_id):
            """
            List all students in a class.

            TODO: Implement triple-nested GET
            STEPS:
            1. Verify school exists
            2. Verify class exists and belongs to school
            3. Get all students in this class
            4. Return students list
            """
            # TODO: Implement GET /schools/{school_id}/classes/{class_id}/students
            pass

        @schools_ns.doc('create_student')
        @schools_ns.expect(student_model)
        @schools_ns.marshal_with(student_model, code=201)
        def post(self, school_id, class_id):
            """
            Enroll a student in a class.

            TODO: Implement triple-nested POST
            STEPS:
            1. Verify school exists
            2. Verify class exists and belongs to school
            3. Get request data
            4. Validate required fields (name, email)
            5. Generate new ID
            6. Set school_id and class_id from URL
            7. Set enrollment_date to today
            8. Add to students list
            9. Update class student count
            10. Update school student count
            11. Return student with 201
            """
            # TODO: Implement POST /schools/{school_id}/classes/{class_id}/students
            pass

    @schools_ns.route('/<int:school_id>/classes/<int:class_id>/students/<int:student_id>')
    @schools_ns.param('school_id', 'School identifier')
    @schools_ns.param('class_id', 'Class identifier')
    @schools_ns.param('student_id', 'Student identifier')
    class StudentItem(Resource):
        """Single student."""

        @schools_ns.doc('get_student')
        @schools_ns.marshal_with(student_model)
        def get(self, school_id, class_id, student_id):
            """
            Get a student.

            TODO: Implement with full hierarchy validation
            """
            # TODO: Implement GET /schools/{school_id}/classes/{class_id}/students/{student_id}
            pass

        @schools_ns.doc('delete_student')
        @schools_ns.response(204, 'Student deleted')
        def delete(self, school_id, class_id, student_id):
            """
            Delete a student.

            TODO: Implement delete with count updates
            STEPS:
            1. Validate hierarchy (school → class → student)
            2. Delete student's grades
            3. Delete student
            4. Update class student count
            5. Update school student count
            6. Return 204
            """
            # TODO: Implement DELETE /schools/{school_id}/classes/{class_id}/students/{student_id}
            pass

    # ============================================================================
    # GRADES ENDPOINTS (Nested under Students)
    # ============================================================================

    @schools_ns.route('/<int:school_id>/classes/<int:class_id>/students/<int:student_id>/grades')
    @schools_ns.param('school_id', 'School identifier')
    @schools_ns.param('class_id', 'Class identifier')
    @schools_ns.param('student_id', 'Student identifier')
    class GradeList(Resource):
        """Grades for a student."""

        @schools_ns.doc('list_student_grades')
        @schools_ns.marshal_list_with(grade_model)
        def get(self, school_id, class_id, student_id):
            """
            Get all grades for a student.

            TODO: Implement 4-level nested GET
            """
            # TODO: Implement GET /schools/{school_id}/classes/{class_id}/students/{student_id}/grades
            pass

        @schools_ns.doc('create_grade')
        @schools_ns.expect(grade_model)
        @schools_ns.marshal_with(grade_model, code=201)
        def post(self, school_id, class_id, student_id):
            """
            Add a grade for a student.

            TODO: Implement 4-level nested POST
            """
            # TODO: Implement POST /schools/{school_id}/classes/{class_id}/students/{student_id}/grades
            pass

    # ============================================================================
    # FLAT ALTERNATIVE ENDPOINTS (For convenience)
    # ============================================================================

    # Sometimes nested URLs are too long. Provide flat alternatives for common queries.

    students_flat_ns = Namespace('students', description='Student operations (flat)')

    @students_flat_ns.route('/<int:id>')
    @students_flat_ns.param('id', 'Student identifier')
    class StudentFlat(Resource):
        """
        Flat student endpoint (alternative to nested).

        WHY?: /schools/1/classes/2/students/3 is very long.
        Sometimes you just want /students/3
        """

        @students_flat_ns.doc('get_student_flat')
        @students_flat_ns.marshal_with(student_model)
        def get(self, id):
            """
            Get student by ID (flat endpoint).

            TODO: Simply find and return student by ID
            BENEFIT: Shorter URL when you already know the student ID
            """
            # TODO: Implement GET /students/{id}
            pass

    @students_flat_ns.route('/<int:id>/grades')
    @students_flat_ns.param('id', 'Student identifier')
    class StudentGradesFlat(Resource):
        """Get grades without full hierarchy."""

        @students_flat_ns.doc('get_student_grades_flat')
        @students_flat_ns.marshal_list_with(grade_model)
        def get(self, id):
            """
            Get all grades for a student (flat).

            TODO: Verify student exists, then return grades
            BENEFIT: /students/3/grades is much shorter than the nested version
            """
            # TODO: Implement GET /students/{id}/grades
            pass

    # ============================================================================
    # REGISTER NAMESPACES
    # ============================================================================

    api.add_namespace(schools_ns, path='/schools')
    api.add_namespace(students_flat_ns, path='/students')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*70)
    print("SCHOOL MANAGEMENT API - Exercise 4: Nested Resources")
    print("="*70)
    print("📚 Learning Objectives:")
    print("  - Design hierarchical resource relationships")
    print("  - Implement nested endpoints")
    print("  - Validate parent-child relationships")
    print("  - Implement cascading deletes")
    print("  - Provide flat alternatives for convenience")
    print("\n🏗️  Resource Hierarchy:")
    print("  Schools")
    print("    └── Classes")
    print("          └── Students")
    print("                └── Grades")
    print("\n🎯 Nested vs Flat Endpoints:")
    print("  Nested:  POST /schools/1/classes/2/students")
    print("  Flat:    GET  /students/3")
    print("\n💡 Key Concepts:")
    print("  - Nested URLs show relationships clearly")
    print("  - Always validate parent resources exist")
    print("  - Cascading deletes maintain data integrity")
    print("  - Flat endpoints provide convenience when needed")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
