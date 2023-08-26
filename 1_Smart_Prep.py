import streamlit as st
#from streamlit_extras.app_logo import add_logo
import sqlite3
from io import BytesIO


st.set_page_config(page_title="SmartPrep",page_icon="https://i.imgur.com/S9k9LNT.png")

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
    st.title("Smartprep")

    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://drive.google.com/file/d/1GdRn4OQ4fZT0HsJ5NAFympFp-Q08Yczq/view?usp=sharing);
                background-repeat: no-repeat;
                padding-top: 100px;
                background-position: 20px 20px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    subjects = fetch_subjects()
    selected_subject = st.selectbox("Select a subject", subjects)

    st.title("Paper Selection")
    #add_logo("https://i.imgur.com/W0NrmI1.png")
    add_logo()

    papers = fetch_papers_by_subject(selected_subject)
    pnames = []
    paper_dict = {}
    for i in papers:
        term = i[3].split('T')
        year = 2000 + int(term[0])
        if term[1] == '1':
            month = 'Jan'
        elif term[1] == '2':
            month = 'May'
        else:
            month = 'Sept'

        if 'ET' in i[2]:
            exam = 'END TERM'
        elif 'Q2' in i[2]:
            exam = 'QUIZ 2'
        else:
            exam = 'QUIZ 1'

        pnames.append(month+' '+str(year)+' '+exam+': '+i[1])
        paper_dict[i[0]] = month+' '+str(year)+' '+exam+': '+i[1]

    selected_paper = st.selectbox("Select a paper", pnames)

    for i in paper_dict:
        if selected_paper == paper_dict[i]:
            selected_paper = i

    st.title("Questions")

    questions = fetch_questions_by_paper(selected_paper,selected_subject)
    qnum = 1

    optnum = 1
    for i in questions:
        images_list = []
        ans_text = 'NONE'
        st.subheader(f"Question Number {qnum}")
        mcq = []
        if len(i[2]):
            st.markdown(f"{i[2][0][0]}")
            images_list = i[2][0][1].split("//")

            for img in images_list:
                selected_image = fetch_image_by_id(img)
                image_bytes = bytes(selected_image)
                image_stream = BytesIO(image_bytes)
                st.image(image_stream)

        st.markdown(f"{i[0][1]}")

        #questionid, questiontext, questiontype, answer, imageids, marks, compid

        if len(i[0][4]):
            images_list = i[0][4].split("//")

            for img in images_list:
                selected_image = fetch_image_by_id(img)
                image_bytes = bytes(selected_image)
                image_stream = BytesIO(image_bytes)
                st.image(image_stream)

        right_aligned_bold_text = f"<div style='text-align: right;'><b>[Marks: {i[0][5]}]</b></div>"
        st.markdown(right_aligned_bold_text, unsafe_allow_html=True)

        if "MCQ" in i[0][2]:
            if len(i[1][0][3]) > 4:
                optnum = 1
                for j in i[1]:
                    selected_image = fetch_image_by_id(j[3])
                    image_bytes = bytes(selected_image)
                    image_stream = BytesIO(image_bytes)
                    st.image(image_stream)
                    mcq.append(str(optnum))
                    optnum += 1

                st.radio("Select the Option based on Images above", mcq, key=i[0][0]+'__'+str(optnum))

            else:
                optlist = []
                for j in i[1]:
                    optlist.append(j[1])

                st.radio("Select an Option", optlist,key=i[0][0]+'__'+str(optnum))

            ans_text = "The Correct Option is " + i[0][3]

        elif "MSQ" in i[0][2]:
            for j in i[1]:
                st.checkbox(j[1],key=i[0][0]+'__'+str(optnum))
                if len(j[3]) > 4:
                    selected_image = fetch_image_by_id(j[3])
                    image_bytes = bytes(selected_image)
                    image_stream = BytesIO(image_bytes)
                    st.image(image_stream)
                optnum += 1
            ans = i[0][3].split(',')
            ans_text = "The Correct Options is/are"
            for k in ans:
                ans_text += ' ' + k + ','
            ans_text = ans_text[:-1]
        else:
            ans_text = ''
            st.text_input("Answer:",key=i[0][0])
            ans = i[0][3].split(',')
            for k in ans:
                ans_text += k
        qnum+=1

        button_a = st.button('Show Answer',key=i[0][0]+"SA")
        if button_a:
            st.write(ans_text)


        st.markdown('----')



if __name__ == "__main__":
    main()
