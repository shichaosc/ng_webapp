from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
import tempfile
from pdf2image import convert_from_path
import os
import io
import logging
from wand.image import Image
import PyPDF2
from django.conf import settings


logger = logging.getLogger(__name__)


def convert_pdf(f_pdf, filelist):
    (w, h) = landscape(A4)
    c = canvas.Canvas(f_pdf, pagesize = landscape(A4))
    for f_jpg in filelist:
        c.drawImage(f_jpg, 0, 0, w, h)
        c.showPage()
    c.save()
    return c._filename


def pdf_png(orig_path):
    re_list = []
    # orig_path_name = os.path.basename(orig_path).split('.')[0]
    # logger.debug(os.path.abspath(orig_path).split('.')[0])
    with tempfile.TemporaryDirectory() as path:
        images = convert_from_path(orig_path)
        for index, img in enumerate(images):
            img.save('%s-%s.png' % (os.path.abspath(orig_path), index))
            re_list.append('cw/%s-%s.png' % (os.path.basename(orig_path), index))


    return re_list


def pdf_page_to_png(src_pdf, pagenum = 0, resolution = 72,):
    '''
    Returns specified PDF page as wand.image.Image png.
    :param PyPDF2.PdfFileReader src_pdf: PDF from which to take pages.
    :param int pagenum: Page number to take.
    :param int resolution: Resolution for resulting png in DPI.
    '''
    dst_pdf = PyPDF2.PdfFileWriter()
    dst_pdf.addPage(src_pdf.getPage(pagenum))

    pdf_bytes = io.BytesIO()
    dst_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    img = Image(file = pdf_bytes, resolution = resolution)
    img.convert("png")

    return img


def convert(path,resolution=72,):
    '''
    Saves each page from a specified PDF as a png image (pdf_name{page_index}.png)
    :param str pdf_name : PDF file name (in the same directory of this script)
    :param int resolution : resolution of the output png_s in DPI
    '''
    pdf_name = os.path.basename(path)
    base_name = pdf_name.split('.')[0]
    path = os.path.dirname(path)
    src_pdf = PyPDF2.PdfFileReader(open(os.path.join(path,pdf_name), "rb"))
    png_list = []
    for i in range(src_pdf.getNumPages()):
        temp=pdf_page_to_png(src_pdf,i,resolution)
        temp.save(filename=os.path.join(path,base_name+str(i)+'.png'))
        png_list.append('cw/%s%s.png' % (base_name, str(i)))
    return png_list
