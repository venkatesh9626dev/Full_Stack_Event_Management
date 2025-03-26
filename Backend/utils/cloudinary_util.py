import config
from cloudinary import uploader,exceptions as cloudinary_exception
from shared import generic_enum

from fastapi import status


from fastapi import HTTPException

def upload_file(file):
    try:
        if file.content_type not in {member.value for member in generic_enum.AllowedFileTypes}:
            raise HTTPException(status_code=415, detail="Only JPG and PNG files are allowed")

        upload_result = uploader.upload(file.file)
        return upload_result["secure_url"]

    except cloudinary_exception.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Cloudinary API error: {str(e)}")
    
    except HTTPException as http_err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Cloudinary API error: {str(http_err)}")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Cloudinary API error: {str(e)}")
