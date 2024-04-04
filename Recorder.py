import tkinter as tk
import requests
import datetime
import time
import os

class GoProControl:
  GOPRO_IP = "10.5.5.9"  # Default IP for GoPro
  GOPRO_URL = f"http://{GOPRO_IP}"
  GOPRO_PASSWORD = "your_gopro_password"
  start_time = 0
  end_time = 0
  def read_logFile(self):
    with open("goproLogs.txt", "r") as f:
      content = f.read()
    return content
  
  def write_logFile(self, content):
    with open("goproLogs.txt", "a") as f:
      f.write(f'{content}\n')
    return "Done"

  def send_gopro_command(self, path):
      try:
          url = f"{self.GOPRO_URL}{path}"
          response = requests.get(url)
          if response.status_code == 200:
              print(f"Command executed successfully: {path}")
          else:
              print(f"Failed to execute command: {path}, Status Code: {response.status_code}")
      except Exception as e:
          print(f"Error sending command: {e}")

  def start_recording(self):
      self.send_gopro_command("/gp/gpControl/command/shutter?p=1")
      self.start_time = datetime.datetime.now()
      self.write_logFile(f"Recording started at {self.start_time}")
      print(f"Recording started at {self.start_time}")

  def stop_recording(self):
      self.send_gopro_command("/gp/gpControl/command/shutter?p=0")
      self.end_time = datetime.datetime.now()
      self.write_logFile(f"Recording stopped at {self.end_time}")
      self.write_logFile(f'Video Named Saved as: {self.end_time}.mp4')
      print(f"Recording stopped at {self.end_time}")
  
  def getEndTime(self):
    return self.end_time



class App:
  def __init__(self, root):
    self.root = root
    self.go_pro_control = GoProControl()
    self.root.title("GoPro Recording App")

    # Page 1 widgets
    self.page1 = tk.Frame(self.root)
    self.duration_label = tk.Label(self.page1, text="Duration (seconds):")
    self.duration_label.pack(side="top", fill="x", padx=5, pady=5)

    self.duration_entry = tk.Entry(self.page1)
    self.duration_entry.pack(side="top", fill="x", padx=5, pady=5)

    self.start_button = tk.Button(self.page1, text="Start Recording", command=self.start_recording)
    self.start_button.pack(side="top", fill="x", padx=5, pady=5)
    self.log_button = tk.Button(self.page1, text="Open Logfile", command=self.read_logFile)
    self.log_button.pack(side="top", fill="x", padx=5, pady=5)

    # Page 2 widgets
    self.page2 = tk.Frame(self.root)
    self.timer_label = tk.Label(self.page2, text="Recording 0 seconds left")  # Initial timer label
    self.timer_label.pack(side="top", fill="x", padx=5, pady=5)
    self.stop_button = tk.Button(self.page2, text="Stop Recording", command=self.stop_recording)
    self.stop_button.pack(side="top", fill="x", padx=5, pady=5)

    # Page 3 after recording stopped and donwloads video
    self.page3 = tk.Frame(self.root)
    self.downloading_label = tk.Label(self.page3, text="Downloading video 0%")
    self.downloading_label.pack(side="top", fill="x", padx=5, pady=5)
    self.goHome = tk.Button(self.page3, text="Go Home", command=self.goHome)
    self.goHome.pack(side="top", fill="x", padx=5, pady=5)
    self.openLogFile = tk.Button(self.page3, text="Open Logfile", command=self.openLogFile)
    self.openLogFile.pack(side="top", fill="x", padx=5, pady=5)
    self.openVideoFolder = tk.Button(self.page3, text="Open Video Folder", command=self.openVideoFolder)
    self.openVideoFolder.pack(side="top", fill="x", padx=5, pady=5)

    self.logFile = tk.Frame(self.root)
    self.logContent = tk.Label(self.logFile, text=self.go_pro_control.read_logFile())
    self.logFile.pack(side="top", fill="both", expand=True)
    self.goHome = tk.Button(self.logFile, text="Go Home", command=self.goHome)
    self.goHome.pack(side="top", fill="x", padx=5, pady=5)
    self.openLogFile = tk.Button(self.logFile, text="Open Logfile", command=self.openLogFile)
    self.openLogFile.pack(side="top", fill="x", padx=5, pady=5)

    # Initially, show page 1 and hide page 2
    self.page1.pack(side="top", fill="both", expand=True)
    self.page2.pack_forget()
    self.page3.pack_forget()
    self.logFile.pack_forget()

  def start_recording(self):

    # Update timer label and start countdown
    if self.duration_entry.get():
        # Get the duration value from the entry
        duration = int(self.duration_entry.get())
        self.timer = duration
        self.update_timer()
        self.go_pro_control.start_recording()
    else:
        self.go_pro_control.start_recording()

    # Switch to page 2
    self.page1.pack_forget()
    self.page2.pack(side="top", fill="both", expand=True)
  
  def getRecentVideo(self):
    mediaListurl = "http://10.5.5.9/gp/gpMediaList"
    time.sleep(5)
    medias = requests.get(mediaListurl).json()
    baseUrl = "http://10.5.5.9/videos/DCIM"
    folderName = medias['media'][0]['d']
    fileName = medias['media'][0]['fs'][-1]['n']
    recentVideo = f'{baseUrl}/{folderName}/{fileName}'
    return recentVideo

  def downloadVideo(self):
    
    fileUrl = self.getRecentVideo()
    # Download the latest media file
    r = requests.get(fileUrl, stream=True)
    total_size = int(r.headers.get('content-length', 0))
    downloaded_size = 0
    filename = self.go_pro_control.getEndTime()
    if not(os.path.exists("videos")):
      os.makedirs("videos")
    if os.path.exists(f"videos/{filename}.mp4"):
      filename = f"{filename}_1"
    with open(f"videos/{filename}.mp4", "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
                downloaded_size += len(chunk)
                percentage = int((downloaded_size / total_size) * 100)
    self.page2.pack_forget()
    self.page3.pack(side="top", fill="both", expand=True)
    self.downloading_label.config(text="\nDownloaded Video to videos folder")
     
  def stop_recording(self):
    print("Stopping recording...")
    self.timer_label.config(text="Downloading video")
    self.go_pro_control.stop_recording()
    self.downloadVideo()

  def update_timer(self):
    if self.timer > 0:
      self.timer -= 1
      self.timer_label.config(text=f"Recording {self.timer} seconds left")
      self.root.after(1000, self.update_timer)
    else:
      self.stop_recording()

  def read_logFile(self):
    self.page1.pack_forget()
    self.page2.pack_forget()
    self.logFile.pack(side="top", fill="both", expand=True)
    logContent = self.go_pro_control.read_logFile()
    if logContent:
      self.logContent.config(text=logContent)
    else:
      self.logContent.config(text="No logs available")
    self.logContent.pack(side="top", fill="both", expand=True)
  def goHome(self):
    self.logFile.pack_forget()
    self.page2.pack_forget()
    self.page3.pack_forget()
    self.page1.pack(side="top", fill="both", expand=True)
  def openLogFile(self):
    # Opens logfile in default text editor
    os.system("open goproLogs.txt")
  def openVideoFolder(self):
    # Opens video folder in Finder
    os.system("open videos")

# Create the main window and start the app
root = tk.Tk()
app = App(root)
root.mainloop()
