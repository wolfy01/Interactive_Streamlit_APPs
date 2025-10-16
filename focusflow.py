"""
NovaLearn AI+ : Syllabus-Aware Study Assistant
Author: Nihal Azman
Built with: Streamlit + Hugging Face Transformers
Python 3.13 Compatible
"""

import streamlit as st
import pandas as pd
import random, re, os, time, torch
from datetime import datetime
from transformers import pipeline
from PyPDF2 import PdfReader

# ---------------------------- CONFIG ---------------------------- #
st.set_page_config(page_title="NovaLearn AI+", page_icon="🚀", layout="wide")
st.markdown("<h1 style='text-align:center;'>🚀 NovaLearn AI+</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>Syllabus-Aware Question Generator • Focus Coach • Insights • Recommender</h4>", unsafe_allow_html=True)
st.write("---")

DATA_DIR = "novalearn_data"
os.makedirs(DATA_DIR, exist_ok=True)

SYLLABUS_TXT = os.path.join(DATA_DIR, "syllabus_text.txt")
QUESTIONS_CSV = os.path.join(DATA_DIR, "generated_questions.csv")
QUIZ_RESULTS_CSV = os.path.join(DATA_DIR, "quiz_results.csv")

# ---------------------- STATE INITIALIZATION -------------------- #
for key, val in {
    "syllabus_text": "",
    "generated_questions": [],
    "focus_running": False,
    "focus_start": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# --------------------------- HELPERS ---------------------------- #
def safe_read_csv(path, cols):
    if not os.path.exists(path):
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(path)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df
    except:
        return pd.DataFrame(columns=cols)


def safe_write_csv(path, df):
    df.to_csv(path, index=False)


def extract_text_from_pdf(upload):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(upload)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()
    except Exception as e:
        st.error(f"PDF extraction failed: {e}")
        return ""


def clean_text_for_sentences(text):
    """Split text into clean, meaningful sentences."""
    text = re.sub(r"\s+", " ", text)
    sents = re.split(r"(?<=[.!?])\s", text)
    return [s.strip() for s in sents if len(s.split()) >= 6]


# ---------------------- MODEL INITIALIZATION -------------------- #
@st.cache_resource(show_spinner=False)
def load_qg_model():
    try:
        model_name = "valhalla/t5-base-qg-hl"
        device = 0 if torch.cuda.is_available() else -1
        qg = pipeline("text2text-generation", model=model_name, device=device)
        st.sidebar.success(f"✅ Model loaded ({'GPU' if device == 0 else 'CPU'})")
        return qg
    except Exception as e:
        st.sidebar.error(f"❌ Model load failed: {e}")
        return None


QG_PIPE = load_qg_model()

# ---------------------- SUPPORT FUNCTIONS ----------------------- #
STOPWORDS = set("""
the a an and or but for nor so yet to of in on at by with from into during including until against
among throughout despite towards upon about above below over under again further then once here there
all any both each few more most other some such no not only own same than too very can will just is
are was were be been being as it its that this these those who whom whose which what when where why how
""".split())

def pick_answer_candidates(sent, max_k=2):
    """Extract good potential answers (nouns / entities) from a sentence."""
    s = re.sub(r"\s+", " ", sent).strip()
    phrases = re.findall(r"(?:[A-Z][a-z]+(?:\s+(?:of|the|and|[A-Z][a-z]+))+)", s)
    singles = re.findall(r"\b[A-Z][a-z]{2,}\b", s)
    content = [w for w in re.findall(r"[A-Za-z\-]{4,}", s) if w.lower() not in STOPWORDS]
    seen, cands = set(), []
    for x in phrases + singles + content:
        if x not in seen:
            seen.add(x)
            cands.append(x)
    return cands[:max_k] if cands else ["concept"]


def clean_question(q):
    """Tidy up generated question text."""
    q = re.sub(r"\s+", " ", q).strip()
    q = re.sub(r"(\?\s*){2,}", "?", q)
    if not q.endswith("?"):
        q += "?"
    return q[0].upper() + q[1:]


# ---------------------- QUESTION GENERATION --------------------- #
def generate_questions(text, num_q, qtype, topic):
    """Highlight-based question generation (one context per sentence)."""
    if not QG_PIPE:
        st.warning("Model not available.")
        return []

    text = re.sub(r"(Table|Figure|Index|Appendix|Page\s+\d+|\.{5,})", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    sents = clean_text_for_sentences(text)
    if not sents:
        st.error("No meaningful sentences found.")
        return []

    num_q = min(int(num_q), len(sents), 25)
    qs, seen = [], set()

    for sent in sents[:num_q]:
        answers = pick_answer_candidates(sent, max_k=1)
        ans = answers[0]

        if ans.lower() not in sent.lower():
            continue

        # Format context with highlight for the answer
        marked = sent.replace(ans, f"<hl> {ans} <hl>")
        prompt = f"generate question: context: {marked}"
        try:
            out = QG_PIPE(prompt, max_new_tokens=48, num_beams=4, do_sample=False)[0]["generated_text"]
        except Exception:
            continue

        qtext = clean_question(out)
        norm_key = re.sub(r"\W+", "", qtext.lower())
        if norm_key in seen:
            continue
        seen.add(norm_key)

        entry = {
            "topic": topic,
            "qtype": qtype,
            "question": qtext,
            "answer": ans,
            "options": []
        }

        # MCQ distractors
        if qtype == "MCQ":
            words = [w for w in re.findall(r"[A-Za-z][A-Za-z\-]{4,}", text) if w.lower() not in STOPWORDS]
            distractors = random.sample(words, min(3, len(words))) if len(words) >= 3 else ["Model", "System", "Theory"]
            distractors = [d for d in distractors if d.lower() != ans.lower()]
            options = [ans] + distractors
            random.shuffle(options)
            entry["options"] = options

        qs.append(entry)

    # Save to CSV
    old = safe_read_csv(QUESTIONS_CSV, ["id","timestamp","topic","qtype","question","options","answer"])
    start_id = 1 if old.empty else int(old["id"].max()) + 1
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = [{
        "id": start_id+i,
        "timestamp": ts,
        "topic": q["topic"],
        "qtype": q["qtype"],
        "question": q["question"],
        "options": "|".join(q["options"]),
        "answer": q["answer"]
    } for i,q in enumerate(qs)]
    new = pd.concat([old, pd.DataFrame(rows)], ignore_index=True)
    safe_write_csv(QUESTIONS_CSV, new)
    return qs


# ---------------------- QUIZ RESULT STORAGE --------------------- #
def record_result(topic, qtype, question, correct, user_ans, correct_ans):
    df = safe_read_csv(QUIZ_RESULTS_CSV, ["timestamp","topic","qtype","question","correct","user_answer","correct_answer"])
    df.loc[len(df)] = [datetime.now().strftime("%Y-%m-%d %H:%M"), topic, qtype, question, int(correct), user_ans, correct_ans]
    safe_write_csv(QUIZ_RESULTS_CSV, df)


# ---------------------------- UI MENU ---------------------------- #
menu = st.sidebar.radio(
    "Navigate",
    ["📄 Upload Syllabus", "🧠 Generate Questions", "📝 Take Quiz", "🔔 Focus Coach", "📈 Progress & Insights"]
)


# ---------------------------- MODULES ---------------------------- #
if menu == "📄 Upload Syllabus":
    st.subheader("📄 Upload Your Syllabus")
    upload = st.file_uploader("Upload a PDF", type=["pdf"])
    if upload:
        text = extract_text_from_pdf(upload)
        if len(text) < 50:
            st.warning("Text seems too short or image-based.")
        else:
            st.session_state.syllabus_text = text
            with open(SYLLABUS_TXT, "w", encoding="utf-8") as f:
                f.write(text)
            st.success("Syllabus extracted successfully.")
            st.text_area("Preview", text[:800], height=250)
    else:
        cached = open(SYLLABUS_TXT, encoding="utf-8").read() if os.path.exists(SYLLABUS_TXT) else ""
        if cached:
            st.info("Loaded previous syllabus.")
            st.session_state.syllabus_text = cached
            st.text_area("Preview", cached[:800], height=250)


elif menu == "🧠 Generate Questions":
    st.subheader("🧠 Generate Questions")
    text = st.session_state.syllabus_text
    if not text:
        st.warning("Please upload a syllabus first.")
    else:
        topic = st.text_input("Topic", "General")
        qtype = st.selectbox("Type", ["MCQ", "Short Answer"])
        num_q = st.slider("How many?", 1, 15, 5)
        if st.button("⚡ Generate"):
            with st.spinner("Generating questions..."):
                qs = generate_questions(text, num_q, qtype, topic)
            st.success(f"Generated {len(qs)} questions.")
            for i, q in enumerate(qs, 1):
                st.markdown(f"**{i}. {q['question']}**")
                if q["qtype"] == "MCQ":
                    for opt in q["options"]:
                        st.write(f"- {opt}")
                st.caption(f"Answer: {q['answer']}")


elif menu == "📝 Take Quiz":
    st.subheader("📝 Take a Quiz")
    df = safe_read_csv(QUESTIONS_CSV, ["id","timestamp","topic","qtype","question","options","answer"])
    if df.empty:
        st.info("Generate questions first.")
    else:
        topics = ["All"] + sorted(df["topic"].unique())
        topic = st.selectbox("Select topic", topics)
        pool = df if topic == "All" else df[df["topic"] == topic]
        n = st.slider("Number of questions", 1, min(10, len(pool)), 5)
        sample = pool.sample(n, random_state=42)
        answers = []
        for i, row in sample.iterrows():
            st.write(f"**{row['question']}**")
            opts = row["options"].split("|") if isinstance(row["options"], str) else []
            if row["qtype"] == "MCQ" and opts:
                ans = st.radio("Choose:", opts, key=f"q_{row['id']}")
            else:
                ans = st.text_input("Your answer:", key=f"q_{row['id']}")
            answers.append((row, ans))
            st.write("")
        if st.button("Submit"):
            correct = 0
            st.write("---")
            for row, ans in answers:
                truth = row["answer"].strip()
                is_corr = ans.strip().lower() == truth.lower()
                record_result(row["topic"], row["qtype"], row["question"], is_corr, ans, truth)
                if is_corr:
                    correct += 1
                    st.success(f"✅ {row['question']}")
                else:
                    st.error(f"❌ {row['question']}\n**Correct:** {truth}")
            st.info(f"Score: {correct}/{len(answers)} ({int(correct / len(answers) * 100)}%)")


elif menu == "🔔 Focus Coach":
    st.subheader("🔔 Focus Coach")
    topic = st.text_input("Topic", "General")
    minutes = st.slider("Focus duration (min)", 5, 120, 25)
    if not st.session_state.focus_running:
        if st.button("▶ Start"):
            st.session_state.focus_running = True
            st.session_state.focus_start = time.time()
            st.success("Focus started!")
    else:
        elapsed = int(time.time() - st.session_state.focus_start)
        pct = min(1, elapsed / (minutes * 60))
        st.progress(pct)
        if elapsed >= minutes * 60:
            st.success("🎉 Session complete!")
            st.session_state.focus_running = False
        if st.button("⏹ Stop"):
            st.session_state.focus_running = False


elif menu == "📈 Progress & Insights":
    st.subheader("📈 Progress & Insights")
    res = safe_read_csv(QUIZ_RESULTS_CSV, ["timestamp", "topic", "qtype", "question", "correct", "user_answer", "correct_answer"])
    if res.empty:
        st.info("No quiz data yet.")
    else:
        acc = res.groupby("topic")["correct"].mean() * 100
        st.bar_chart(acc)
        pct = int(100 * res["correct"].mean())
        st.metric("Overall Accuracy", f"{pct}%")
        weak = acc[acc < 60]
        if not weak.empty:
            st.warning("Weak topics: " + ", ".join(weak.index))
