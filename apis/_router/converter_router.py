from ninja import Router, File
from ninja.files import UploadedFile
from pdf2image import convert_from_bytes
import io
import os
from django.http import HttpResponse
from dispenser.settings import CONVERTER_KEY
converter_router = Router()

@converter_router.post("/pdf-to-jpg")
def convert_pdf_to_jpg(request, file: UploadedFile = File(...)):
    try:
        if request.headers.get('Authorization') != CONVERTER_KEY:
            return {"error": "Invalid authorization key"}
        
        # 파일 이름에서 확장자를 제외한 부분 추출
        filename = os.path.splitext(file.name)[0]
        
        # PDF 파일을 이미지로 변환
        images = convert_from_bytes(file.read())
        
        # 첫 페이지만 처리 (여러 페이지 처리가 필요하다면 수정 필요)
        if images:
            img = images[0]
            
            # 이미지를 바이트로 변환
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # JPG 파일로 응답 (원본 파일명 유지)
            response = HttpResponse(img_byte_arr, content_type='image/jpeg')
            response['Content-Disposition'] = f'attachment; filename={filename}.jpg'
            return response
            
        return {"error": "PDF 변환 실패"}
        
    except Exception as e:
        return {"error": str(e)} 