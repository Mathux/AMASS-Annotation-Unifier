import os

from tqdm import tqdm

from tools.jtools import load_json, save_dict_json
from tools.amass import load_amass_npz, compute_duration
from tools.kitml import load_mmm_csv, load_kit_mocap_annotation

from sanitize_text import sanitize
from tools.saving import store_keyid


def process_kitml(amass_path: str, kitml_path: str, kitml_process_folder: str, outputs: str = "outputs"):
    amasspath2kitml_path = os.path.join(kitml_process_folder, "amass-path2kitml.json")
    if not os.path.exists(amasspath2kitml_path):
        raise FileNotFoundError("You should launch the cmd 'python kitml_text_preprocess.py' first")

    os.makedirs(outputs, exist_ok=True)
    save_json_index_path = os.path.join(outputs, "kitml.json")

    original_dico = load_json(amasspath2kitml_path)

    dico = {}
    for keyid, path in tqdm(original_dico.items()):
        csv_path = os.path.join(kitml_path, keyid + "_fke.csv")
        mmm = load_mmm_csv(csv_path)

        npz_path = os.path.join(amass_path, path)
        smpl_data = load_amass_npz(npz_path)

        len_seq = len(mmm)
        len_amass_seq = len(smpl_data["trans"])

        if len_seq != len_amass_seq:
            print(f"Excluding {keyid}, as there is a mismatch between AMASS and MMM motions")
            continue

        start = 0.0
        duration = compute_duration(smpl_data)
        # whole sequence for KIT-ML
        end = duration

        texts = load_kit_mocap_annotation(kitml_path, keyid)

        # drop the sequence
        if not texts:
            continue

        annotations = []
        for idx, text in enumerate(texts):
            text = sanitize(text)
            seg_id = f"{keyid}_{idx}"

            element = {
                # to save the correspondance
                # with the original KIT-ML dataset
                "seg_id": f"{keyid}_{idx}",
                "text": text,
                "start": start,
                "end": end
            }

            if not text.isascii():
                raise TypeError("The text should not have non-ascii characters")

            annotations.append(element)

        # at least one
        if len(annotations) >= 1:
            store_keyid(dico, keyid, path, duration, annotations)

    # saving the annotations
    save_dict_json(dico, save_json_index_path)
    print(f"Saving the annotations to {save_json_index_path}")


if __name__ == "__main__":
    amass_path = "datasets/AMASS/"
    kitml_path = "datasets/kit-mocap/"

    kitml_process_folder = "kitml_process"
    process_kitml(amass_path, kitml_path, kitml_process_folder)
