from pathlib import Path
from typing import List, Dict


class DataEntry:
    def __init__(self, filename: str, name: str, left_x: int, left_y: int, right_x: int, right_y: int, mouth_x: int, mouth_y: int):
        self.filename = filename
        self.name = name
        self.left_x = left_x
        self.left_y = left_y
        self.right_x = right_x
        self.right_y = right_y
        self.mouth_x = mouth_x
        self.mouth_y = mouth_y


def read_annotation(annotation_file: str) -> List[DataEntry]:
    """
    Read the entries from data_dir, remove any entry
    with lack of field.
    """

    annotation_file_path = Path(annotation_file)
    data_dir = annotation_file_path.parent

    entries = []
    for line in annotation_file_path.open('r'):
        fields = line.split(' ')

        filename = data_dir / fields[1]
        name = fields[3]
        right_x, right_y = fields[11], fields[12]
        left_x, left_y = fields[14], fields[15]
        mouth_x, mouth_y = fields[17], fields[18]

        if 'Inf' in [left_x, left_y,
                     right_x, right_y,
                     mouth_x, mouth_y]:
            continue

        left_x = int(left_x)
        left_y = int(left_y)
        right_x = int(right_x)
        right_y = int(right_y)
        mouth_x = int(mouth_x)
        mouth_y = int(mouth_y)
        filename = str(filename)
        name = name.upper()

        entry = DataEntry(filename, name, left_x, left_y, right_x, right_y, mouth_x, mouth_y)
        entries.append(entry)

    return entries


def construct_name2id(annotations: List[DataEntry]) -> Dict[str, int]:
    max_id = 0
    name2id = {}
    for annotation in annotations:
        if annotation.name not in name2id:
            name2id[annotation.name] = max_id
            max_id += 1

    return name2id


def write_fold(annotations: List[DataEntry], name2id: Dict[str, int], output_file: str):
    with Path(output_file).open('w') as file:
        annotations = sorted(annotations, key=lambda annot: name2id[annot.name])
        lines = (f'{annot.filename} {name2id[annot.name]}\n' for annot in annotations)
        file.writelines(lines)


annotation_file = './data_CTai/annotations_ctai.txt'
annotations = read_annotation(annotation_file)
sample_count = len(annotations)
name2id = construct_name2id(annotations)

train_ratio = 0.8
gal_ratio = 0.1
probe_ratio = 0.1

train_annotations = annotations[:int(len(annotations) * train_ratio)]
gal_annotations = annotations[int(len(annotations) * train_ratio):int(len(annotations) * (train_ratio + gal_ratio))]
probe_annotations = annotations[int(len(annotations) * (train_ratio + gal_ratio)):]

Path('chimp_splits/fold_1/').mkdir(parents=True, exist_ok=True)
write_fold(train_annotations, name2id, 'chimp_splits/train_1.txt')
write_fold(gal_annotations, name2id, 'chimp_splits/fold_1/gal_1.txt')
write_fold(probe_annotations, name2id, 'chimp_splits/fold_1/probe_1.txt')
