import os
from tika import parser



def extract_text_from_pdf(pdf_fp, pdf_fn):
    fn = os.path.splitext(pdf_fn)[0] + '.txt'
    full_txt_file_path = os.path.join(txt_file_dir_path, fn)
    # print(full_txt_file_path)
    pdf_contents = parser.from_file(pdf_fp)
    with open(full_txt_file_path, 'w') as txt_file:
        print("Writing contents to " + full_txt_file_path)
        txt_file.write(pdf_contents['content'])



# txt_file_dir_path = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/stanford/text_files'
# pdf_dir_path = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/stanford/pdf_files'

txt_file_dir_path = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/wiki/text_files'
pdf_dir_path = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/wiki/pdf_files'

# pdf_files = os.listdir(pdf_dir_path)
# # ex_fn = pdf_files[4]
# # ex_full_fp = os.path.join(pdf_dir_path, ex_fn)
# # print(f"Convert PDF to Text: {ex_full_fp}")
# # extract_text_from_pdf(ex_full_fp, ex_fn)
# for fn in pdf_files:
#     c_full_fp = os.path.join(pdf_dir_path, fn)
#     print(f"Convert PDF to Text: {c_full_fp}")
#     extract_text_from_pdf(c_full_fp, fn)

# pdf_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/wiki/pdf_files/Applications of artificial intelligence - Wikipedia.pdf'
# fn = 'Applications of artificial intelligence - Wikipedia.pdf'
# extract_text_from_pdf(pdf_fp, fn)
