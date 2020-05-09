import re
import subprocess
import sys

gcc_E_str = subprocess.Popen(
    ["g++", "-E", "-fdirectives-only", "-dI", "-CC"] + sys.argv,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
).stdout.read()

gcc_E_lines = gcc_E_str.decode("utf-8").split("\n")

class Flags:
  ENTER_INCLUDE = "1"
  LEAVE_INCLUDE = "2"
  SYSTEM_HEADER = "3"
  EXTERN_C = "4"

in_user_code = False
for i, line in enumerate(gcc_E_lines):
  if line.strip().startswith("#include") and re.match("^# 1 \".*\" 1$", gcc_E_lines[i+2]):
    continue

  match = re.match("^# \d+ \"(.*)\"([ \d]*)$", line)

  if match:
    if match.group(1) == u"<built-in>":
      in_user_code = False
    elif match.group(2):
      in_user_code = Flags.SYSTEM_HEADER not in match.group(2)
  else:
    if in_user_code:
      print(line)
