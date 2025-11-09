"""
Exercise 4: Nested Resources - School Management API - SOLUTION

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
        for school in schools:
            if school['id'] == school_id:
                return school
        return None

    def find_class_by_id(class_id):
        """Find class by ID."""
        for cls in classes:
            if cls['id'] == class_id:
                return cls
        return None

    def find_student_by_id(student_id):
        """Find student by ID."""
        for student in students:
            if student['id'] == student_id:
                return student
        return None

    def find_grade_by_id(grade_id):
        """Find grade by ID."""
        for grade in grades:
            if grade['id'] == grade_id:
                return grade
        return None

    def get_classes_for_school(school_id):
        """Get all classes belonging to a school."""
        return [cls for cls in classes if cls['school_id'] == school_id]

    def get_students_for_class(class_id):
        """Get all students in a class."""
        return [student for student in students if student['class_id'] == class_id]

    def get_grades_for_student(student_id):
        """Get all grades for a student."""
        return [grade for grade in grades if grade['student_id'] == student_id]

    def update_class_student_count(class_id):
        """Update student count for a class."""
        cls = find_class_by_id(class_id)
        if cls:
            cls['student_count'] = len(get_students_for_class(class_id))

    def update_school_student_count(school_id):
        """Update total student count for a school."""
        school = find_school_by_id(school_id)
        if school:
            # Count all students in all classes of this school
            total = len([s for s in students if s['school_id'] == school_id])
            school['student_count'] = total

    def validate_parent_child_relationship(school_id, class_id):
        """
        Validate that a class belongs to a school.

        WHY?: For nested endpoints like /schools/{school_id}/classes/{class_id}/students,
        we need to verify the class actually belongs to that school.
        """
        cls = find_class_by_id(class_id)
        if not cls:
            return False
        return cls['school_id'] == school_id

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
            return schools

        @schools_ns.doc('create_school')
        @schools_ns.expect(school_model)
        @schools_ns.marshal_with(school_model, code=201)
        def post(self):
            """
            Create a new school.
            """
            data = request.json

            # Validate required fields
            if 'name' not in data or 'address' not in data:
                return {'error': 'Missing required fields: name and address'}, 400

            # Generate new ID
            new_id = max([s['id'] for s in schools], default=0) + 1

            # Create school
            school = {
                'id': new_id,
                'name': data['name'],
                'address': data['address'],
                'principal': data.get('principal', ''),
                'student_count': 0
            }

            schools.append(school)
            return school, 201

    @schools_ns.route('/<int:school_id>')
    @schools_ns.param('school_id', 'School identifier')
    class SchoolItem(Resource):
        """Single school."""

        @schools_ns.doc('get_school')
        @schools_ns.marshal_with(school_model)
        def get(self, school_id):
            """Get school by ID."""
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404
            return school

        @schools_ns.doc('delete_school')
        @schools_ns.response(204, 'School deleted')
        def delete(self, school_id):
            """
            Delete school and cascade to classes and students.

            CASCADING DELETE: When you delete a school, all related
            classes and students should also be deleted.
            """
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            # Get all classes in this school
            school_classes = get_classes_for_school(school_id)

            # For each class, delete all students and grades
            for cls in school_classes:
                # Delete all students in this class
                class_students = get_students_for_class(cls['id'])
                for student in class_students:
                    # Delete all grades for this student
                    student_grades = get_grades_for_student(student['id'])
                    for grade in student_grades:
                        grades.remove(grade)
                    # Delete student
                    students.remove(student)

                # Delete the class
                classes.remove(cls)

            # Delete the school
            schools.remove(school)
            return '', 204

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
            """
            # Verify school exists
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            # Get all classes for this school
            return get_classes_for_school(school_id)

        @schools_ns.doc('create_class_in_school')
        @schools_ns.expect(class_model)
        @schools_ns.marshal_with(class_model, code=201)
        def post(self, school_id):
            """
            Create a class in a school.

            KEY CONCEPT: We automatically set school_id from the URL,
            ensuring the class belongs to the correct school.
            """
            # Verify school exists (PARENT VALIDATION)
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            data = request.json

            # Validate required fields
            required = ['name', 'subject', 'teacher']
            if not all(field in data for field in required):
                return {'error': 'Missing required fields: name, subject, teacher'}, 400

            # Generate new ID
            new_id = max([c['id'] for c in classes], default=0) + 1

            # Create class
            cls = {
                'id': new_id,
                'school_id': school_id,  # Set from URL
                'name': data['name'],
                'subject': data['subject'],
                'teacher': data['teacher'],
                'student_count': 0
            }

            classes.append(cls)
            return cls, 201

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

            VALIDATION: We check that the class actually belongs to
            the specified school, preventing access to /schools/1/classes/999
            if class 999 belongs to school 2.
            """
            # Verify school exists
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            # Find class
            cls = find_class_by_id(class_id)
            if not cls:
                return {'error': 'Class not found'}, 404

            # Verify class belongs to school
            if not validate_parent_child_relationship(school_id, class_id):
                return {'error': 'Class does not belong to this school'}, 404

            return cls

        @schools_ns.doc('update_class')
        @schools_ns.expect(class_model)
        @schools_ns.marshal_with(class_model)
        def put(self, school_id, class_id):
            """
            Update a class.
            """
            # Verify school exists
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            # Find class
            cls = find_class_by_id(class_id)
            if not cls:
                return {'error': 'Class not found'}, 404

            # Verify class belongs to school
            if not validate_parent_child_relationship(school_id, class_id):
                return {'error': 'Class does not belong to this school'}, 404

            data = request.json

            # Update fields
            if 'name' in data:
                cls['name'] = data['name']
            if 'subject' in data:
                cls['subject'] = data['subject']
            if 'teacher' in data:
                cls['teacher'] = data['teacher']

            return cls

        @schools_ns.doc('delete_class')
        @schools_ns.response(204, 'Class deleted')
        def delete(self, school_id, class_id):
            """
            Delete a class and its students.
            """
            # Verify school exists
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            # Find class and verify it belongs to school
            cls = find_class_by_id(class_id)
            if not cls:
                return {'error': 'Class not found'}, 404

            if not validate_parent_child_relationship(school_id, class_id):
                return {'error': 'Class does not belong to this school'}, 404

            # Delete all students in this class
            class_students = get_students_for_class(class_id)
            for student in class_students:
                # Delete all grades for this student
                student_grades = get_grades_for_student(student['id'])
                for grade in student_grades:
                    grades.remove(grade)
                # Delete student
                students.remove(student)

            # Delete the class
            classes.remove(cls)

            # Update school's student count
            update_school_student_count(school_id)

            return '', 204

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
            """
            # Verify school exists
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            # Verify class exists and belongs to school
            cls = find_class_by_id(class_id)
            if not cls:
                return {'error': 'Class not found'}, 404

            if not validate_parent_child_relationship(school_id, class_id):
                return {'error': 'Class does not belong to this school'}, 404

            # Get all students in this class
            return get_students_for_class(class_id)

        @schools_ns.doc('create_student')
        @schools_ns.expect(student_model)
        @schools_ns.marshal_with(student_model, code=201)
        def post(self, school_id, class_id):
            """
            Enroll a student in a class.
            """
            # Verify school exists
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            # Verify class exists and belongs to school
            cls = find_class_by_id(class_id)
            if not cls:
                return {'error': 'Class not found'}, 404

            if not validate_parent_child_relationship(school_id, class_id):
                return {'error': 'Class does not belong to this school'}, 404

            data = request.json

            # Validate required fields
            if 'name' not in data or 'email' not in data:
                return {'error': 'Missing required fields: name and email'}, 400

            # Generate new ID
            new_id = max([s['id'] for s in students], default=0) + 1

            # Create student
            student = {
                'id': new_id,
                'class_id': class_id,  # Set from URL
                'school_id': school_id,  # Set from URL
                'name': data['name'],
                'email': data['email'],
                'enrollment_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'gpa': data.get('gpa', 0.0)
            }

            students.append(student)

            # Update counts
            update_class_student_count(class_id)
            update_school_student_count(school_id)

            return student, 201

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
            """
            # Validate hierarchy
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            cls = find_class_by_id(class_id)
            if not cls:
                return {'error': 'Class not found'}, 404

            if not validate_parent_child_relationship(school_id, class_id):
                return {'error': 'Class does not belong to this school'}, 404

            student = find_student_by_id(student_id)
            if not student:
                return {'error': 'Student not found'}, 404

            # Verify student belongs to this class
            if student['class_id'] != class_id:
                return {'error': 'Student does not belong to this class'}, 404

            return student

        @schools_ns.doc('delete_student')
        @schools_ns.response(204, 'Student deleted')
        def delete(self, school_id, class_id, student_id):
            """
            Delete a student.
            """
            # Validate hierarchy
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            cls = find_class_by_id(class_id)
            if not cls:
                return {'error': 'Class not found'}, 404

            if not validate_parent_child_relationship(school_id, class_id):
                return {'error': 'Class does not belong to this school'}, 404

            student = find_student_by_id(student_id)
            if not student:
                return {'error': 'Student not found'}, 404

            if student['class_id'] != class_id:
                return {'error': 'Student does not belong to this class'}, 404

            # Delete student's grades
            student_grades = get_grades_for_student(student_id)
            for grade in student_grades:
                grades.remove(grade)

            # Delete student
            students.remove(student)

            # Update counts
            update_class_student_count(class_id)
            update_school_student_count(school_id)

            return '', 204

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
            """
            # Validate full hierarchy
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            cls = find_class_by_id(class_id)
            if not cls:
                return {'error': 'Class not found'}, 404

            if not validate_parent_child_relationship(school_id, class_id):
                return {'error': 'Class does not belong to this school'}, 404

            student = find_student_by_id(student_id)
            if not student:
                return {'error': 'Student not found'}, 404

            if student['class_id'] != class_id:
                return {'error': 'Student does not belong to this class'}, 404

            # Get all grades for this student
            return get_grades_for_student(student_id)

        @schools_ns.doc('create_grade')
        @schools_ns.expect(grade_model)
        @schools_ns.marshal_with(grade_model, code=201)
        def post(self, school_id, class_id, student_id):
            """
            Add a grade for a student.
            """
            # Validate full hierarchy
            school = find_school_by_id(school_id)
            if not school:
                return {'error': 'School not found'}, 404

            cls = find_class_by_id(class_id)
            if not cls:
                return {'error': 'Class not found'}, 404

            if not validate_parent_child_relationship(school_id, class_id):
                return {'error': 'Class does not belong to this school'}, 404

            student = find_student_by_id(student_id)
            if not student:
                return {'error': 'Student not found'}, 404

            if student['class_id'] != class_id:
                return {'error': 'Student does not belong to this class'}, 404

            data = request.json

            # Validate required fields
            required = ['subject', 'grade', 'score']
            if not all(field in data for field in required):
                return {'error': 'Missing required fields: subject, grade, score'}, 400

            # Generate new ID
            new_id = max([g['id'] for g in grades], default=0) + 1

            # Create grade
            grade = {
                'id': new_id,
                'student_id': student_id,  # Set from URL
                'subject': data['subject'],
                'grade': data['grade'],
                'score': data['score'],
                'date': datetime.utcnow().strftime('%Y-%m-%d')
            }

            grades.append(grade)
            return grade, 201

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

            BENEFIT: Shorter URL when you already know the student ID
            """
            student = find_student_by_id(id)
            if not student:
                return {'error': 'Student not found'}, 404
            return student

    @students_flat_ns.route('/<int:id>/grades')
    @students_flat_ns.param('id', 'Student identifier')
    class StudentGradesFlat(Resource):
        """Get grades without full hierarchy."""

        @students_flat_ns.doc('get_student_grades_flat')
        @students_flat_ns.marshal_list_with(grade_model)
        def get(self, id):
            """
            Get all grades for a student (flat).

            BENEFIT: /students/3/grades is much shorter than the nested version
            """
            student = find_student_by_id(id)
            if not student:
                return {'error': 'Student not found'}, 404

            return get_grades_for_student(id)

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
