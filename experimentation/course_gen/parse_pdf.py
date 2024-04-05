import os
from tika import parser


# def extract_text_from_pdfs_recursively(dir):
#     for root, dirs, files in os.walk(dir):
#         for file in files:
#             path_to_pdf = os.path.join(root, file)
#             [stem, ext] = os.path.splitext(path_to_pdf)
#             if ext == '.pdf':
#                 print("Processing " + path_to_pdf)
#                 pdf_contents = parser.from_file(path_to_pdf)
#                 path_to_txt = stem + '.txt'
#                 with open(path_to_txt, 'w') as txt_file:
#                     print("Writing contents to " + path_to_txt)
#                     txt_file.write(pdf_contents['content'])


# supp_files_dir = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/supplementary_material'
# pdf_fp = os.path.join(supp_files_dir, 'pdf_files/CS_161_Computer_Security_Symmetric_Cryptography.pdf')
# pdf_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/supplementary_material/second/pdf_files/CS_161_Computer_Security_Symmetric_Cryptography.pdf'
pdf_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/supplementary_material/second/pdf_files/Symmetric-key algorithm - Wikipedia.pdf'
[stem, ext] = os.path.splitext(pdf_fp)
pdf_contents = parser.from_file(pdf_fp)
path_to_txt = stem + '.txt'
with open(path_to_txt, 'w') as txt_file:
    print("Writing contents to " + path_to_txt)
    txt_file.write(pdf_contents['content'])

