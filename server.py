import io, csv, os, imagePrediction, json
from flask import Flask, render_template, request, redirect, url_for, Response, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = ""

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'cr2', 'arw'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
JSON_DB = os.path.join(BASE_DIR, 'scores.json')

def load_scores():
    if not os.path.exists(JSON_DB):
        return {}
    with open(JSON_DB, 'r') as f:
        return json.load(f)

def save_score(filename, score):
    scores = load_scores()
    scores[filename] = score
    with open(JSON_DB, 'w') as f:
        json.dump(scores, f, indent=4)

def file_check(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    upload_path = app.config['UPLOAD_FOLDER']
    all_scores = load_scores()
    filenames = [f for f in os.listdir(upload_path) if os.path.isfile(os.path.join(upload_path, f))]

    display_files = []
    for name in filenames:
        display_files.append({
            'name': name,
            'score': all_scores.get(name, "Pending..."),
            'processed': name in all_scores,
            'url': url_for('display_image', filename=name)
        })

    return render_template('index.html', files=display_files, file_count=len(display_files), has_scores=len(all_scores) > 0)

@app.route('/upload', methods=['POST'])
def upload_file():
    print(request.files)

    existing_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER'])
                      if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]

    if len(existing_files) >= 10:
        print("Storage full! Limit is 10 files. Please delete some before uploading.")
        return redirect(url_for('index'))

    if 'file' not in request.files:
        print('No file part')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename  == '':
        print('No selected file')
        return redirect(url_for('index'))

    if file and file_check(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(f"Successfully uploaded {filename}. ({len(existing_files) + 1}/10)")
        return redirect(url_for('index'))

    print("Invalid file type.")
    return redirect(url_for('index'))

@app.route('/files')
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])

    files = [f for f in files if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    return render_template('index.html', files=files, file_count=len(files))

@app.route('/process', methods=['POST'])
def process_images():
    upload_path = app.config['UPLOAD_FOLDER']
    all_scores = load_scores()

    filenames = [f for f in os.listdir(upload_path)
                 if os.path.isfile(os.path.join(upload_path, f))]

    if not filenames:
        print("No images to process!")
        return redirect(url_for('index'))

    for name in filenames:

        if name not in all_scores:
            f = os.path.join(upload_path, name)
            score = imagePrediction.imagePrediction(f).getValue()
            save_score(name, score)
            os.remove(f)

    print("Processing complete!")
    return redirect(url_for('index'))

@app.route('/display/<filename>')
def display_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download-scores')
def download_scores():
    all_scores = load_scores()

    if not all_scores:
        print("No data available to download. Please upload and process images first.")
        return redirect(url_for('index'))

    si = io.StringIO()
    cw = csv.writer(si)

    cw.writerow(['Filename', 'Score'])
    for name, score in all_scores.items():
        cw.writerow([name, score])

    output = si.getvalue()

    with open(JSON_DB, 'w') as f:
        json.dump({}, f)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=image_scores.csv"}
    )

if __name__  == '__main__':
    app.run(debug=True)
