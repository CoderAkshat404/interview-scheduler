from fpdf import FPDF
from datetime import datetime, timedelta
import pandas as pd
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['excel_file']
        start_time_str = request.form['start_time']
        duration = int(request.form['duration'])
        break_time = int(request.form['break_time'])

        df = pd.read_excel(file)
        df['Domain'] = df['Domain'].astype(str)
        base_start_time = datetime.strptime(start_time_str, '%H:%M')

        # Organize applicants by domain
        domain_applicants = {}
        for _, row in df.iterrows():
            name = row['Name']
            domains = [d.strip() for d in row['Domain'].split(',')]
            for domain in domains:
                domain_applicants.setdefault(domain, []).append(name)

        # Prepare PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Interview Schedule", ln=True, align='C')
        pdf.ln(10)

        current_time = base_start_time

        for domain, applicants in domain_applicants.items():
            pdf.set_font("Arial", style='B', size=12)
            pdf.cell(200, 10, txt=domain, ln=True)
            pdf.set_font("Arial", size=12)

            for name in applicants:
                time_str = current_time.strftime('%H:%M')
                pdf.cell(200, 10, txt=f"{time_str} - {name}", ln=True)
                current_time += timedelta(minutes=duration)

            # Add break after domain schedule
            current_time += timedelta(minutes=break_time)
            pdf.ln(5)

        output_filename = "interview_schedule.pdf"
        pdf.output(output_filename)

        return send_file(output_filename, as_attachment=True)

    # HTML form with break time input
    return '''
    <form method="post" enctype="multipart/form-data">
        Excel File: <input type="file" name="excel_file"><br>
        Start Time (HH:MM): <input type="text" name="start_time"><br>
        Duration per interview (minutes): <input type="number" name="duration"><br>
        Break time between domains (minutes): <input type="number" name="break_time"><br>
        <input type="submit" value="Generate Schedule">
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
