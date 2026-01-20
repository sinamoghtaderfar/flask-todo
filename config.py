import os

# مسیر پوشه برای آپلود عکس پروفایل
UPLOAD_FOLDER = os.path.join(os.getcwd(), "static/profile_img")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# اطمینان از اینکه پوشه وجود دارد
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
