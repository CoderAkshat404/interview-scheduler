from flask import Flask, render_template, request, send_file
import pandas as pd
from fpdf import FPDF
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'GET':
        # Prevent direct GET access to /schedule, redirect to home
        return render_template('index.html')

    file = request.files['file']
    start_time_str = request.form['start_time']
    duration = int(request.form['duration'])

    # Read Excel file
    df = pd.read_excel(file)

    # Ensure required columns are present
    if 'Name' not in df.columns or 'Domain' not in df.columns:
        return "Excel must have 'Name' and 'Domain' columns", 400

    # Group by domain
    grouped = df.groupby('Domain')

    start_time = datetime.strptime(start_time_str, "%H:%M")
    final_schedule = []

    for domain, group in grouped:
        domain_time = start_time
        for _, row in group.iterrows():
            final_schedule.append({
                'Name': row['Name'],
                'Domain': domain,
                'Time': domain_time.strftime('%H:%M')
            })
            domain_time += timedelta(minutes=duration)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Interview Schedule", ln=True, align='C')
    pdf.ln(10)

    for item in final_schedule:
        line = f"{item['Time']} - {item['Name']} ({item['Domain']})"
        pdf.cell(200, 10, txt=line, ln=True)

    output_path = "schedule.pdf"
    pdf.output(output_path)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
