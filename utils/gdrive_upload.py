from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

FOLDER_ID = "138q20HHJFDxrQ87t5fVf-nOBYqc5jJxf"
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # Opens browser once for login
gauth.SaveCredentialsFile("credentials.json")

if gauth.credentials is None:
    # first-time only, locally run this to generate credentials.json
    gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("credentials.json")
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()


drive = GoogleDrive(gauth)

def upload_to_drive(file_path, filename, folder_id):
    file = drive.CreateFile({
        "title": filename,
        "parents": [{"id": "138q20HHJFDxrQ87t5fVf-nOBYqc5jJxf"}]  # folder ID of your shared folder
    })
    file.SetContentFile(file_path)
    file.Upload()
    return f"https://drive.google.com/uc?export=view&id={file['id']}"
