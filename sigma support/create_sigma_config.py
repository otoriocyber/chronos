import json
import os
import yaml
import argparse


def dump_mapping(path, all_fields):
    mapping = {}
    field_mapping = {}
    for field in all_fields:
        key = field.split(".")[-1]
        key = (key[0].upper() + key[1:])
        cur = field_mapping.get(key, None)
        if cur:
            field_mapping[key].append(field.replace("None.", ""))
        else:
            field_mapping[key] = [field.replace("None.", "")]
        if "user" in key:
            custom_key = "AccountName"
            account = field_mapping.get(custom_key, None)
            if account:
                field_mapping[custom_key].append(field.replace("None.", ""))
            else:
                field_mapping[custom_key] = [field.replace("None.", "")]

    mapping["fieldmappings"] = field_mapping

    with open(path, "w") as f:
        yaml.dump(mapping, f, default_flow_style=False)


def get_keys(data, prev=None, all_fields=None):
    if all_fields is None:
        all_fields = set()
    for k, v in data.items():
        pre = "{}.{}".format(prev, k)
        try:
            v = json.loads(v)
        except:
            pass
        if isinstance(v, dict):
            all_fields |= get_keys(v, pre, all_fields)
        else:
            all_fields.add(pre)

    return all_fields


def create_mapping_file(logs_path, result_path):
    all_fields = set()

    for root, dirs, files in os.walk(logs_path):
        for name in files:
            fp = os.path.join(root, name)
            print(fp)
            with open(fp) as f:
                data = json.load(f)
            for i in data:
                all_fields |= get_keys(i, None, None)

    for i in sorted(list(all_fields)):
        print(".".join(i.split(".")[1:]))

    print(len(all_fields))

    dump_mapping(result_path, all_fields)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", type=str, help='The path of the dumped logs')
    parser.add_argument("-o", "--output", type=str, help='The mapping file')
    args = parser.parse_args()

    create_mapping_file(args.source, args.output)


if __name__ == "__main__":
    main()


