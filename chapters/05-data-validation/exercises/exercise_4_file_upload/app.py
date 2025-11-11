"""
Exercise 4: File Upload Validation
Chapter 5: Data Validation & Error Handling

Learning Objectives:
- Validate file size limits
- Check file extensions and MIME types
- Verify image dimensions with PIL
- Implement secure filename handling
- Detect potentially malicious files

TODO: Complete the marked sections to implement file upload validation!
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from marshmallow import Schema, fields as ma_fields, ValidationError
from PIL import Image
import os
import io
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max request
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

api = Api(
    app,
    version='1.0',
    title='Exercise 4: File Upload Validation',
    description='Learn to validate and secure file uploads',
    doc='/swagger'
)

# ============================================================================
# DATABASE MODEL
# ============================================================================

class Post(db.Model):
    __tablename__ = 'posts_ex4'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    image_filename = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'image_url': self.image_url,
            'image_filename': self.image_filename
        }

# ============================================================================
# TODO 1: Create File Size Validator
# ============================================================================
# Create a function that validates file size:
# - Maximum file size: 5MB (5 * 1024 * 1024 bytes)
# - Use file.seek(0, os.SEEK_END) to get file size
# - Use file.tell() to get current position (which is the size)
# - Remember to file.seek(0) to reset position after checking
#
# Hints:
# - file.seek(0, os.SEEK_END) moves to end of file
# - file.tell() returns current position
# - Don't forget to reset with file.seek(0)

def validate_file_size(file):
    """Validate file size (max 5MB)"""

    # TODO: Get file size
    # file.seek(0, os.SEEK_END)
    # size = file.tell()
    # file.seek(0)  # Reset to beginning

    # TODO: Check if size exceeds 5MB
    # max_size = 5 * 1024 * 1024  # 5MB
    # if size > max_size:
    #     raise ValidationError(f'File too large. Maximum size is 5MB, got {size / (1024*1024):.2f}MB')

    pass

# ============================================================================
# TODO 2: Create File Extension Validator
# ============================================================================
# Validate allowed file extensions:
# - Allowed: .jpg, .jpeg, .png, .gif
# - Use secure_filename() to sanitize filename
# - Extract extension with filename.rsplit('.', 1)[1].lower()
#
# Hints:
# - Use werkzeug.utils.secure_filename(file.filename)
# - Check if '.' is in filename before splitting

def validate_file_extension(file):
    """Validate file extension"""

    # TODO: Sanitize filename
    # filename = secure_filename(file.filename)

    # TODO: Check if file has extension
    # if '.' not in filename:
    #     raise ValidationError('File must have an extension')

    # TODO: Extract and validate extension
    # ext = filename.rsplit('.', 1)[1].lower()
    # allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
    #
    # if ext not in allowed_extensions:
    #     raise ValidationError(f'Invalid file type. Allowed: {", ".join(allowed_extensions)}')

    pass

# ============================================================================
# TODO 3: Create MIME Type Validator
# ============================================================================
# Validate actual file type (prevents fake extensions):
# - Use PIL Image.open() to verify it's actually an image
# - Allowed MIME types: image/jpeg, image/png, image/gif
# - Catch PIL.UnidentifiedImageError for invalid images
#
# Hints:
# - Read file into BytesIO: io.BytesIO(file.read())
# - Use Image.open(image_stream)
# - Check img.format for actual type
# - Don't forget file.seek(0) to reset

def validate_mime_type(file):
    """Validate actual file type using PIL"""

    # TODO: Read file content
    # file_content = file.read()
    # file.seek(0)  # Reset position

    # TODO: Try to open as image
    # try:
    #     image_stream = io.BytesIO(file_content)
    #     img = Image.open(image_stream)
    #
    #     # Check format
    #     allowed_formats = ['JPEG', 'PNG', 'GIF']
    #     if img.format not in allowed_formats:
    #         raise ValidationError(f'Invalid image format: {img.format}')
    #
    # except Exception as e:
    #     raise ValidationError(f'Invalid image file: {str(e)}')

    pass

# ============================================================================
# TODO 4: Create Image Dimensions Validator
# ============================================================================
# Validate image dimensions:
# - Maximum width: 2000 pixels
# - Maximum height: 2000 pixels
# - Use PIL Image.open() to get dimensions
#
# Hints:
# - img.width and img.height give dimensions
# - Read file into BytesIO like in TODO 3

def validate_image_dimensions(file):
    """Validate image dimensions (max 2000x2000)"""

    # TODO: Read file and open as image
    # file_content = file.read()
    # file.seek(0)
    #
    # image_stream = io.BytesIO(file_content)
    # img = Image.open(image_stream)

    # TODO: Check dimensions
    # max_width = 2000
    # max_height = 2000
    #
    # if img.width > max_width or img.height > max_height:
    #     raise ValidationError(
    #         f'Image too large. Maximum: {max_width}x{max_height}, '
    #         f'got {img.width}x{img.height}'
    #     )

    pass

# ============================================================================
# TODO 5: Create Complete File Validator
# ============================================================================
# Combine all validators into one function

def validate_image_upload(file):
    """Complete image upload validation"""

    if not file:
        raise ValidationError('No file provided')

    # TODO: Run all validators
    # validate_file_size(file)
    # validate_file_extension(file)
    # validate_mime_type(file)
    # validate_image_dimensions(file)

    pass

# ============================================================================
# NAMESPACES
# ============================================================================

posts_ns = Namespace('posts', description='Post operations')
api.add_namespace(posts_ns, path='/posts')

# File upload model for Swagger
upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True,
                          help='Image file (jpg, png, gif) - max 5MB, max 2000x2000')

# ============================================================================
# ROUTES
# ============================================================================

@posts_ns.route('/')
class PostList(Resource):
    def post(self):
        """Create a post"""
        data = request.json or {}
        post = Post(
            title=data.get('title', 'Sample Post'),
            content=data.get('content', 'Sample content')
        )
        db.session.add(post)
        db.session.commit()
        return {'message': 'Post created', 'post': post.to_dict()}, 201

    def get(self):
        """Get all posts"""
        posts = Post.query.all()
        return {'posts': [p.to_dict() for p in posts]}, 200

# ============================================================================
# TODO 6: Implement Image Upload Endpoint
# ============================================================================

@posts_ns.route('/<int:post_id>/image')
class PostImage(Resource):
    @posts_ns.expect(upload_parser)
    def post(self, post_id):
        """Upload image for post"""

        # TODO: Get post
        # post = Post.query.get_or_404(post_id)

        # TODO: Get file from request
        # if 'file' not in request.files:
        #     return {'error': 'No file provided'}, 400
        #
        # file = request.files['file']

        # TODO: Validate file
        # try:
        #     validate_image_upload(file)
        # except ValidationError as err:
        #     return {'error': str(err)}, 400

        # TODO: Save file
        # filename = secure_filename(file.filename)
        # # Add timestamp to make unique
        # from datetime import datetime
        # unique_filename = f"{post_id}_{datetime.utcnow().timestamp()}_{filename}"
        # filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        #
        # file.save(filepath)

        # TODO: Update post
        # post.image_filename = unique_filename
        # post.image_url = f'/uploads/{unique_filename}'
        # db.session.commit()

        # TODO: Return success
        # return {
        #     'message': 'Image uploaded successfully',
        #     'post': post.to_dict()
        # }, 200

        return {'error': 'Not implemented. Complete TODO 6!'}, 501

# ============================================================================
# DATABASE INIT
# ============================================================================

with app.app_context():
    db.create_all()
    print("✅ Database table created: posts_ex4")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")

# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("📸 EXERCISE 4: File Upload Validation")
    print("="*70)
    print("\nTODO List:")
    print("  1. Create validate_file_size() function (max 5MB)")
    print("  2. Create validate_file_extension() function (jpg, png, gif)")
    print("  3. Create validate_mime_type() function (verify with PIL)")
    print("  4. Create validate_image_dimensions() function (max 2000x2000)")
    print("  5. Create validate_image_upload() combining all validators")
    print("  6. Implement image upload endpoint")
    print("\nTest Cases:")
    print("  ✓ Upload file > 5MB → File too large error")
    print("  ✓ Upload .exe renamed to .jpg → Invalid image error")
    print("  ✓ Upload 3000x3000 image → Image too large error")
    print("  ✓ Upload valid .jpg image → Success!")
    print("\nTesting:")
    print("  1. Create a post: POST /posts")
    print("  2. Upload image: POST /posts/1/image (use 'file' field)")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
