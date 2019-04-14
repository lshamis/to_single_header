import re
import subprocess
import sys

gcc_default_include_str = subprocess.Popen(
    ["gcc", "-E", "-Wp,-v", "-xc++", "/dev/null"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
).stderr.read()

gcc_default_includes = [
    line.strip()
    for line in gcc_default_include_str.decode("utf-8").split("\n")
    if line.startswith(" ")
]

gcc_E_str = subprocess.Popen(
    ["g++", "-E", "-fdirectives-only", "-dI", "-CC"] + sys.argv,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
).stdout.read()

class Flags:
  ENTER_INCLUDE = "1"
  LEAVE_INCLUDE = "2"
  SYSTEM_HEADER = "3"
  EXTERN_C = "4"

in_user_code = False
for line in gcc_E_str.decode("utf-8").split("\n"):
  match = re.match("^# \d+ \"(.*)\"([ \d]*)$", line)

  if match:
    if match.group(1) == u"<built-in>":
      in_user_code = False
    elif match.group(2):
      in_user_code = Flags.SYSTEM_HEADER not in match.group(2)
  else:
    if in_user_code:
      print(line)
