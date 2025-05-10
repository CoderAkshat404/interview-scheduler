from flask import Flask, request, jsonify, send_file
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import io

app = Flask(__name__)

# Make sure to create the "uploads" folder in your project
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route to upload the .xlsx file
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    
    if file.filename.endswith('.xlsx'):
        # Save file to server
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Read the data from the file
        data = pd.read_excel(filepath)
        
        return jsonify({"message": "File uploaded successfully!"}), 200
    else:
        return jsonify({"message": "Invalid file type. Please upload an .xlsx file."}), 400

# Route to generate interview schedule
@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    # Read the data from the uploaded file (you may need to adjust the file path if needed)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'interview_data.xlsx')
    data = pd.read_excel(filepath)

    start_time = request.json.get("start_time")  # In format 'HH:MM'
    interview_time = int(request.json.get("time_per_interview"))  # In minutes

    # Create an empty list to store the schedule
    schedule = []

    # Iterate over the domains and create a schedule for each domain
    for domain in data['domain'].unique():
        domain_data = data[data['domain'] == domain]
        current_time = start_time
        
        for _, person in domain_data.iterrows():
            person_schedule = {
                "name": person['name'],
                "domain": domain,
                "time_slot": current_time
            }
            schedule.append(person_schedule)
            
            # Increment the time slot by interview_time for the next person
            hours, minutes = map(int, current_time.split(':'))
            minutes += interview_time
            if minutes >= 60:
                hours += minutes // 60
                minutes = minutes % 60
            current_time = f"{hours:02}:{minutes:02}"
    
    # Generate the schedule as a PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Interview Schedule")
    y_position = 730
    for person in schedule:
        c.drawString(100, y_position, f"{person['name']} ({person['domain']}) - {person['time_slot']}")
        y_position -= 20
    
    c.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="schedule.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
