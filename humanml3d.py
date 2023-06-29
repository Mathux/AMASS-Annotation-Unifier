import os
import pandas

from tqdm import trange

from tools.jtools import load_json, save_dict_json
from tools.amass import load_amass_npz, compute_duration
from sanitize_text import sanitize
from tools.saving import store_keyid


def load_humanml3d_txt(path):
    with open(path) as ff:
        return [x.strip() for x in ff.readlines()]


def process_humanml3d(amass_path: str, humanml3d_path: str, outputs: str = "outputs"):
    os.makedirs(outputs, exist_ok=True)
    save_json_index_path = os.path.join(outputs, "humanml3d.json")

    humanml3d_index_path = os.path.join(humanml3d_path, 'index.csv')
    index_file = pandas.read_csv(humanml3d_index_path)
    texts_path = os.path.join(humanml3d_path, "HumanML3D/texts/")

    dico = {}
    print("For now, skipping humanact12 motions")
    for i in trange(len(index_file)):
        element = index_file.iloc[i]

        source_path = element["source_path"]
        start_frame = element["start_frame"]

        end_frame = element["end_frame"]
        new_name = element["new_name"]

        path = source_path.replace("./pose_data/", "").replace(".npy", "")

        if "humanact12" in path:
            continue
            path = path.replace("humanact12/humanact12/", "humanact12/")

        keyid = new_name.replace(".npy", "")

        # The FPS for H3D is always set to 20
        fps = 20
        # Store in seconds to not depend on FPS
        start = start_frame / fps
        end = end_frame / fps

        # compute offset in second
        # to align the annotations
        # see https://github.com/EricGuo5513/HumanML3D/blob/main/raw_pose_processing.ipynb
        # at the last cell
        # the data is trimmed before beeing sliced
        # same here, by saving the start and end with an offset

        if 'Eyes_Japan_Dataset' in path or 'MPI_HDM05' in path:
            offset = 3
        elif 'TotalCapture' in path or 'MPI_Limits' in path:
            offset = 1
        elif 'Transitions_mocap' in path:
            offset = 0.5
        else:
            offset = 0

        start += offset
        end += offset

        npz_path = os.path.join(amass_path, path + ".npz")
        smpl_data = load_amass_npz(npz_path)
        duration = compute_duration(smpl_data)

        if end_frame == -1:
            # should happend only in humanact12
            assert "humanact12" in source_path
            # replace by the entire duration
            end = duration

        tpath = os.path.join(texts_path, keyid + ".txt")
        txts = load_humanml3d_txt(tpath)

        annotations = []
        for idx, txt in enumerate(txts):
            text, _, start_seg, end_seg = txt.split("#")
            text = sanitize(text)

            element = {
                # to save the correspondance
                # with the original Humanml3D dataset
                "seg_id": f"{keyid}_{idx}",
                "text": text
            }

            # remove nan
            # same process that Guo et al.
            start_seg = 0.0 if start_seg == "nan" else float(start_seg)
            end_seg = 0.0 if end_seg == "nan" else float(end_seg)

            # fix problem when they are swapped
            start_seg, end_seg = min(start_seg, end_seg), max(start_seg, end_seg)

            if start_seg == end_seg and start_seg != 0.0:
                # normally this is incorrect and should
                # count as a 1-frame annotation..
                # but we "correct" this by taking the whole segment instead
                # so put both as 0.0
                start_seg = 0.0
                end_seg = 0.0

            if start_seg == end_seg and start_seg == 0.0:
                # take the whole segment
                element["start"] = start
                element["end"] = end
            else:
                seg_duration = end_seg - start_seg
                element["start"] = start + start_seg
                element["end"] = min(end, element["start"] + seg_duration)

            annotations.append(element)

        # at least one
        if len(annotations) >= 1:
            store_keyid(dico, keyid, path, duration, annotations)

    # saving the annotations
    save_dict_json(dico, save_json_index_path)
    print(f"Saving the annotations to {save_json_index_path}")


if __name__ == "__main__":
    amass_path = "datasets/AMASS/"
    humanml3d_path = "datasets/HumanML3D/"
    process_humanml3d(amass_path, humanml3d_path)
