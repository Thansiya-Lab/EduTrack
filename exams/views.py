from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from courses.models import Enrollment
from courses.utils import get_module_lock_status
from .models import FinalExam, ExamResult


@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(FinalExam, id=exam_id)
    course = exam.course

    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, 'You must enroll in this course before taking the final exam.')
        return redirect('course_detail', slug=course.slug)

    _, all_cleared = get_module_lock_status(request.user, course)
    if not all_cleared:
        messages.error(request, 'Please complete and pass every module quiz before attempting the final exam.')
        return redirect('course_detail', slug=course.slug)

    if request.method == 'POST':
        total = exam.questions.count()
        correct = 0
        for q in exam.questions.all():
            selected_id = request.POST.get(f'question_{q.id}')
            if selected_id:
                try:
                    choice = q.choices.get(id=selected_id)
                    if choice.is_correct:
                        correct += 1
                except Exception:
                    pass
        score = (correct / total) * 100 if total else 0
        passed = score >= exam.pass_percentage
        result = ExamResult.objects.create(student=request.user, exam=exam, score_percent=score, passed=passed)
        return render(request, 'exams/result.html', {
            'exam': exam, 'score': score, 'correct': correct, 'total': total,
            'passed': passed, 'result': result
        })

    return render(request, 'exams/take_exam.html', {'exam': exam})


@login_required
def download_certificate(request, result_id):
    result = get_object_or_404(ExamResult, id=result_id, student=request.user)
    if not result.passed:
        return HttpResponse("Certificate not available. You have not passed this exam.", status=403)

    response = HttpResponse(content_type='application/pdf')
    filename = f"EduTrack_Certificate_{result.exam.course.title.replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    PURPLE = colors.HexColor('#5C2E6B')
    PURPLE_MID = colors.HexColor('#7E3F8F')
    GRAY = colors.HexColor('#555555')

    W, H = landscape(A4)
    p = canvas.Canvas(response, pagesize=landscape(A4))

    # ===== Simple border =====
    p.setStrokeColor(PURPLE)
    p.setLineWidth(2.2)
    p.rect(0.45 * inch, 0.45 * inch, W - 0.9 * inch, H - 0.9 * inch)
    p.setStrokeColor(PURPLE_MID)
    p.setLineWidth(0.6)
    p.rect(0.58 * inch, 0.58 * inch, W - 1.16 * inch, H - 1.16 * inch)

    # ===== Logo (icon + wordmark + tagline, all in one image) =====
    logo_path = str(settings.BASE_DIR / 'static' / 'images' / 'edutrack_logo_full.png')
    LOGO_H = 1.0 * inch
    LOGO_W = 1.0 * inch
    try:
        p.drawImage(logo_path, W / 2 - LOGO_W / 2, H - 0.85 * inch - LOGO_H, width=LOGO_W, height=LOGO_H,
                    preserveAspectRatio=True, mask='auto')
    except Exception:
        pass

    # ===== Title =====
    p.setFont('Times-Bold', 30)
    p.setFillColor(PURPLE)
    p.drawCentredString(W / 2, H - 2.35 * inch, 'CERTIFICATE OF COMPLETION')

    p.setStrokeColor(PURPLE_MID)
    p.setLineWidth(1)
    p.line(W / 2 - 1.5 * inch, H - 2.55 * inch, W / 2 + 1.5 * inch, H - 2.55 * inch)

    # ===== Body =====
    p.setFont('Helvetica', 13)
    p.setFillColor(GRAY)
    p.drawCentredString(W / 2, H - 3.05 * inch, 'This certifies that')

    try:
        full_name = result.student.profile.full_name
    except Exception:
        full_name = result.student.get_full_name() or result.student.username

    p.setFont('Times-BoldItalic', 30)
    p.setFillColor(PURPLE)
    p.drawCentredString(W / 2, H - 3.7 * inch, full_name)

    name_w = p.stringWidth(full_name, 'Times-BoldItalic', 30)
    p.setStrokeColor(PURPLE)
    p.setLineWidth(1)
    p.line(W / 2 - name_w / 2 - 0.4 * inch, H - 3.87 * inch, W / 2 + name_w / 2 + 0.4 * inch, H - 3.87 * inch)

    p.setFont('Helvetica', 13)
    p.setFillColor(GRAY)
    p.drawCentredString(W / 2, H - 4.3 * inch, 'has successfully completed the final examination of the course')

    p.setFont('Helvetica-Bold', 20)
    p.setFillColor(PURPLE_MID)
    p.drawCentredString(W / 2, H - 4.8 * inch, result.exam.course.title)

    score_text = f'Score: {result.score_percent:.1f}%      Category: {result.exam.course.category.name}'
    p.setFont('Helvetica', 12.5)
    p.setFillColor(GRAY)
    p.drawCentredString(W / 2, H - 5.25 * inch, score_text)

    # ===== Footer: certificate no / date (left) =====
    left_x = 1.1 * inch
    footer_y = 1.35 * inch
    cert_no = f"EDU-{result.taken_on.year}-{result.id:06d}"
    p.setFont('Helvetica-Bold', 10.5)
    p.setFillColor(PURPLE)
    p.drawString(left_x, footer_y + 0.35 * inch, 'Certificate No.')
    p.setFont('Helvetica', 10.5)
    p.setFillColor(GRAY)
    p.drawString(left_x, footer_y + 0.15 * inch, cert_no)

    p.setFont('Helvetica-Bold', 10.5)
    p.setFillColor(PURPLE)
    p.drawString(left_x, footer_y - 0.25 * inch, 'Date of Issue')
    p.setFont('Helvetica', 10.5)
    p.setFillColor(GRAY)
    p.drawString(left_x, footer_y - 0.45 * inch, result.taken_on.strftime('%d %B %Y'))

    # ===== Footer: signature (right, left blank) =====
    sig_w = 2.4 * inch
    sig_x2 = W - 1.1 * inch
    sig_x1 = sig_x2 - sig_w
    sig_y = footer_y + 0.15 * inch
    p.setStrokeColor(PURPLE)
    p.setLineWidth(1)
    p.line(sig_x1, sig_y, sig_x2, sig_y)
    p.setFont('Helvetica-Bold', 11)
    p.setFillColor(PURPLE)
    p.drawCentredString((sig_x1 + sig_x2) / 2, sig_y - 0.22 * inch, 'Authorized Signatory')
    p.setFont('Helvetica', 9.5)
    p.setFillColor(GRAY)
    p.drawCentredString((sig_x1 + sig_x2) / 2, sig_y - 0.4 * inch, 'EduTrack Administration')

    # ===== Tagline =====
    p.setFont('Helvetica', 11)
    p.setFillColor(PURPLE_MID)
    tagline = 'L E A R N      .      P R A C T I C E      .      A C H I E V E'
    p.drawCentredString(W / 2, 0.75 * inch, tagline)

    p.showPage()
    p.save()
    return response
