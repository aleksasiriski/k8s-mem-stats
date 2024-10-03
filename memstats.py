import json
from collections import defaultdict


def convert_memory(memory_str):
    if memory_str.endswith("Gi"):
        return int(memory_str[:-2]) * 1024
    elif memory_str.endswith("Mi"):
        return int(memory_str[:-2])
    return 0


def extract_base_key(key):
    parts = key.split("-")
    if len(parts) > 2:
        return "-".join(parts[:-2])
    return key


def extract_namespace(key):
    return key.split("/")[0]


def remove_namespace_prefix(key):
    return key.split("/", 1)[-1]


def is_job_pod(pod_name):
    # A simple heuristic to filter out pods likely managed by Jobs
    parts = pod_name.split("-")
    if len(parts) > 2 and parts[-2].isdigit() and len(parts[-1]) == 5:
        return True  # Matches the typical Job pod name pattern
    return False


def process_memory_data(input_file, output_file):
    with open(input_file, "r") as f:
        data = json.load(f)

    memory_dict = defaultdict(lambda: defaultdict(int))
    namespace_totals = defaultdict(int)
    total_memory = 0

    for item in data:
        for key, value in item.items():
            pod_name = remove_namespace_prefix(key)
            if is_job_pod(pod_name):
                continue  # Skip pods from Kubernetes Jobs
            namespace = extract_namespace(key)
            base_key = extract_base_key(pod_name)
            memory_value = convert_memory(value)
            memory_dict[namespace][base_key] += memory_value
            namespace_totals[namespace] += memory_value
            total_memory += memory_value

    output_data = {
        "total": f"{total_memory}Mi",
        **{
            namespace: {
                "total": f"{total_memory}Mi",
                "pods": [{pod: f"{memory}Mi"} for pod, memory in pods.items()],
            }
            for namespace, total_memory, pods in (
                (ns, ns_total, memory_dict[ns])
                for ns, ns_total in namespace_totals.items()
            )
        },
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)


# Process mem_req.json and mem_used.json
process_memory_data("mem_req.json", "mem_req_stats.json")
process_memory_data("mem_used.json", "mem_used_stats.json")
