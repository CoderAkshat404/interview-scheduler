from flask import Flask, request, send_file, redirect, url_for, render_template
from fpdf import FPDF
from datetime import datetime, timedelta
import pandas as pd
import os
import zipfile

app = Flask(__name__)

OUTPUT_FOLDER = "generated_files"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def sanitize_domain(domain):
    return domain.lower().replace(' ', '_')

def generate_vcf(domain, entries):
    vcf_content = ""
    for name, phone in entries:
        if pd.isna(phone):
            continue
        vcf_content += (
            "BEGIN:VCARD\n"
            "VERSION:3.0\n"
            f"N:{name};;;\n"
            f"FN:{name}\n"
            f"TEL;TYPE=CELL:{str(phone)}\n"
            "END:VCARD\n\n"
        )
    filename = os.path.join(OUTPUT_FOLDER, f"{sanitize_domain(domain)}.vcf")
    with open(filename, "w", encoding='utf-8') as f:
        f.write(vcf_content)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['excel_file']
        start_time_str = request.form['start_time']
        duration = int(request.form['duration'])
        schedule_type = request.form['schedule_type']  # "same_day" or "separate_days"

        df = pd.read_excel(file)

        # Detect columns
        name_col, domain_col, phone_col = None, None, None
        for col in df.columns:
            col_lower = col.lower()
            if 'name' in col_lower and not name_col:
                name_col = col
            elif 'domain' in col_lower and not domain_col:
                domain_col = col
            elif ('phone' in col_lower or 'mobile' in col_lower or 'contact' in col_lower) and not phone_col:
                phone_col = col

        if not name_col or not domain_col:
            return "Error: Could not detect 'Name' or 'Domain' columns."

        df[domain_col] = df[domain_col].astype(str)
        base_start_time = datetime.strptime(start_time_str, '%H:%M')

        # Clean previous files
        for f in os.listdir(OUTPUT_FOLDER):
            os.remove(os.path.join(OUTPUT_FOLDER, f))

        # Organize applicants by domain
        domain_applicants = {}
        for _, row in df.iterrows():
            name = str(row[name_col]).strip()
            phone = row[phone_col] if phone_col else None
            domains = [d.strip().lower() for d in row[domain_col].split(',')]
            for domain in domains:
                domain_applicants.setdefault(domain, []).append((name, phone))

        current_time = base_start_time

        for domain, applicants in domain_applicants.items():
            # Generate PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"{domain.upper()} Interview Schedule", ln=True, align='C')
            pdf.ln(10)

            domain_start_time = current_time if schedule_type == "same_day" else base_start_time

            for name, _ in applicants:
                time_str = domain_start_time.strftime('%H:%M')
                pdf.cell(200, 10, txt=f"{time_str} - {name}", ln=True)
                domain_start_time += timedelta(minutes=duration)

            if schedule_type == "same_day":
                current_time = domain_start_time

            pdf_path = os.path.join(OUTPUT_FOLDER, f"{sanitize_domain(domain)}.pdf")
            pdf.output(pdf_path)

            # Generate VCF
            generate_vcf(domain, applicants)

        return redirect(url_for('download_all'))

    return render_template('index.html')

@app.route('/download_all')
def download_all():
    zip_filename = "all_files.zip"
    zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in os.listdir(OUTPUT_FOLDER):
            if filename.endswith('.pdf') or filename.endswith('.vcf'):
                zipf.write(os.path.join(OUTPUT_FOLDER, filename), arcname=filename)

    return send_file(zip_path, as_attachment=True)

# ✅ This section is updated for Railway deployment
import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
