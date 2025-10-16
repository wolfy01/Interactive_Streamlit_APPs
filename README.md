# 🎮 Streamlit apps Collection

This repository contains **four interactive applications** built with [Streamlit](https://streamlit.io/):

1. **🧮 Calculator**  
   - Perform basic arithmetic operations (Add, Subtract, Multiply, Divide).  
   - Handles invalid inputs and division by zero gracefully.  

2. **📝 Advanced To-Do List**  
   - Add tasks with due date and time.  
   - Countdown timer shows time left until the deadline.  
   - Mark tasks as completed (moved to completed list).  
   - Snooze tasks (+1 day or +1 week).  
   - Export tasks to **CSV** or **JSON**.  
   - Persistent storage in `tasks.json`.  

3. **⭕❌ Smart Tic-Tac-Toe**  
   - **Two Players Mode**: Enter names, track wins, and play against a friend.  
   - **Play vs Computer Mode**: Face an **unbeatable AI** using the Minimax algorithm.  
   - Persistent **leaderboard** stored in `leaderboard.json`.  
   - Restart game button.  
   - Displays winner’s name or declares a tie. 

4. **NovaLearnAI**
   - 📄 Upload Syllabus

   - Click Upload Syllabus from sidebar.

   - Upload your syllabus or lecture notes (PDF).

   - Preview extracted text.

   - 🧠 Generate Questions

   - Choose Topic, Question Type (MCQ/Short Answer), and Number of Questions.

   - Click ⚡ Generate to create AI-based questions.

   - 📝 Take Quiz

   - Select a topic and number of questions.

   - Answer MCQs or type responses.

   - Submit to see instant feedback and correct answers.

   - 🔔 Focus Coach

   - Set a study topic and session duration.

   - Click ▶ Focus to start a timed focus session.

   - 📈 Progress & Insights

   - View charts of accuracy by topic.

   - See weak topics and average performance trends. 

## requirements for NovaLearnAI 
   - **pip install streamlit transformers torch torchvision torchaudio huggingface_hub sentencepiece PyPDF2 pandas**
   - if you have Cuda (GPU) **pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121** (install compatibale version of cuda)


---

## 🚀 How to Get Started

```bash
# 1. Clone the repository
git clone https://github.com/your-username/streamlit-games.git
cd streamlit-games

# 2. Create and activate a virtual environment
python -m venv venv
# On Windows
venv/Scripts/activate
# On macOS/Linux
source venv/bin/activate

# 4. Run any of the apps
streamlit run calculator_app.py
streamlit run todo_app.py
streamlit run tic_tac_toe_app.py
streamlit NovaLearnAI.py
