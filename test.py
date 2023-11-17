import shutil
import os

# Specify the file names
old_file = 'test.py'
new_file = 'new.py'

# Copy the content of new.py to main.py
shutil.copy(new_file, old_file)

# Remove new.py if you want to replace it entirely
os.remove(new_file)
