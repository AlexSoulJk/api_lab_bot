import os.path
import subprocess
import datetime
import shutil
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googledrive.helper import get_credentials
from dotenv import load_dotenv

load_dotenv()

def upload_backup_to_drive(file_name, file_path, credentials):
    folder_id = os.getenv("BACKUP_FOLDER_ID")
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'parents': [folder_id], 'name': file_name + '.gpg'}
    media = MediaFileUpload(file_path, mimetype='application/octet-stream')
    service.files().create(body=file_metadata, media_body=media, fields='id, parents').execute()


def download_docs_from_drive(folder_id, credentials, output_dir):
    service = build('drive', 'v3', credentials=credentials)
    query = f"'{folder_id}' in parents"
    response = service.files().list(q=query).execute()
    items = response.get('files', [])

    if items:
        for item in items:
            file_id = item['id']
            file_name = item['name']
            print(f"Downloading file {file_name} ({file_id})")

            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                done, _ = downloader.next_chunk()

            with open(os.path.join(output_dir, file_name), 'wb') as f:
                f.write(fh.getbuffer())

            print(f"Completed download of file {file_name} ({file_id})")


def create_db_backup(backup_directory, DB_USER, DB_NAME, passphrase):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    dump_file = f'db_{timestamp}.sql'
    dump_path = os.path.join(backup_directory, dump_file)
    archive_file = f'{dump_path[:-4]}.tar.gz'

    subprocess.run([
        'docker', 'exec', 'api_lab_bot-database-1', 'pg_dump', '-U', DB_USER, DB_NAME
    ], stdout=open(dump_path, 'w'), check=True)

    shutil.make_archive(archive_file.replace('.tar.gz', ''), 'gztar', backup_directory)
    subprocess.run(f'gpg --symmetric --batch --passphrase {passphrase} {archive_file}', shell=True, check=True)

    return archive_file


def main():
    credentials = get_credentials()

    backup_directory = 'BACKUP'
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)

    fold_id = os.getenv("FOLDER_ID")

    download_docs_from_drive(fold_id, credentials, backup_directory)

    DB_USER = os.getenv("DB_USER")
    DB_NAME = os.getenv("DB_NAME")

    archive_file = create_db_backup(backup_directory, DB_USER, DB_NAME, passphrase=os.getenv("MY_PASS_PHRASE"))

    upload_backup_to_drive(archive_file, f"{archive_file}.gpg", credentials)
    shutil.rmtree(backup_directory)


if __name__ == "__main__":
    main()
