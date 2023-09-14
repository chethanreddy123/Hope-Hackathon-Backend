from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
import argparse
import subprocess


def create_billing_slip(bill_no, patient_id, date, name, address, cell_no, amount_paid, package_program):
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
        ["Package / Program", package_program],
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate billing slip.")
    parser.add_argument("bill_no", type=str, help="Bill number")
    parser.add_argument("patient_id", type=str, help="Patient ID")
    parser.add_argument("date", type=str, help="Date (YYYY-MM-DD)")
    parser.add_argument("name", type=str, help="Name")
    parser.add_argument("address", type=str, help="Address")
    parser.add_argument("cell_no", type=str, help="Cell number")
    parser.add_argument("amount_paid", type=str, help="Amount paid")
    parser.add_argument("package_program", type=str, help="Package program")

    args = parser.parse_args()

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))




    # Call the function with provided arguments
    create_billing_slip(
        args.bill_no,
        args.patient_id,
        args.date,
        args.name,
        args.address,
        args.cell_no,
        args.amount_paid,
        args.package_program
    )





