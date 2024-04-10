import os
from dotenv import load_dotenv, find_dotenv
import numpy as np
import faiss
import tiktoken
import pickle
from openai import OpenAI


if 'PRODUCTION' not in os.environ:
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)

API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(
    api_key = API_KEY,
)

def get_num_tokens_from_string(string, encoding_name):
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding


# bsize = 15000
# text_file_path_list = [
#     '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/stanford/text_files',
#     '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/wiki/text_files'
# ]

# final_file_list = []
# final_file_embedding_list = []
# for txt_dir_fp in text_file_path_list:
#     text_files_list = os.listdir(txt_dir_fp)    
    
#     for fn in text_files_list:
#         txt_full_fp = os.path.join(txt_dir_fp, fn)
#         txt_lines = open(txt_full_fp, 'r').read().strip()

#         for idx in range(0, len(txt_lines), bsize):
#             batch_txt = txt_lines[idx:idx+bsize].strip()
#             num_tokens = get_num_tokens_from_string(
#                 string = batch_txt,
#                 encoding_name = 'cl100k_base'
#             )
#             print(f"File: {fn} | Length of Text File: {len(batch_txt)} | Number of Tokens: {num_tokens}")

#             txt_embd = get_embedding(batch_txt)
#             final_file_list.append({
#                 'file_path': txt_full_fp,
#                 'batch_text': batch_txt,
#                 'num_tokens': num_tokens,
#                 'embedding': txt_embd
#             })
#             final_file_embedding_list.append(txt_embd)


# print(f"Total number of file batch text: {len(final_file_list)} | Total embeddings: {len(final_file_embedding_list)}")

# print(f"Pickling all Files...")

# with open('final_file_embedding_list.pkl', 'wb') as f:
#     pickle.dump(final_file_embedding_list, f)

# with open('final_file_list.pkl', 'wb') as f:
#     pickle.dump(final_file_list, f)


# print(f"Opening all Pickle Files...")

# with open('final_file_list.pkl', 'rb') as f:
#     final_file_list = pickle.load(f)

# with open('final_file_embedding_list.pkl', 'rb') as f:
#     final_file_embedding_list = pickle.load(f)

# np_embedding_list = np.array(final_file_embedding_list)
# embedding_dimension = np_embedding_list[0].shape[0]
# index = faiss.IndexFlatL2(embedding_dimension)
# index.add(np_embedding_list)
# print(index.ntotal)
# faiss.write_index(index, 'embedding.index')






# txt_file_dir_path = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/new_knowledge_base/stanford/text_files'
# text_files_list = os.listdir(txt_file_dir_path)

# final_file_list = []
# final_file_embedding_list = []
# for fn in text_files_list:
#     txt_full_fp = os.path.join(txt_file_dir_path, fn)
#     txt_lines = open(txt_full_fp, 'r').read().strip()    

#     for idx in range(0, len(txt_lines), bsize):
#         batch_txt = txt_lines[idx:idx+bsize].strip()
#         num_tokens = get_num_tokens_from_string(
#             string = batch_txt,
#             encoding_name = 'cl100k_base'
#         )
#         print(f"File: {fn} | Length of Text File: {len(batch_txt)} | Number of Tokens: {num_tokens}")

#         txt_embd = get_embedding(batch_txt)

#         final_file_list.append({
#             'file_path': txt_full_fp,
#             'batch_text': batch_txt,
#             'num_tokens': num_tokens,
#             'embedding': txt_embd
#         })
#         final_file_embedding_list.append(txt_embd)


# print(f"Pickling all Files...")

# with open('final_file_embedding_list.pkl', 'wb') as f:
#     pickle.dump(final_file_embedding_list, f)

# with open('final_file_list.pkl', 'wb') as f:
#     pickle.dump(final_file_list, f)


# print(f"Opening all Pickle Files...")

# with open('final_file_list.pkl', 'rb') as f:
#     final_file_list = pickle.load(f)

# with open('final_file_embedding_list.pkl', 'rb') as f:
#     final_file_embedding_list = pickle.load(f)


# np_embedding_list = np.array(final_file_embedding_list)
# embedding_dimension = np_embedding_list[0].shape[0]
# index = faiss.IndexFlatL2(embedding_dimension)
# index.add(np_embedding_list)
# print(index.ntotal)
# faiss.write_index(index, 'embedding.index')


