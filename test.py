from src.tools.head import check_resume
from src.tools.parser import PDFParser

parser = PDFParser()
resume = parser.parse("src/knowledges/Ilia_Klichuk_CV_ML_Engineer_eng.pdf")
# print(resume)

resume_check = check_resume(resume)
print(resume_check)