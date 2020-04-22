import csv
import os
import shutil

orignal1 = os.path.join(os.getcwd(),"Tutorien","Tutorium4","Standorte.csv")
temp1 = os.path.join(os.getcwd(),"Tutorien","Tutorium4","StandorteTemp.csv")
orignal2 = os.path.join(os.getcwd(),"Tutorien","Tutorium4","Absatzorte.csv")
temp2 = os.path.join(os.getcwd(),"Tutorien","Tutorium4","AbsatzorteTemp.csv")

shutil.copyfile(orignal1,temp1)
shutil.copyfile(orignal2,temp2)
IsCorrectFormat = True
with open(orignal1 ,newline="", encoding="utf-8") as f:
    IsCorrectFormat = f.read(1) != '"'

if IsCorrectFormat:
    with open(temp1, encoding="utf-8-sig") as csv_file, open(orignal1, "w",newline="", encoding="utf-8") as out_file:
        csv_reader = csv.DictReader(csv_file, delimiter=";")
        csv_writer = csv.DictWriter(out_file, delimiter=",", fieldnames=csv_reader.fieldnames)
        csv_writer.writeheader()
        for row in csv_reader:
            csv_writer.writerow(row)

    with open(temp2, encoding="utf-8-sig") as csv_file, open(orignal2, "w",newline="", encoding="utf-8") as out_file:
        csv_reader = csv.DictReader(csv_file, delimiter=";")
        csv_writer = csv.DictWriter(out_file, delimiter=",", fieldnames=csv_reader.fieldnames)
        csv_writer.writeheader()
        for row in csv_reader:
            csv_writer.writerow(row)

else:
    with open(temp1, encoding="utf-8") as in_file, open(orignal1, "w",newline="", encoding="utf-8") as out_file:
        allLines= in_file.readlines()
        for line in allLines:
            out_file.write(line[1:-2]+"\n")
    with open(temp2, encoding="utf-8") as in_file, open(orignal2, "w",newline="", encoding="utf-8") as out_file:
        allLines= in_file.readlines()
        for line in allLines:
            out_file.write(line[1:-2]+"\n")

os.remove(temp1)
os.remove(temp2)