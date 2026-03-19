import io, csv, os, imagePrediction, json
from flask import Flask, render_template, request, redirect, flash, url_for, Response
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "345i9-03945-03i45tonedfg0o9jeofgnslk"

JSON_DB = 'scores.json'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'cr2', 'arw'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure folder exists

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
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    count = len([f for f in files if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))])
    return render_template('index.html', file_count=count)

@app.route('/upload', methods=['POST'])
def upload_file():
    print(request.files)
# 1. Check if the folder is already full
    existing_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                      if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    
    if len(existing_files) >= 10:
        flash("Storage full! Limit is 10 files. Please delete some before uploading.")
        return redirect(url_for('index'))

    # 2. Proceed with standard upload checks
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file and file_check(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash(f"Successfully uploaded {filename}. ({len(existing_files) + 1}/10)")
        return redirect(url_for('index'))
    
    flash("Invalid file type.")
    return redirect(url_for('index'))

@app.route('/files')
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    # Filter out hidden files or system files if necessary
    files = [f for f in files if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    return render_template('index.html', files=files, file_count=len(files))

@app.route('/process')
def process_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    files = [f for f in files if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    for f in files:
        score = imagePrediction.imagePrediction(os.path.join(app.config['UPLOAD_FOLDER'], f)).getValue()
        save_score(f, score)
        print(os.path.join(app.config['UPLOAD_FOLDER'], f))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))

    return render_template('index.html', files=files, file_count=len(files))

@app.route('/download-scores')
def download_scores():
    all_scores = load_scores()
    
    if not all_scores:
        flash("No data available to download. Please upload and process images first.")
        return redirect(url_for('index'))
    
    # Create the in-memory file
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Write Header and Data
    cw.writerow(['Filename', 'Score'])
    for name, score in all_scores.items():
        cw.writerow([name, score])
    
    # Important: Move the "read pointer" to the start of the string
    output = si.getvalue()

    with open(JSON_DB, 'w') as f:
        json.dump({}, f)
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=image_scores.csv"}
    )
    
if __name__ == '__main__':
    app.run(debug=True)