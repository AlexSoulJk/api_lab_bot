import os.path
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", 'w') as token:
            token.write(creds.to_json())
    return creds


def upload_file_to_drive(file_name, file_path, credentials):
    folder_id = os.getenv("FOLDER_ID")
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'name': file_name,
                     'parents': [folder_id]}
    media = MediaFileUpload(file_path, mimetype='application/octet-stream')
    file = service.files().create(body=file_metadata, media_body=media, fields='id, parents').execute()
    return file.get('id')


