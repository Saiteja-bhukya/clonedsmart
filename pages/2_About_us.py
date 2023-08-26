
import streamlit as st
#from streamlit_extras.app_logo import add_logo
import sqlite3
from io import BytesIO


st.set_page_config(page_title="Smartprep",page_icon="https://i.imgur.com/S9k9LNT.png")

# Function to fetch subjects from the database
def fetch_subjects():
    conn = sqlite3.connect("database.db")  # Update with your database name
    cursor = conn.cursor()

    cursor.execute("SELECT subjectname FROM Subjects")
    subjects = cursor.fetchall()
    frame = []
    for i in subjects:
        if i not in frame:
            frame.append(i)

    conn.close()
    return [subject[0] for subject in frame]


# Function to fetch papers by subject from the database
def fetch_papers_by_subject(subject):
    conn = sqlite3.connect("database.db")  # Update with your database name
    cursor = conn.cursor()
    paperid_list = []
    cursor.execute("SELECT subjects,paperid,papername,exam,paperterm FROM Paper")
    info = cursor.fetchall()

    for i in info:
        if subject in i[0]:
            paperid_list.append((i[1],i[2],i[3],i[4]))

    conn.close()
    return [paper for paper in paperid_list]


# Function to fetch questions by paper from the database
def fetch_questions_by_paper(paper, subject):
    conn = sqlite3.connect("database.db")  # Update with your database name
    cursor = conn.cursor()
    full_data = []
    cursor.execute("SELECT questionid, questiontext, questiontype, answer, imageids, marks, compid FROM Question WHERE paperid=? and subject=?", (paper,subject,))
    questions = cursor.fetchall()

    for i in questions:
        options = []
        comprehension = []
        cursor.execute("SELECT optnumber, opttext, answer, imageids FROM Options where questionid=?", (i[0],))
        options = cursor.fetchall()

        if i[6] != 'NONE':
            cursor.execute("SELECT comptext, imageids FROM Comprehension WHERE compid=?", (i[6],))
            comprehension = cursor.fetchall()

        full_data.append((i,options,comprehension))

    conn.close()
    return full_data

def fetch_image_by_id(imageid):
    conn = sqlite3.connect("database.db")  # Update with your database name
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM Image WHERE imageid=?", (imageid,))
    blobdata = cursor.fetchall()

    return blobdata[0][0]

def btn_b_callback():
    st.session_state.display_result = False
    st.session_state.reset = False

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://i.imgur.com/S9k9LNT.png);
                background-repeat: no-repeat;
                padding-top: 120px;
                background-position: 20px 20px;

            }
            [data-testid="stSidebarNav"]::before {
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def main():

    st.title("About us")
    # add_logo("https://i.imgur.com/W0NrmI1.png")
    add_logo()

    st.write("I Am Sai Teja and I'm an amateur coder who dabbles in Web Development. I'm currently pursuing Diploma level and plan to complete the BS Degree.")

    st.write("This Website was conceived as a part of roster of projects done for the Wayanad Tech Club.")

    st.write("Apart from academics i love playing Cricket, CS:GO and chess. I love watching movies in my spare time.")

    st.write("If you would like to collaborate on any projects or just reach out for any doubts regarding the website, I'll be available at 21f1005681@ds.study.iitm.ac.in")

if __name__ == "__main__":
    main()