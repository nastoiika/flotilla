import subprocess
import os

# Путь к проекту
project_path = os.path.abspath(".")
report_json = os.path.join(project_path, "pylint_report.json")
report_html = os.path.join(project_path, "pylint_report.html")

# 1. Запуск Pylint с выводом в JSON
subprocess.run([
    "pylint",
    "timesyty",
    "--output-format=json",
    "--exit-zero"  # чтобы Pylint не возвращал код ошибки
], stdout=open(report_json, "w"))

# 2. Конвертация JSON в HTML
subprocess.run([
    "pylint-json2html",
    "-o",
    report_html,
    report_json
])

print(f"Отчет создан: {report_html}")
