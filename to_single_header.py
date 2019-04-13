import re
import subprocess
import sys

gcc_default_import_str = subprocess.Popen(
    ["gcc", "-E", "-Wp,-v", "-xc++", "/dev/null"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
).stderr.read()

gcc_default_imports = [
    line.strip()
    for line in gcc_default_import_str.decode("utf-8").split("\n")
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

sys_depth = 0
in_user_code = False
for line in gcc_E_str.decode("utf-8").split("\n"):
  match = re.match("^# \d+ \"(.*)\"( \d)*$", line)
  if match:
    if match.group(2):
      flags = line.split('"')[2].split()
      if Flags.ENTER_INCLUDE in flags:
        sys_depth += 1
        if Flags.SYSTEM_HEADER in flags and sys_depth == 1:
          source_path = match.group(1)
          for imp in gcc_default_imports:
            if source_path.startswith(imp):
              inc = match.group(1)[len(imp)+1:]
              print("#include <{}>".format(inc))
              break

      if Flags.LEAVE_INCLUDE in flags:
        sys_depth -= 1

      in_user_code = (Flags.SYSTEM_HEADER not in flags)

  elif in_user_code:
    print(line)
