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
    ["gcc", "-E", "-dD", "-CC"] + sys.argv,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
).stdout.read()

class Flags:
  ENTER_INCLUDE = "1"
  LEAVE_INCLUDE = "2"
  SYSTEM_HEADER = "3"
  EXTERN_C = "4"

def print_include(abspath):
  for prefix in gcc_default_includes:
    if abspath.startswith(prefix):
      print("#include <{}>".format(abspath[len(prefix)+1:]))
      return

in_user_code = False
for line in gcc_E_str.decode("utf-8").split("\n"):
  match = re.match("^# \d+ \"(.*)\"([ \d]*)$", line)

  if not match:
    if in_user_code:
      print(line)
    continue

  if not match.group(2):
    continue

  is_sys_hdr = Flags.SYSTEM_HEADER in match.group(2)

  if in_user_code and is_sys_hdr:
    print_include(match.group(1))

  in_user_code = not is_sys_hdr
