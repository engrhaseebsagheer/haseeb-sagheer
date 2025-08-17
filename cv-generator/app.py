from flask import Flask, request, render_template, redirect
from fpdf import FPDF
import re
from datetime import datetime
import uuid


def fix_multiline_paragraph(text):
    lines = text.strip().splitlines()
    cleaned = []
    paragraph = ""

    # Regex to match bullets or numbered formats
    bullet_pattern = re.compile(
        r"""^(
            [\-\*•‣‧▪]+                        |  # common bullet symbols
            \d+[\.\)]?                         |  # 1. or 1) or 1
            [a-zA-Z][\.\)]?                    |  # a. or a) or A) or A.
            [ivxlcdm]+[\.\)]?                  |  # Roman numerals i., ii), etc.
        )\s+""",
        re.IGNORECASE | re.VERBOSE
    )

    for line in lines:
        stripped = line.strip()

        if bullet_pattern.match(stripped):
            if paragraph:
                cleaned.append(paragraph.strip())
                paragraph = ""
            cleaned.append(stripped)
        elif stripped == "":
            if paragraph:
                cleaned.append(paragraph.strip())
                paragraph = ""
        else:
            paragraph += " " + stripped

    if paragraph:
        cleaned.append(paragraph.strip())

    return "\n".join(cleaned)


def generate_experience_section(pdf, occupation, place, position, start_date, end_date, description_text):
 
    left_margin = 6
    right_margin = 6
    height_cell = 7

    pdf.cell(w=12)
    pdf.set_xy(pdf.x,pdf.y +2.5)
    # Occupation and Location
    occupation = occupation.upper() + " -   "
    pdf.set_font("Emoji", size=12)
    pdf.cell(w=6, h=height_cell, txt="☑")
    pdf.set_font("PoppinsBold", size=12)
    pdf.cell(w=pdf.get_string_width(occupation) + 2, h=height_cell, txt=occupation, align="L")

    pdf.set_font("PoppinsRegular", size=12)
    place = place.upper()
    pdf.cell(w=pdf.get_string_width(place) + 2, h=height_cell, txt=place, align="L", ln=True)
    pdf.set_xy(12, pdf.y)

    # Position and Dates
    position_text = position.upper() + "  - "
    pdf.set_font("PoppinsBold", size=12)
    pdf.cell(w=pdf.get_string_width(position_text) + 2, h=height_cell, txt=position_text, align="L")

    pdf.set_font("PoppinsRegular", size=12)
    date_range = start_date.upper() + "  -  "
    pdf.cell(w=pdf.get_string_width(date_range), h=height_cell, txt=date_range)
    pdf.cell(w=pdf.get_string_width(end_date.upper()), h=height_cell, txt=end_date.upper(), ln=True)

    # Draw underlined date line
    pdf.set_line_width(0.3)
    pdf.set_draw_color(0, 0, 50)
    x_start = left_margin + 7
    y = pdf.get_y() - 1
    line_length = pdf.get_string_width(position_text + date_range + end_date.upper())
    pdf.line(x_start, y, x_start + line_length + 2, y)

    # Description paragraph
    pdf.set_font("PoppinsRegular", size=10)
    pdf.set_xy(left_margin + 6.5, pdf.get_y() + 1)

    cleaned_text = fix_multiline_paragraph(description_text)

    pdf.multi_cell(
        w=pdf.w - (left_margin + 7) - right_margin,
        h=6,
        txt=cleaned_text,
        border=False,
        align="L"
    )

def generate_education_section(pdf, start_date, end_date, location, degree_title, institute_name, modules_text, final_grade):
    # First line: Date + Location
    
    pdf.cell(w=12,h=2)
    pdf.set_xy(pdf.x,pdf.y+3)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("PoppinsRegular", size=10)
    education_duration = f"{start_date} - {end_date} | {location}"
    pdf.cell(w=pdf.get_string_width(education_duration), txt=education_duration, h=7, border=False, align="L", ln=True)

    # Second line: Degree Title + Institute
    pdf.cell(12)
    pdf.set_font("PoppinsBold", size=12)
    degree_title = degree_title.upper()
    pdf.cell(w=pdf.get_string_width(degree_title), txt=degree_title, h=7, border=False, align="L")
    
    institute_name = " " + institute_name
    pdf.set_font("PoppinsRegular", size=12)
    pdf.cell(w=pdf.get_string_width(institute_name), txt=institute_name, h=7, border=False, align="L", ln=True)

    # Line separator
    pdf.set_line_width(0.6)
    pdf.set_draw_color(0, 75, 128)
    line_y = pdf.get_y()
    pdf.line(6 + 7, line_y, pdf.w - 6, line_y)

    # Modules paragraph
    
    cleaned_text = fix_multiline_paragraph(modules_text)
    if not cleaned_text:
        print("The string was empty")
    else:
        pdf.set_font("PoppinsRegular", size=10)
        pdf.set_xy(6 + 6.5, pdf.get_y() + 2)
        pdf.multi_cell(
        w=pdf.w - (6 + 7) - 6,
        h=6,
        txt=cleaned_text,
        border=False,
        align="L"
    )

    
   

    

    # Final grade line
    pdf.set_xy(6 + 6.5, pdf.get_y() + 1)
    pdf.set_font("PoppinsBold", size=12)
    label = "Final Grade: "
    pdf.cell(
        w=pdf.get_string_width(label),
        h=7,
        txt=label,
        align="L",
        border=False
    )

    pdf.set_font("PoppinsRegular", size=12)
    pdf.cell(
        w=pdf.get_string_width(final_grade),
        h=7,
        txt=final_grade,
        align="L",
        border=False,
        ln=True
    )



def render_language_skills_table(pdf, lang, listening, reading, spoken_prod, spoken_inter, writing):
  
    from fpdf import FPDF
    pdf.set_fill_color(240, 245, 255)
    pdf.set_draw_color(0, 75, 128)
    pdf.set_line_width(0.6)

    # Fixed margins and sizes
    left_margin = 13
    right_edge = pdf.w - 6
    table_width = right_edge - left_margin
    cell_height = 8

    # Corrected column widths: 6 equal parts of full usable width
    col_width = table_width / 6
    col_widths = [col_width] * 6
    total_width = sum(col_widths)

    start_x = left_margin  # Aligned with content start

    # CATEGORY HEADERS
    pdf.set_xy(start_x, pdf.get_y())
    pdf.set_font("PoppinsBold", size=12)

    pdf.cell(col_widths[0], cell_height * 2, "", border=0)

    pdf.cell(col_widths[1] + col_widths[2], cell_height, "UNDERSTANDING", border=0, align="C")
    pdf.cell(col_widths[3] + col_widths[4], cell_height, "SPEAKING", border=0, align="C")
    pdf.cell(col_widths[5], cell_height, "WRITING", border=0, align="C")
    pdf.ln(cell_height)

    # SUB HEADERS
    pdf.set_x(start_x + col_widths[0])
    pdf.set_font("PoppinsRegular", size=12)
    pdf.cell(col_widths[1], cell_height, "Listening", border=0, align="C")
    pdf.cell(col_widths[2], cell_height, "Reading", border=0, align="C")
    pdf.cell(col_widths[3], cell_height, "Spoken prod.", border=0, align="C")
    pdf.cell(col_widths[4], cell_height, "Spoken inter.", border=0, align="C")
    pdf.ln(cell_height)

    # DRAW TOP BORDER for data row
    pdf.line(start_x, pdf.get_y(), start_x + total_width, pdf.get_y())

    # DATA ROW
    pdf.set_font("PoppinsBold", size=12)
    pdf.set_x(start_x)
    pdf.cell(col_widths[0], cell_height, lang.upper(), border=0, align="C", fill=True)
    pdf.set_font("PoppinsRegular", size=12)
    pdf.cell(col_widths[1], cell_height, listening, border=0, align="C", fill=True)
    pdf.cell(col_widths[2], cell_height, reading, border=0, align="C", fill=True)
    pdf.cell(col_widths[3], cell_height, spoken_prod, border=0, align="C", fill=True)
    pdf.cell(col_widths[4], cell_height, spoken_inter, border=0, align="C", fill=True)
    pdf.cell(col_widths[5], cell_height, writing, border=0, align="C", fill=True)
    pdf.ln(cell_height)

    # DRAW BOTTOM BORDER for data row
    pdf.line(start_x, pdf.get_y(), start_x + total_width, pdf.get_y())

    pdf.ln(2)  # spacing after table

def generate_cv_now(u_name,u_b_place,u_phone,u_email,u_website,u_linkedin,u_about, u_company,u_c_place,u_position,u_start_date,u_end_date,u_status_date,u_c_description,u_education_start_date,u_education_end_date,u_education_program,u_education_inititue,u_insititue_place,u_education_description,u_education_grade,u_mother_tongue,u_other_langauges,u_listeing,u_reading,u_spoken,u_spoken_inter,u_soft_skills,u_programming_skills,u_projects,u_links):
    pdf = FPDF()
    pdf.set_margins(0, 0, 0)
    pdf.add_page()
   
    # Fonts
    pdf.add_font("PoppinsLarger", "", "Poppins/Poppins-Bold.ttf", uni=True)
    pdf.add_font("PoppinsRegular", "", "Poppins/Poppins-Regular.ttf", uni=True)
    pdf.add_font("PoppinsBold", "", "Poppins/Poppins-SemiBold.ttf", uni=True)
    pdf.add_font("Emoji", "", "Noto_Color_Emoji/Symbola.ttf", uni=True)

    # Background Rect
    pdf.set_fill_color(0, 75, 128)
    pdf.rect(x=0, y=0, w=pdf.w, h=40, style='F')

    # Title
    pdf.set_font("PoppinsLarger", size=18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(ln=True, w=pdf.w, h=4, border=False)
    pdf.cell(5)
    user_name = u_name
    pdf.cell(w=pdf.get_string_width(user_name), h=13, txt=user_name, border=False, align="L", ln=True)

    # White line under title
    left_margin = 6
    right_margin = 6
    line_y = pdf.get_y()
    pdf.set_line_width(0.3)
    pdf.set_draw_color(255, 255, 255)
    pdf.line(left_margin, line_y, pdf.w - right_margin, line_y)

    pdf.cell(w=pdf.w, h=2, ln=True, border=False)
    pdf.cell(5)

    # Info Row 1
    height_cell = 7
    pdf.set_font("PoppinsBold", size=10)
    pdf.cell(w=28, h=height_cell, txt="Place of Birth:", border=False, align="C", ln=False)
    pdf.set_font("PoppinsRegular", size=10)
    pdf.cell(w=pdf.get_string_width(u_b_place), h=height_cell, txt=u_b_place, border=False, ln=False)

    pdf.cell(w=8, h=height_cell, txt="-", border=False, ln=False)
    pdf.set_font("PoppinsBold", size=10)
    pdf.cell(w=15, h=height_cell, txt="Phone:", border=False, align="C", ln=False)
    pdf.set_font("PoppinsRegular", size=10)
    pdf.cell(w=pdf.get_string_width(u_phone), h=height_cell, txt=u_phone, border=False, ln=False)

    pdf.cell(w=6, h=height_cell, txt="-", border=False, ln=False)
    pdf.set_font("PoppinsBold", size=10)
    pdf.cell(w=15, h=height_cell, txt="Email:", border=False, align="C", ln=False)
    pdf.set_font("PoppinsRegular", size=10)
    pdf.cell(w=pdf.get_string_width(u_email), h=height_cell, txt=u_email, border=False, ln=True)

    # Info Row 2
    pdf.cell(50)
    pdf.set_font("PoppinsBold", size=10)
    pdf.cell(w=20, h=height_cell, txt="Website:", border=False, align="C", ln=False)
    pdf.set_font("PoppinsRegular", size=10)
    if not u_website:
        pdf.cell(w=20, h=height_cell, txt="None", border=False, align="C", ln=False,
             link="https://haseebsagheer.com/")
    else:
        pdf.cell(w=20, h=height_cell, txt="None", border=False, align="C", ln=False,
             link=u_website)


    

    pdf.cell(10)
    pdf.cell(w=15, h=height_cell, txt="-", border=False, ln=False)
    pdf.set_font("PoppinsBold", size=10)
    pdf.cell(w=17, h=height_cell, txt="Linkedin:", border=False, align="C", ln=False)
    pdf.set_font("PoppinsRegular", size=10)
    pdf.cell(w=32, h=height_cell, txt="View Profile", border=False, ln=True,
             link=u_linkedin)

    # About Myself Section
    pdf.cell(w=5, h=7, ln=True)
    pdf.cell(5)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Emoji", size=12)
    pdf.cell(w=6.5, h=height_cell * 2, txt="◉", ln=False)

    pdf.set_font("PoppinsLarger", size=12)
    pdf.cell(w=pdf.w, h=height_cell * 2, txt="ABOUT MYSELF", ln=True, align="L")

    # Draw Line ABOVE the paragraph
    pdf.set_line_width(0.8)
    pdf.set_draw_color(0, 75, 128)
    line_y2 = pdf.get_y() - 3 # Current Y BEFORE paragraph
    pdf.line(left_margin + 7, line_y2, pdf.w - right_margin, line_y2)

    # Multi-line text
    pdf.set_font("PoppinsRegular", size=10)
    pdf.set_xy(left_margin + 6.5, pdf.get_y()-1)  # Add spacing below the line 

    pdf.multi_cell(
        w=pdf.w - (left_margin + 7) - right_margin,
        h=6,
        txt=fix_multiline_paragraph(u_about),
        border=False,
        align="L"
    )

    # Section heading
    pdf.cell(w=5, h=-1, ln=True)
    pdf.cell(5)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Emoji", size=12)
    pdf.cell(w=6.5, h=height_cell * 2, txt="◉", ln=False, border=False)
    pdf.set_font("PoppinsLarger", size=12)
    pdf.cell(w=pdf.w, h=height_cell * 2, txt="WORK EXPERIENCE", ln=True, align="L", border=False)
    pdf.set_text_color(0, 0, 50)

    # Section divider line
    line_y2 = pdf.get_y() - 3
    pdf.line(left_margin + 7, line_y2, pdf.w - right_margin, line_y2)
    pdf.set_font("PoppinsRegular", size=10)
    pdf.set_xy(pdf.x, pdf.get_y() - 1)

    
    for (e_company,e_place,e_position,e_start_date,e_end_date,e_status,e_description) in zip(u_company,u_c_place,u_position,u_start_date,u_end_date,u_status_date,u_c_description):
        end_date_new = "nothing"
        if not e_end_date or not e_end_date.strip():
            end_date_new = "Present"
        else:
            end_date_new = e_end_date

        generate_experience_section(pdf,e_company,e_place,e_position,e_start_date,end_date_new,e_description)
        

   

    # About Education and training section
    pdf.cell(w=5, h=4, ln=True)
    pdf.cell(5)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Emoji", size=12)
    pdf.cell(w=6.5, h=height_cell * 2, txt="◉", ln=False)

    pdf.set_font("PoppinsLarger", size=12)
    pdf.cell(w=pdf.w, h=height_cell * 2, txt="EDUCATION AND TRAINING", ln=True, align="L")

    # Draw Line ABOVE the paragraph
    pdf.set_line_width(0.8)
    pdf.set_draw_color(0, 75, 128)
    line_y2 = pdf.get_y() - 2 # Current Y BEFORE paragraph
    pdf.line(left_margin + 7, line_y2, pdf.w - right_margin, line_y2)
   #def generate_education_section(pdf, start_date, end_date, location, degree_title, institute_name, modules_text, final_grade):

    for (ed_start_date,ed_end_date,ed_i_location,ed_degree_title,ed_insitute_name,ed_module_text,ed_final_grade) in zip(u_education_start_date,u_education_end_date,u_insititue_place,u_education_program,u_education_inititue,u_education_description,u_education_grade):
        generate_education_section(pdf,ed_start_date,ed_end_date,ed_i_location,ed_degree_title,ed_insitute_name,ed_module_text,ed_final_grade)
    pdf.cell(w=5, h=-1, ln=True)
    pdf.cell(5)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Emoji", size=12)
    pdf.cell(w=6.5, h=height_cell * 2, txt="◉", ln=False)

    pdf.set_font("PoppinsLarger", size=12)
    pdf.cell(w=pdf.w, h=height_cell * 2, txt="LANGUAGE SKILLS", ln=True, align="L")

    # Draw Line ABOVE the paragraph
    pdf.set_line_width(0.8)
    pdf.set_draw_color(0, 75, 128)
    line_y2 = pdf.get_y() - 3 # Current Y BEFORE paragraph
    pdf.line(left_margin + 7, line_y2, pdf.w - right_margin, line_y2)
    pdf.set_font("PoppinsRegular",size=13)
    pdf.cell(w=12,h=3)
    pdf.cell(txt="Mother Tongue(s): ",w=pdf.get_string_width("Mother Tongue(s): "),h=height_cell)
    language = u_mother_tongue
    language= language.upper()
    pdf.set_font("PoppinsBold",size=12)
    pdf.cell(txt=language,w=pdf.get_string_width(language),h=height_cell,ln=True)
    pdf.cell(w=12,h=6)
    pdf.set_font("PoppinsRegular",size=12)
    pdf.cell(txt="Other Language(s):",w=pdf.get_string_width("Other Language(s):"),h=height_cell)
    pdf.set_xy(pdf.x,pdf.y+8)
    for (n_lang,n_list,n_reading,n_spoken,n_inter) in zip(u_other_langauges,u_listeing,u_reading,u_spoken,u_spoken_inter):

        count = 0
        if n_lang == "C1":
            count += 1
        if n_reading == "C1":
            count += 1
        if n_spoken == "C1":
            count += 1
        if n_inter == "C1":
            count += 1

  
     

    
        writing_test = "B1"
        if(count == 1):
         writing_test = "B1"
        elif(count == 2):
         writing_test = "B2"
        elif(count == 3):
         writing_test = "C1"
        elif(count == 4):
         writing_test = "C2"
        else:
         writing_test = "A2"
        
        render_language_skills_table(pdf,n_lang,n_list,n_reading,n_spoken,n_inter,writing_test)
    

    pdf.cell(w=5, h=2, ln=True)
    pdf.cell(5)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Emoji", size=12)
    pdf.cell(w=6.5, h=height_cell * 2, txt="◉", ln=False)

    pdf.set_font("PoppinsLarger", size=12)
    pdf.cell(w=pdf.w, h=height_cell * 2, txt="COMMUNICATION AND INTERPERSONAL SKILLS", ln=True, align="L")

    # Draw Line ABOVE the paragraph
    pdf.set_line_width(0.8)
    pdf.set_draw_color(0, 75, 128)
    line_y2 = pdf.get_y() - 2 # Current Y BEFORE paragraph
    pdf.line(left_margin + 7, line_y2, pdf.w - right_margin, line_y2)

    pdf.set_font("PoppinsBold", size=12)
    pdf.set_text_color(0,0,50)
    pdf.cell(12)
    pdf.cell(w=pdf.w, h=height_cell * 2, txt="Soft Skills", ln=True, align="L")

    # Draw Line ABOVE the paragraph
    pdf.set_line_width(0.5)
    pdf.set_draw_color(0, 75, 128)
    line_y2 = pdf.get_y() - 3 # Current Y BEFORE paragraph
    pdf.line(left_margin + 7, line_y2, pdf.w - right_margin, line_y2)
    pdf.set_font("PoppinsRegular", size=12)
    skills = u_soft_skills
    final_skills= skills.split(',')

    final_skills = list(map(str.strip,final_skills))
    pdf.set_xy(pdf.x,pdf.y+2)
    for item in final_skills:
        pdf.cell(16)
        pdf.cell(w=pdf.get_string_width("• "+item),h=height_cell,txt="• "+item,ln=True)

    pdf.cell(w=5, h=2, ln=True)
    pdf.cell(5)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Emoji", size=12)
    pdf.cell(w=6.5, h=height_cell * 2, txt="◉", ln=False)

    pdf.set_font("PoppinsLarger", size=12)
    pdf.cell(w=pdf.w, h=height_cell * 2, txt="PROGRAMMING SKILLS", ln=True, align="L")

    # Draw Line ABOVE the paragraph
    pdf.set_line_width(0.8)
    pdf.set_draw_color(0, 75, 128)
    line_y2 = pdf.get_y() - 2 # Current Y BEFORE paragraph
    pdf.line(left_margin + 7, line_y2, pdf.w - right_margin, line_y2)

    pdf.set_font("PoppinsBold", size=12)
    pdf.set_text_color(0,0,50)
    pdf.cell(12)
    pdf.cell(w=pdf.w, h=height_cell * 2, txt="Languages", ln=True, align="L")

    # Draw Line ABOVE the paragraph
    pdf.set_line_width(0.5)
    pdf.set_draw_color(0, 75, 128)
    line_y2 = pdf.get_y() - 3 # Current Y BEFORE paragraph
    pdf.line(left_margin + 7, line_y2, pdf.w - right_margin, line_y2)
    pdf.set_font("PoppinsRegular", size=12)
    language_skills = u_programming_skills
    language_final_skills= language_skills.split(',')

    language_final_skills = list(map(str.strip,language_final_skills))
    pdf.set_xy(pdf.x,pdf.y+2)
    for item in language_final_skills:
        pdf.set_x(20)
        pdf.cell(w=pdf.get_string_width("• " + item) + 1, h=height_cell, txt="• " + item, ln=True, border=False)

    pdf.set_y(pdf.get_y() + 2)

    # Projects Heading
    pdf.set_font("PoppinsBold", size=12)
    pdf.set_text_color(0, 0, 50)
    pdf.cell(12)
    pdf.cell(w=pdf.w, h=height_cell, txt="Projects", ln=True, align="L", border=False)

    # Blue line under heading
    pdf.set_line_width(0.5)
    pdf.set_draw_color(0, 75, 128)
    line_y2 = pdf.get_y() + 0.5
    pdf.line(left_margin + 7, line_y2, pdf.w - right_margin, line_y2)

    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font("PoppinsRegular",size=12)

    def add_project(pdf, data):
        pdf.set_x(left_margin + 6.5)
        pdf.multi_cell(
            w=pdf.w - (left_margin + 7) - right_margin,
            h=6,
            txt=data,
            border=False,
            align="L"
        )


    for project in u_projects:
        add_project(pdf,fix_multiline_paragraph(project))
   

    def add_link(pdf,link2):
        pdf.cell(12,4)
        pdf.set_font("PoppinsBold", size=12)
        pdf.cell(w=pdf.get_string_width("Link: "),h=height_cell,txt="Link: ")
        pdf.set_font("PoppinsRegular", size=12)
        pdf.cell(w=pdf.get_string_width(link2), h = height_cell, txt = link2,link=link2,ln=True)
    links = u_links
    for link in links:
        add_link(pdf,link)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    unique_id = uuid.uuid4().hex[:6]  # First 6 characters of UUID
    safe_name = u_name.replace(" ", "_")  # Replace spaces with underscores
    cv_name = f"CV_{safe_name}_{timestamp}_{unique_id}.pdf"
   
    pdf.output(cv_name)
    return cv_name


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/generate", methods=["POST"])
def generate():
    # Personal Information
    name = request.form.get('name')
    birthplace = request.form.get('birthplace')
    phone = request.form.get('phone')
    email = request.form.get('email')
    website = request.form.get('website')
    linkedin = request.form.get('linkedin')
    address = request.form.get('address')
    about = request.form.get('about')
  
    # Experience (multiple entries)
    exp_companies = request.form.getlist('exp_company[]')
    exp_locations = request.form.getlist('exp_location[]')
    exp_positions = request.form.getlist('exp_position[]')
    exp_starts = request.form.getlist('exp_start[]')
    exp_ends = request.form.getlist('exp_end[]')
    exp_currents = request.form.getlist('exp_current[]')
    exp_descriptions = request.form.getlist('exp_description[]')
  
    # Education (multiple entries)
    edu_institutes = request.form.getlist('edu_institute[]')
    edu_programs = request.form.getlist('edu_program[]')
    edu_locations = request.form.getlist('edu_location[]')
    edu_starts = request.form.getlist('edu_start[]')
    edu_ends = request.form.getlist('edu_end[]')
    edu_grades = request.form.getlist('edu_grade[]')
    edu_descriptions = request.form.getlist('edu_description[]')
      
    # Languages
    mother_tongue = request.form.get('mother_tongue')
    lang_names = request.form.getlist('lang_name[]')
    lang_listenings = request.form.getlist('lang_listening[]')
    lang_readings = request.form.getlist('lang_reading[]')
    lang_spokens = request.form.getlist('lang_spoken[]')
    lang_interactions = request.form.getlist('lang_interaction[]')
    
    # Skills
    soft_skills = request.form.get('soft_skills')
    programming_skills = request.form.get('programming_skills')
    
    # Projects (multiple entries)
    project_descriptions = request.form.getlist('project_description[]')
    
    # Additional Links (multiple entries)
    additional_links = request.form.getlist('additional_links[]')
    cv_name =    generate_cv_now(name,birthplace,phone,email,website,linkedin,about,exp_companies,exp_locations,exp_positions,exp_starts,exp_ends,exp_currents,exp_descriptions,
                                                    edu_starts,edu_ends,edu_programs,edu_institutes,edu_locations,edu_descriptions,edu_grades,
                                                            mother_tongue,lang_names,lang_listenings,lang_readings,lang_spokens,lang_interactions,soft_skills,programming_skills,project_descriptions,additional_links
                                                              
                                 
                             )
   
    return redirect(f"https://haseebsagheer.com/cv-generator/{cv_name}")


if __name__ == "__main__":
    app.run(debug =True,host='0.0.0.0',port=50001)
    
    