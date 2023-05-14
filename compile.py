import os
import shutil
from distutils.dir_util import copy_tree

fileNames = ["main", "macros"]
copyFiles = ["data", "Images", "settings.json", "main.py", "definitions.py", "kNearestNeighbors.py"]
dontDelete = ["Tesseract-OCR", "mainMK9.exe", "macros.exe"]
copyTo = "D:\Dropbox\Shellshockbot"
file_executed_in = os.getcwd()

try: shutil.rmtree(f'{file_executed_in}/dist')
except: pass
os.mkdir(f'{file_executed_in}/dist')

for cf in copyFiles:
    try: shutil.copyfile(f'{file_executed_in}/{cf}', f'{file_executed_in}/dist/{cf}')
    except: copy_tree(f'{file_executed_in}/{cf}', f'{file_executed_in}/dist/{cf}')

for root, dirs, files in os.walk(copyTo):
    dirs[:] = [d for d in dirs if d not in dontDelete]
    files[:] = [f for f in files if f not in dontDelete]
    for f in files:
        os.unlink(os.path.join(root, f))
    for d in dirs:
        shutil.rmtree(os.path.join(root, d))

copy_tree(f'{file_executed_in}/dist', copyTo)

for fn in fileNames:
    os.system(f'pyinstaller --onefile {fn}.py')
    print("finished compiling", fn)
    shutil.move(f'{file_executed_in}/dist/{fn}.exe', f'{copyTo}/{fn}.exe')

shutil.rmtree(f'{file_executed_in}/dist')

print("finished the process")