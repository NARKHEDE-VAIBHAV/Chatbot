import os
import glob

folder_path = r'C:\Users\ADITYA\Desktop\chatbot\test\img\hand'
image_files = glob.glob(os.path.join(folder_path, '*.*'))
image_files.sort()

for idx, file in enumerate(image_files, start=1):
    file_extension = os.path.splitext(file)[1]
    new_name = os.path.join(folder_path, f'img({idx}){file_extension}')
    os.rename(file, new_name)

print("Files renamed successfully.")
