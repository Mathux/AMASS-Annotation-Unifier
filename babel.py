import os

from tqdm import tqdm

from tools.jtools import load_json, save_dict_json
from tools.amass import load_amass_npz, compute_duration

from sanitize_text import sanitize
from tools.saving import store_keyid


def process_babel(amass_path: str, babel_path: str, mode: str = "all", outputs: str = "outputs"):
    assert mode in ["all", "seq", "seg"]
    os.makedirs(outputs, exist_ok=True)
    save_json_index_path = os.path.join(outputs, "babel.json")
    if mode != "all":
        save_json_index_path = os.path.join(outputs, f"babel_{mode}.json")

    train_path = os.path.join(babel_path, "train.json")
    val_path = os.path.join(babel_path, "val.json")

    train_dico = load_json(train_path)
    val_dico = load_json(val_path)

    all_dico = val_dico | train_dico

    dico = {}
    for keyid, babel_ann in tqdm(all_dico.items()):
        path = babel_ann["feat_p"]
        babel_ann = all_dico[keyid]

        keyid = keyid.zfill(5)

        path = "/".join(path.split("/")[1:])
        dur = babel_ann["dur"]

        npz_path = os.path.join(amass_path, path)
        smpl_data = load_amass_npz(npz_path)
        c_dur = compute_duration(smpl_data)
        duration = c_dur

        # check the duration are similar
        assert abs(c_dur - dur) < 0.25

        annotations = []
        # sequence_level annotations
        if mode in ["seq", "all"]:
            start = 0.0
            end = c_dur

            if not ((labels := babel_ann["seq_ann"]) and (labels := labels["labels"])):
                labels = []

            for idx, data in enumerate(labels):
                text = data["raw_label"]
                text = sanitize(text)

                element = {
                    # to save the correspondance
                    # with the original BABEL dataset
                    "seg_id": f"{keyid}_seq_{idx}",
                    "babel_id": data["seg_id"],
                    "text": text,
                    "start": start,
                    "end": end
                }
                annotations.append(element)

        if mode in ["seg", "all"]:
            if not ((labels := babel_ann["frame_ann"]) and (labels := labels["labels"])):
                labels = []

            for idx, data in enumerate(labels):
                text = data["raw_label"]
                text = sanitize(text)

                start = data["start_t"]
                end = data["end_t"]

                element = {
                    # to save the correspondance
                    # with the original BABEL dataset
                    "seg_id": f"{keyid}_seg_{idx}",
                    "babel_id": data["seg_id"],
                    "text": text,
                    "start": start,
                    "end": end
                }

                annotations.append(element)

        # at least one
        if len(annotations) >= 1:
            store_keyid(dico, keyid, path, duration, annotations)

    # saving the annotations
    save_dict_json(dico, save_json_index_path)
    print(f"Saving the annotations to {save_json_index_path}")


if __name__ == "__main__":
    amass_path = "datasets/AMASS/"
    babel_path = "datasets/babel-teach/"
    process_babel(amass_path, babel_path)
