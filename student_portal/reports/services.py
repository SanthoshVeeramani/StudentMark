from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from io import BytesIO
from examinations.services import compute_student_result_for_examination

def generate_marksheet_pdf(student_profile, examination, school_info=None):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    school_name = school_info.get("name", "My Institution") if school_info else "My Institution"
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 30 * mm, school_name)
    if school_info and school_info.get("address"):
        c.setFont("Helvetica", 9)
        c.drawCentredString(width / 2, height - 36 * mm, school_info.get("address"))

    x_left = 20 * mm
    y = height - 50 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x_left, y, f"Name: {student_profile.user.get_full_name()}")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(x_left, y, f"Admission No: {student_profile.admission_number}")
    c.drawString(x_left + 80 * mm, y, f"Roll No: {student_profile.roll_number}")
    y -= 6 * mm
    c.drawString(x_left, y, f"Class: {examination.classroom.name}")
    c.drawString(x_left + 80 * mm, y, f"Exam: {examination.name}")

    y -= 12 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x_left, y, "Subject")
    c.drawString(x_left + 70 * mm, y, "Marks")
    c.drawString(x_left + 100 * mm, y, "Internal")
    c.drawString(x_left + 125 * mm, y, "Practical")
    c.drawString(x_left + 150 * mm, y, "Total")
    y -= 6 * mm
    c.line(x_left, y, width - x_left, y)
    y -= 6 * mm

    result = compute_student_result_for_examination(examination, student_profile)
    marks = result["marks"]
    c.setFont("Helvetica", 10)
    for m in marks:
        if y < 40 * mm:
            c.showPage()
            y = height - 30 * mm
        c.drawString(x_left, y, m.subject.name)
        c.drawRightString(x_left + 95 * mm, y, f"{m.marks_obtained}")
        c.drawRightString(x_left + 125 * mm, y, f"{m.internal_marks}")
        c.drawRightString(x_left + 150 * mm, y, f"{m.practical_marks}")
        c.drawRightString(x_left + 180 * mm, y, f"{m.total_marks}")
        y -= 6 * mm

    y -= 8 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x_left, y, f"Total: {result['total_obtained']} / {result['max_total']}")
    y -= 6 * mm
    c.drawString(x_left, y, f"Percentage: {result['percentage']}%")
    c.drawString(x_left + 80 * mm, y, f"Grade: {result['grade']}")

    y -= 20 * mm
    c.line(x_left, y, x_left + 60 * mm, y)
    c.drawString(x_left, y - 5, "Class Teacher")
    c.line(x_left + 90 * mm, y, x_left + 150 * mm, y)
    c.drawString(x_left + 90 * mm, y - 5, "Principal")

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
