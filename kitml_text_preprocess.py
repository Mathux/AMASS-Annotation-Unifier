import os
import json

from tools.jtools import write_json


def fix_paths_kitml(amass_path: str, kitml_process_folder: str):
    # input
    json_path = os.path.join(kitml_process_folder, 'kitml_amass_path.json')

    # outputs
    corres_json_path = os.path.join(kitml_process_folder, 'amass-path2kitml.json')
    bad_amass_path = os.path.join(kitml_process_folder, 'kitml_not_found_amass.json')

    with open(json_path) as ff:
        dico = json.load(ff)

    nseq = len(dico)
    print(f"There are {nseq} sequences")

    count_bad = 0
    not_found_in_amass = {}
    def get_path_id(x, y):
        path = y["path"]
        identifier = y["identifier"]

        try_order = {
            "kit": ["KIT", "CMU", "EKUT"],
            "cmu": ["CMU", "EKUT", "KIT"]
        }

        sub_folders = try_order[identifier]
        for sub_folder in sub_folders:
            path_id = os.path.join(sub_folder, path)
            smpl_datapath = os.path.join(amass_path, path_id)

            if os.path.exists(smpl_datapath):
                return path_id

        nonlocal count_bad
        count_bad += 1
        # More probable missing one
        path_id = os.path.join(sub_folders[0], path)
        not_found_in_amass[x] = path_id
        return None

    paths = {
        x: z for x, y in dico.items() if (z := get_path_id(x, y))
    }

    print(f"There are {count_bad} sequences not found in AMASS")
    tot_path = len(paths)
    print(f"There are {tot_path} sequences found in AMASS")
    print()

    write_json(paths, corres_json_path)
    print(f"Saving correspondances (keyid -> AMASS) into {corres_json_path}")

    write_json(not_found_in_amass, bad_amass_path)
    print(f"Saving bad correspondances (missing motions in AMASS) into {bad_amass_path}")


if __name__ == "__main__":
    amass_path = "datasets/AMASS/"
    kitml_process_folder = "kitml_process"
    fix_paths_kitml(amass_path, kitml_process_folder)
