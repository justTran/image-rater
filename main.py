import os, csv, json, math
from imagePrediction import *

best_name, best = '', 0.0
worst_name, worst = '', 15.0

dir = "\\\\justin-nas\\Files\\Photos from Camera\\2024_11_11\\CR2"
with open(os.path.join(dir, 'data.csv'), 'w+', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Filename", "Score"])
    for file in [s for s in os.listdir(dir) if s.endswith(('.JPG', '.CR2'))]:
        a = imagePrediction(os.path.join(dir, file)).getValue()
        if a > best:
            best_name, best = file, a
        if a < worst:
            worst_name, worst = file, a

        writer.writerow([file, a])

print(f'\nBest: {best_name} | {best}')
print(f'Worst: {worst_name} | {worst}')