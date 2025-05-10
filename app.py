from fpdf import FPDF
from datetime import datetime, timedelta
import pandas as pd
import os
from flask import Flask, request, send_from_directory, redirect, url_for

app = Flask(__name__)
OUTPUT_FOLDER = "schedules"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['excel_file']
        start_time_str = request.form['start_time']
        duration = int(request.form['duration'])
        schedule_type = request.form['schedule_type']  # "same_day" or "separate_days"

        df = pd.read_excel(file)
        df['Domain'] = df['Domain'].astype(str)
        base_start_time = datetime.strptime(start_time_str, '%H:%M')

        # Clean old files
        for f in os.listdir(OUTPUT_FOLDER):
            os.remove(os.path.join(OUTPUT_FOLDER, f))

        # Organize applicants by domain
        domain_applicants = {}
        for _, row in df.iterrows():
            name = row['Name']
            domains = [d.strip().lower() for d in row['Domain'].split(',')]
            for domain in domains:
                domain_applicants.setdefault(domain, []).append(name)

        # Used only for same_day option
        current_time = base_start_time

        for domain, applicants in domain_applicants.items():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"{domain.upper()} Interview Schedule", ln=True, align='C')
            pdf.ln(10)

            if schedule_type == "separate_days":
                domain_start_time = base_start_time
            else:
                domain_start_time = current_time

            for name in applicants:
                time_str = domain_start_time.strftime('%H:%M')
                pdf.cell(200, 10, txt=f"{time_str} - {name}", ln=True)
                domain_start_time += timedelta(minutes=duration)

            # Update shared current_time only for same_day scheduling
            if schedule_type == "same_day":
                current_time = domain_start_time

            filename = os.path.join(OUTPUT_FOLDER, f"{domain}.pdf")
            pdf.output(filename)

        return redirect(url_for('download_all'))

    # Updated HTML form
    return '''
    <form method="post" enctype="multipart/form-data">
        <label>Excel File:</label> <input type="file" name="excel_file" required><br><br>
        <label>Start Time (HH:MM):</label> <input type="text" name="start_time" required><br><br>
        <label>Duration per interview (minutes):</label> <input type="number" name="duration" required><br><br>
        <label>Schedule Type:</label><br>
        <input type="radio" name="schedule_type" value="separate_days" checked> Separate days (default)<br>
        <input type="radio" name="schedule_type" value="same_day"> Same day (consecutive domains)<br><br>
        <input type="submit" value="Generate Schedule">
    </form>
    '''

@app.route('/download_all')
def download_all():
    files = os.listdir(OUTPUT_FOLDER)
    links = ''.join([f'<li><a href="/download/{f}">{f}</a></li>' for f in files])
    return f'''
    <h2>Download Interview Schedules</h2>
    <ul>{links}</ul>
    '''

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
