# Interview Scheduler 🗓️

A simple and efficient web application to automate the interview scheduling process for student clubs and committees.

Built using **Flask** and **Pandas**, this tool allows users to upload Excel files of applicant data and generate personalized interview schedules (PDFs) and VCF contact files for each domain — saving hours of manual work!

---

## 🔍 Features

- 📁 Upload Excel sheet containing applicant names, phone numbers, and selected domains  
- 🕐 Set custom **start time**, **interview duration**, and **breaks between domains**  
- 🗓️ Choose scheduling type: **All interviews on the same day** or **Separate days for each domain**  
- 📄 Automatically generates **downloadable PDF schedules**  
- 📇 Generates **VCF contact files** domain-wise  
- 💻 Fully responsive UI (works on both **mobile** and **desktop**)

---

## 💡 How the Idea Started

During college club recruitments, we used Google Forms to collect applicant data. However, sorting names and phone numbers domain-wise and manually planning interviews was repetitive and prone to errors.  
This inspired us to build **Interview Scheduler** — a tool to automate and simplify this task!

---

## 🛠 Tech Stack

- **Frontend**: HTML, CSS  
- **Backend**: Python (Flask)  
- **Libraries**: 
  - `pandas` for data processing  
  - `reportlab` for PDF generation  
  - `vobject` for VCF generation  
- **Deployment**: Render

---

## 🚀 Getting Started (Local Setup)

1. **Clone the repository**:
   git clone https://github.com/CoderAkshat404/interview-scheduler.git

   cd interview-scheduler

2. **Create a virtual environment**

python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**

pip install -r requirements.txt


4. **Run the application**

python app.py

Open your browser and go to http://localhost:5000

📁 **Folder Structure**

├── app.py
├── templates/
│   └── index.html
├── static/
│   └── background.jpg
├── generated/
│   └── (PDFs & VCFs generated here)
├── requirements.txt
└── README.md

🤝 **Contributors**
Akshat Mishra

Akshata Bakre

📬 **Feedback**
If you have any suggestions, feel free to open an issue or submit a pull request. We'd love to improve this tool further!