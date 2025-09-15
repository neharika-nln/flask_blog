from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

FOLDER_ID = "138q20HHJFDxrQ87t5fVf-nOBYqc5jJxf"

def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("credentials.json")
    
    if gauth.credentials is None:
        raise Exception("No valid credentials found. Run auth flow locally first.")
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    return GoogleDrive(gauth)

def upload_to_drive(file_path, filename, folder_id=FOLDER_ID):
    drive = authenticate_drive()
    file = drive.CreateFile({
        "title": filename,
        "parents": [{"id": folder_id}]
    })
    file.SetContentFile(file_path)
    file.Upload()
    return f"https://drive.google.com/uc?export=view&id={file['id']}"



# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive

# FOLDER_ID = "138q20HHJFDxrQ87t5fVf-nOBYqc5jJxf"
# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()  # Opens browser once for login

# drive = GoogleDrive(gauth)

# def upload_to_drive(file_path, filename, folder_id):
#     file = drive.CreateFile({
#         "title": filename,
#         "parents": [{"id": "138q20HHJFDxrQ87t5fVf-nOBYqc5jJxf"}]  # folder ID of your shared folder
#     })
#     file.SetContentFile(file_path)
#     file.Upload()
#     return f"https://drive.google.com/uc?export=view&id={file['id']}"
