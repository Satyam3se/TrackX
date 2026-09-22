import sys
path = r"anpr_kaggle\automatic-number-plate-recognition.py"
with open(path, "r", encoding="utf-8") as f: text = f.read()
text = text.replace("os.system('pip ", "os.system(f'{sys.executable} -m pip ")
text = text.replace("os.system('python ", "os.system(f'{sys.executable} ")
with open(path, "w", encoding="utf-8") as f: f.write("import sys\n" + text)
