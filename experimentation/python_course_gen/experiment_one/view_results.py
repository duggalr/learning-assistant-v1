import os
import json


def view_json_results():
    output_dir_files = sorted(os.listdir(output_dir))
    for fn in output_dir_files:
        if '.json' in fn:
            output_json_fp = os.path.join(output_dir, fn)
            with open(output_json_fp) as f:
                d = json.load(f)
                print(fn)
                print(d)
                print('------------------------------------------------')



output_dir = '/Users/rahulduggal/Documents/personal_learnings/learning-assistant-v1/experimentation/python_course_gen/experiment_one/output_files/run_one'
view_json_results()

