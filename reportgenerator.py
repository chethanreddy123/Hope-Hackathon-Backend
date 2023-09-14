import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, PageTemplate, BaseDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, Frame, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfgen import canvas



from io import BytesIO

def get_first_six_words(sentence):
    words = sentence.split()
    first_six_words = " ".join(words[:6])
    return first_six_words


def create_pain_scale_graph(painscales, dates):
    fig = go.Figure(data=go.Scatter(x=dates, y=painscales, mode='lines+markers'))
    fig.update_layout(title_text='Pain Scale Graph', xaxis_title='Date', yaxis_title='Pain Scale')
    fig.write_image("painGraph.png")

def create_daywise_exercise_table(doctor_prescription):
    data = [["Date", "Pain Scale", "Comments"]]
    for entry in doctor_prescription:
        data.append([entry["Date"], entry["PainScale"], entry["Comments"]])

    # Build and apply table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
    ])

    # Create the table
    table = Table(data)
    table.setStyle(table_style)

    return table

def create_exercises_table(exercises):
    data = [["Sr No", "Name of Exercise", "Reps", "Sets", "No of Days", "Next Review"]]
    for exercise in exercises:
        data.append([exercise["SrNo"], get_first_six_words(exercise["NameOfExercise"]), exercise["Reps"],
                     exercise["Sets"], exercise["NoOfDays"], exercise["NextReview"]])

    # Build and apply table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
    ])

    # Create the table
    table = Table(data)
    table.setStyle(table_style)

    return table

def create_pdf_discharge(name, age, gender, referred_by, chief_complaint, previous_treatment, diagnosis, duration,
               treatment_given, treatment_dates, painscales, home_advice, next_review,
               doctor_prescription, exercises):
    print(treatment_dates, painscales)
    doc = SimpleDocTemplate("hospital_report.pdf", pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Create custom page template with borders
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='test', frames=frame, onPage=draw_page_border)
    doc.addPageTemplates([template])

    # Styles for the headings and subheadings
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=18, textColor=colors.blue, alignment=1)
    heading_style = ParagraphStyle("Heading1", parent=styles["Heading2"], fontSize=14, textColor=colors.blue, alignment=1)
    subheading_style = ParagraphStyle("Subheading", parent=styles["Heading3"], spaceAfter=6)

    # Data for the main table
    data = [
        ["Name", name],
        ["Age", age],
        ["Gender", gender],
        ["Referred by", referred_by],
        ["Chief Complaint", chief_complaint],
        ["Previous Treatment Taken", previous_treatment],
        ["Diagnosis", diagnosis],
        ["Duration", duration],
        ["Treatment Given", treatment_given],
        ["Home Advice", home_advice],
        ["Next Review", next_review],
    ]

    # Create the pain scale graph
    create_pain_scale_graph(painscales, treatment_dates)
    pain_graph = Image('painGraph.png', width=6*inch, height=4*inch)

    # Create the Daywise exercise analysis table
    exercise_table = create_daywise_exercise_table(doctor_prescription)

    # Create the exercises table
    exercises_table = create_exercises_table(exercises)

    # Logo adding part:
    hospital_logo = Image('hospital_logo.png', width=4*inch, height=1*inch)

    # Build the PDF content for the first page
    first_page_content = []

    first_page_content.append(hospital_logo)

    # Address and line break
    first_page_content.append(Paragraph("Intermediate Ring Road, Domlur", heading_style))
    first_page_content.append(Paragraph("Embassy Golf Links Road, Challaghatta", heading_style))
    first_page_content.append(Paragraph("Bengaluru, Karnataka 560071", heading_style))
    first_page_content.append(Spacer(1, 0.2*inch))  # Line break
    first_page_content.append(Paragraph("Daily Treatment summary", heading_style))
    first_page_content.append(Spacer(1, 0.2*inch))
    # Add the main table
    main_table = Table(data)
    main_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
    ]))
    first_page_content.append(main_table)

     # Add the exercises table
    first_page_content.append(Paragraph("Exercise Plan:", heading_style))
    first_page_content.append(exercises_table)

    # Line break after the Daywise exercise analysis table
    first_page_content.append(Spacer(1, 0.5*inch))

    # Combine the content for the first page
    story = first_page_content

    # Build the PDF content for the second page
    second_page_content = []
    # Add the pain scale graph on the second page
    second_page_content.append(Paragraph("<b>Pain Scale Graph during the Treatment Period:</b>", subheading_style))
    second_page_content.append(pain_graph)


    
    # Add the Daywise exercise analysis table
    second_page_content.append(Paragraph("Daywise Treatment Analysis:", heading_style))
    second_page_content.append(exercise_table)

    # Combine the content for the second page
    story += [PageBreak()] + second_page_content

    doc.build(story)

def draw_page_border(canvas, doc):
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(2)
    canvas.rect(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, stroke=1)


def create_billing_slip_rehab(bill_no, patient_id, date, name, address, cell_no, amount_paid, package_program):
    doc = SimpleDocTemplate("billing_slip_rehab.pdf", pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Build the PDF content
    content = []

    # Logo and Address
    logo = "hospital_logo.png"
    address_lines = [
        "Intermediate Ring Road, Domlur", 
       "Embassy Golf Links Road, Challaghatta", 
       "Bengaluru, Karnataka 560071"
    ]
    content.append(Spacer(1, 0.2*inch))
    content.append(Paragraph("<img src='{}' width='250' height='50'/>".format(logo), styles['Center']))
    for address_line in address_lines:
        content.append(Paragraph(address_line, styles['Center']))
    content.append(Spacer(1, 0.2*inch))

    # Bill Information
    bill_info = [
        ["Bill No:", bill_no],
        ["Patient ID:", patient_id],
        ["Date:", date],
        ["Name:", name],
        ["Address:", address],
        ["Cell No:", cell_no],
        ["Amount Paid:", amount_paid],
        ["Package & Program:", package_program],
    ]
    bill_table_data = [[Paragraph(cell, styles['Normal']) for cell in row] for row in bill_info]
    bill_table = Table(bill_table_data, colWidths=[1.2*inch, 3.8*inch])
    bill_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    content.append(bill_table)
    content.append(Spacer(1, 0.2*inch))  # Line break

    # Additional Sections (if needed)
    # ...

    # Footer
    footer_text = "Thank you for choosing our services. For any queries, please contact us at 04182 - 222527."
    footer = Paragraph(footer_text, styles['Normal'])
    content.append(footer)

    doc.build(content)





def create_billing_slip(bill_no, patient_id, date, name, address, cell_no, amount_paid, no_days):
    doc = SimpleDocTemplate("billing_slip.pdf", pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Build the PDF content
    content = []

    # Logo and Address
    logo = "hospital_logo.png"
    address_lines = [
         "Intermediate Ring Road, Domlur", 
       "Embassy Golf Links Road, Challaghatta", 
       "Bengaluru, Karnataka 560071"
    ]
    content.append(Spacer(1, 0.2*inch))
    content.append(Paragraph("<img src='{}' width='250' height='50'/>".format(logo), styles['Center']))
    for address_line in address_lines:
        content.append(Paragraph(address_line, styles['Center']))
    content.append(Spacer(1, 0.2*inch))

    # Bill Information
    bill_info = [
        ["Bill No:", bill_no],
        ["Patient ID:", patient_id],
        ["Date:", date],
        ["Name:", name],
        ["Address:", address],
        ["Cell No:", cell_no],
        ["Amount Paid:", amount_paid],
        ["Number of Days", no_days],
    ]
    bill_table_data = [[Paragraph(cell, styles['Normal']) for cell in row] for row in bill_info]
    bill_table = Table(bill_table_data, colWidths=[1.2*inch, 3.8*inch])
    bill_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    content.append(bill_table)
    content.append(Spacer(1, 0.2*inch))  # Line break

    # Additional Sections (if needed)
    # ...

    # Footer
    footer_text = "Thank you for choosing our services. For any queries, please contact us at 04182 - 222527."
    footer = Paragraph(footer_text, styles['Normal'])
    content.append(footer)

    doc.build(content)

# Sample data for billing slip
bill_no = "BS12345"
patient_id = "PAT12345"
date = "2023-07-28"
name = "John Doe"
address = "123 Main Street, Cityville"
cell_no = "9876543210"
amount_paid = "$200.00"
no_days = "10"

# Get sample stylesheet
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Center', alignment=1))

# Generate the billing slip in PDF format
create_billing_slip(bill_no, patient_id, date, name, address, cell_no, amount_paid, no_days)