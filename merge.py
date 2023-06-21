import os
from tools.jtools import load_json, save_dict_json


def merge(dataset_paths, outputs: str = "outputs"):
    all_annotations = {}
    # path -> list
    all_names = "_".join(dataset_paths.keys())
    save_json_index_path = os.path.join(outputs, f"{all_names}.json")

    for name, dataset_path in dataset_paths.items():
        index = load_json(dataset_path)

        for keyid, dico in index.items():
            path = dico["path"]
            duration = dico["duration"]
            if path in all_annotations:
                assert duration == all_annotations[path]["duration"]
            else:
                all_annotations[path] = {"duration": duration, "annotations": []}

            for ann in dico["annotations"]:
                new_ann = ann.copy()
                new_ann["seg_id"] = f"{name}_{ann['seg_id']}"
                all_annotations[path]["annotations"].append(new_ann)

    save_dict_json(all_annotations, save_json_index_path)
    print(f"Saving the merged annotations to {save_json_index_path}")


if __name__ == "__main__":
    outputs = "outputs"
    dataset_paths = {
        dataset: os.path.join(outputs, dataset + ".json")
        for dataset in ["babel", "humanml3d", "kitml"]
    }

    merge(dataset_paths)
