# Domain registry
from tau_bench_extend.domains.healthcare import tasks as healthcare
from tau_bench_extend.domains.insurance import tasks as insurance
from tau_bench_extend.domains.ecommerce import tasks as ecommerce

DOMAIN_REGISTRY = {
    "healthcare": {
        "get_tasks": healthcare.get_tasks,
        "get_tools": healthcare.get_tools,
        "get_policy": healthcare.get_policy,
    },
    "insurance": {
        "get_tasks": insurance.get_tasks,
        "get_tools": insurance.get_tools,
        "get_policy": insurance.get_policy,
    },
    "ecommerce": {
        "get_tasks": ecommerce.get_tasks,
        "get_tools": ecommerce.get_tools,
        "get_policy": ecommerce.get_policy,
    },
}


def get_domain(name: str) -> dict:
    if name not in DOMAIN_REGISTRY:
        raise ValueError(f"Unknown domain '{name}'. Available: {list(DOMAIN_REGISTRY.keys())}")
    return DOMAIN_REGISTRY[name]
