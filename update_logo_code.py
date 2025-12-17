
import re
import os

file_path = 'lxc-bot-v1.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update LOGO_URL default
# Find LOGO_URL definition and change default
# LOGO_URL = os.getenv('LOGO_URL', 'https://i.imgur.com/xSsIERx.png')
content = re.sub(
    r"LOGO_URL = os\.getenv\('LOGO_URL', '[^']+'\)", 
    "LOGO_URL = os.getenv('LOGO_URL', 'attachment://logo.jpg')", 
    content
)

# 2. Add file attachment to send/edit methods
# We want to match existing 'embed=' kwarg and prepend 'file=..., '
# We target calls to send, send_message, edit_message, edit, reply, followup.send

# Regex explanation:
# Look for function calls that likely send messages.
# We trust that 'embed=' is used as a keyword argument for sending messages in this codebase.
# We replace `embed=` with `file=discord.File("logo.jpg", filename="logo.jpg"), embed=`
# We use a negative lookbehind to ensure we don't double-patch if I run this twice? No, simple script.

# Pattern finds:
# (send|edit_message|reply|followup\.send|user\.send|owner\.send)\(.*?embed=
# Since regex across lines is hard, and simple string replacement of "embed=" is dangerous (assignments).
# But we know the code style is fairly standard.

# Only replace "embed=" when it looks like a kwarg (preceded by ( or , or space)
# AND followed by something.
# But we only want to do it for "sending" functions. 

# A safer approach for this specific file structure:
# Replace "embed=" with "file=discord.File('logo.jpg', filename='logo.jpg'), embed="
# BUT only in lines that contain "await ". 
# Most sends are "await ...". 
# Assignments "embed = ..." don't have "await".

def replacement(match):
    return match.group(0).replace('embed=', 'file=discord.File("logo.jpg", filename="logo.jpg"), embed=')

# Regex: find lines with "await" and "embed="
# We iterate line by line to be safe?
lines = content.split('\n')
new_lines = []
for line in lines:
    if 'await ' in line and ('ctx.send' in line or 'interaction.response' in line or 'followup.send' in line or 'user.send' in line or 'owner.send' in line or '.edit' in line):
        if 'embed=' in line:
            # Check if not already patched
            if 'discord.File("logo.jpg"' not in line:
                line = line.replace('embed=', 'file=discord.File("logo.jpg", filename="logo.jpg"), embed=')
    new_lines.append(line)

content = '\n'.join(new_lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully refactored lxc-bot-v1.py to use local logo file.")
