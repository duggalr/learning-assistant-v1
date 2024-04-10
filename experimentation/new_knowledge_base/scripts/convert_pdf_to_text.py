import os
from tika import parser



def extract_text_from_pdf(pdf_fp, pdf_fn, text_file_dir_path):
    fn = os.path.splitext(pdf_fn)[0] + '.txt'
    full_txt_file_path = os.path.join(text_file_dir_path, fn)
    # print(full_txt_file_path)
    pdf_contents = parser.from_file(pdf_fp)
    with open(full_txt_file_path, 'w') as txt_file:
        print("Writing contents to " + full_txt_file_path)
        txt_file.write(pdf_contents['content'])


# /Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/stanford/pdf_files
# /Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/stanford/text_files

# /Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/wiki/pdf_files
# /Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/wiki/text_files

# txt_file_dir_path = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/stanford/text_files'
# pdf_dir_path = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/stanford/pdf_files'

# txt_file_dir_path = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/wiki/text_files'
# pdf_dir_path = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/wiki/pdf_files'

tmp_file_dir_list = [
    {
        'text_dir_path': '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/stanford/text_files',
        'pdf_dir_path': '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/stanford/pdf_files'
    },
    {
        'text_dir_path': '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/wiki/text_files',
        'pdf_dir_path': '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/wiki/pdf_files'
    }
]

# for di in tmp_file_dir_list:
#     text_dir_path, pdf_dir_path = di['text_dir_path'], di['pdf_dir_path']
#     pdf_files = os.listdir(pdf_dir_path)
#     for fn in pdf_files:
#         c_full_fp = os.path.join(pdf_dir_path, fn)
#         print(f"Convert PDF to Text: {c_full_fp}")
#         extract_text_from_pdf(c_full_fp, fn, text_dir_path)


# pdf_fp = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/wiki/pdf_files/Applications of artificial intelligence - Wikipedia.pdf'
# fn = 'Applications of artificial intelligence - Wikipedia.pdf'
# extract_text_from_pdf(pdf_fp, fn)

# ex_fn = pdf_files[4]
# ex_full_fp = os.path.join(pdf_dir_path, ex_fn)
# print(f"Convert PDF to Text: {ex_full_fp}")
# extract_text_from_pdf(ex_full_fp, ex_fn)
