from ninja import Router, File
from ninja.files import UploadedFile
from pdf2image import convert_from_bytes
from PIL import Image
import io
import os
from django.http import JsonResponse
from base64 import b64encode
from dispenser.settings import CONVERTER_KEY

converter_router = Router()

@converter_router.post("/pdf-to-jpg")
def convert_pdf_to_jpg(request, file: UploadedFile = File(...)):
    """PDF 파일을 JPG 이미지로 변환하는 API

    Args:
        request (HttpRequest): HTTP 요청 객체
        file (UploadedFile): 변환할 PDF 파일. multipart/form-data 형식으로 전송되어야 함

    Returns:
        JsonResponse: 변환된 이미지 정보를 포함한 JSON 응답
            {
                "images": [
                    {
                        "filename": "원본파일명_page_1.jpg",  # 변환된 이미지 파일명
                        "content_type": "image/jpeg",         # 파일 타입
                        "data": "base64로 인코딩된 이미지..."  # 실제 이미지 데이터
                    },
                    ...
                ],
                "total_pages": 3  # PDF의 총 페이지 수
            }

    Raises:
        Exception: PDF 변환 실패 시 에러 메시지 반환
            {
                "error": "에러 메시지"
            }

    요청 헤더:
        Authorization: API 인증 키 (필수)

    예시:
        curl -X POST "http://your-domain/api/converter/pdf-to-jpg" \
            -H "Authorization: your-api-key" \
            -F "file=@document.pdf"

    주의사항:
        - PDF 파일의 각 페이지는 개별 JPG 이미지로 변환됩니다
        - 파일명은 원본 PDF 파일명을 기준으로 페이지 번호가 추가됩니다
        - 이미지 데이터는 base64로 인코딩되어 전송됩니다
        - 대용량 PDF 파일의 경우 변환 시간이 길어질 수 있습니다
    """
    try:
        if request.headers.get('Authorization') != CONVERTER_KEY:
            return {"error": "Invalid authorization key"}
        
        # 파일 이름에서 확장자를 제외한 부분 추출
        filename = os.path.splitext(file.name)[0]
        
        # PDF 파일을 이미지로 변환
        images = convert_from_bytes(file.read())
        
        # 변환된 이미지들을 저장할 리스트
        converted_images = []
        
        # 모든 페이지 처리
        for i, img in enumerate(images, start=1):
            # 이미지를 바이트로 변환
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            
            # 이미지를 base64로 인코딩
            img_base64 = b64encode(img_byte_arr.getvalue()).decode('utf-8')
            
            # 결과 추가
            converted_images.append({
                "filename": f"{filename}_page_{i}.jpg",
                "content_type": "image/jpeg",
                "data": img_base64
            })
        
        return JsonResponse({
            "images": converted_images,
            "total_pages": len(images)
        })
            
    except Exception as e:
        return {"error": str(e)} 