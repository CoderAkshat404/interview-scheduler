from flask import Flask, request, send_file, redirect, url_for, render_template_string
from fpdf import FPDF
from datetime import datetime, timedelta
import pandas as pd
import os
import zipfile

app = Flask(__name__)

OUTPUT_FOLDER = "generated_pdfs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['excel_file']
        start_time_str = request.form['start_time']
        duration = int(request.form['duration'])
        schedule_type = request.form['schedule_type']  # "same_day" or "separate_days"

        df = pd.read_excel(file)

        # Identify columns containing 'name' and 'domain'
        name_col = None
        domain_col = None

        for col in df.columns:
            col_lower = col.lower()
            if 'name' in col_lower and name_col is None:
                name_col = col
            elif 'domain' in col_lower and domain_col is None:
                domain_col = col

        if not name_col or not domain_col:
            return "Error: Could not detect 'Name' or 'Domain' columns. Please check your Excel file."

        df[domain_col] = df[domain_col].astype(str)
        base_start_time = datetime.strptime(start_time_str, '%H:%M')

        # Clean previous PDFs
        for f in os.listdir(OUTPUT_FOLDER):
            os.remove(os.path.join(OUTPUT_FOLDER, f))

        # Organize applicants by domain
        domain_applicants = {}
        for _, row in df.iterrows():
            name = row[name_col]
            domains = [d.strip().lower() for d in row[domain_col].split(',')]
            for domain in domains:
                domain_applicants.setdefault(domain, []).append(name)

        current_time = base_start_time

        # Generate one PDF per domain
        for domain, applicants in domain_applicants.items():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"{domain.upper()} Interview Schedule", ln=True, align='C')
            pdf.ln(10)

            domain_start_time = current_time if schedule_type == "same_day" else base_start_time

            for name in applicants:
                time_str = domain_start_time.strftime('%H:%M')
                pdf.cell(200, 10, txt=f"{time_str} - {name}", ln=True)
                domain_start_time += timedelta(minutes=duration)

            if schedule_type == "same_day":
                current_time = domain_start_time

            filename = os.path.join(OUTPUT_FOLDER, f"{domain}.pdf")
            pdf.output(filename)

        return redirect(url_for('download_all'))

    # HTML form
    return '''
    <h2>Interview Scheduler</h2>
    <form method="post" enctype="multipart/form-data">
        <label>Excel File (Google Form response):</label><br>
        <input type="file" name="excel_file" required><br><br>

        <label>Start Time (HH:MM):</label><br>
        <input type="text" name="start_time" placeholder="e.g., 10:00" required><br><br>

        <label>Duration per interview (minutes):</label><br>
        <input type="number" name="duration" required><br><br>

        <label>Schedule interviews:</label><br>
        <input type="radio" name="schedule_type" value="separate_days" checked> On Separate Days (default)<br>
        <input type="radio" name="schedule_type" value="same_day"> On Same Day (consecutively)<br><br>

        <input type="submit" value="Generate Schedule">
    </form>
    '''

@app.route('/download_all')
def download_all():
    zip_filename = "all_pdfs.zip"
    zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in os.listdir(OUTPUT_FOLDER):
            if filename.endswith('.pdf'):
                zipf.write(os.path.join(OUTPUT_FOLDER, filename), arcname=filename)

    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
