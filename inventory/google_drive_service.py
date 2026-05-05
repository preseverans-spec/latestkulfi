import base64
import io
import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload


DRIVE_SCOPE = ['https://www.googleapis.com/auth/drive']


def drive_is_enabled():
    return bool(os.getenv('GOOGLE_SERVICE_ACCOUNT_INFO', '').strip() and os.getenv('GOOGLE_DRIVE_FOLDER_ID', '').strip())


def _load_service_account_info():
    raw_info = os.getenv('GOOGLE_SERVICE_ACCOUNT_INFO', '').strip()
    if not raw_info:
        raise RuntimeError('GOOGLE_SERVICE_ACCOUNT_INFO is not set.')

    if raw_info.startswith('{'):
        return json.loads(raw_info)

    # Optional support for base64-encoded JSON.
    decoded = base64.b64decode(raw_info).decode('utf-8')
    return json.loads(decoded)


def _get_drive_service():
    info = _load_service_account_info()
    credentials = service_account.Credentials.from_service_account_info(info, scopes=DRIVE_SCOPE)
    return build('drive', 'v3', credentials=credentials, cache_discovery=False)


def upload_invoice_to_drive(file_obj, filename, content_type=None):
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '').strip()
    if not folder_id:
        raise RuntimeError('GOOGLE_DRIVE_FOLDER_ID is not set.')

    service = _get_drive_service()
    file_obj.seek(0)
    buffer = io.BytesIO(file_obj.read())

    media = MediaIoBaseUpload(
        buffer,
        mimetype=content_type or 'application/octet-stream',
        resumable=False,
    )
    metadata = {'name': filename, 'parents': [folder_id]}

    created = service.files().create(
        body=metadata,
        media_body=media,
        fields='id,name,mimeType',
    ).execute()

    return {
        'id': created.get('id', ''),
        'name': created.get('name', filename),
        'mime_type': created.get('mimeType', content_type or 'application/octet-stream'),
    }


def download_invoice_from_drive(file_id):
    service = _get_drive_service()

    metadata = service.files().get(fileId=file_id, fields='id,name,mimeType').execute()
    request = service.files().get_media(fileId=file_id)
    output = io.BytesIO()
    downloader = MediaIoBaseDownload(output, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    output.seek(0)

    return {
        'content': output.read(),
        'name': metadata.get('name', 'invoice-file'),
        'mime_type': metadata.get('mimeType', 'application/octet-stream'),
    }


def delete_invoice_from_drive(file_id):
    service = _get_drive_service()
    service.files().delete(fileId=file_id).execute()
