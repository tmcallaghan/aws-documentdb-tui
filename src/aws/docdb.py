from __future__ import annotations

from typing import Any

import boto3


def list_clusters(session: boto3.Session) -> list[dict[str, Any]]:
    client = session.client("docdb")
    clusters = []
    paginator = client.get_paginator("describe_db_clusters")
    for page in paginator.paginate():
        for cluster in page["DBClusters"]:
            clusters.append({
                "id": cluster["DBClusterIdentifier"],
                "status": cluster.get("Status", "unknown"),
                "engine_version": cluster.get("EngineVersion", ""),
                "instance_count": len(cluster.get("DBClusterMembers", [])),
                "storage_type": cluster.get("StorageType", "standard"),
                "parameter_group": cluster.get("DBClusterParameterGroup", ""),
            })
    return clusters


def get_cluster_detail(session: boto3.Session, cluster_id: str) -> dict[str, Any]:
    client = session.client("docdb")
    response = client.describe_db_clusters(DBClusterIdentifier=cluster_id)
    cluster = response["DBClusters"][0]

    param_group = cluster.get("DBClusterParameterGroup", "")
    param_group_status = "unknown"
    for member in cluster.get("DBClusterMembers", []):
        statuses = member.get("DBClusterParameterGroupStatus", "")
        if statuses:
            param_group_status = statuses
            break

    return {
        "id": cluster["DBClusterIdentifier"],
        "status": cluster.get("Status", "unknown"),
        "engine_version": cluster.get("EngineVersion", ""),
        "instance_count": len(cluster.get("DBClusterMembers", [])),
        "storage_type": cluster.get("StorageType", "standard"),
        "parameter_group": param_group,
        "parameter_group_status": param_group_status,
        "endpoint": cluster.get("Endpoint", ""),
        "reader_endpoint": cluster.get("ReaderEndpoint", ""),
        "port": cluster.get("Port", 27017),
    }


def list_instances(session: boto3.Session, cluster_id: str) -> list[dict[str, Any]]:
    client = session.client("docdb")
    instances = []
    paginator = client.get_paginator("describe_db_instances")
    for page in paginator.paginate(
        Filters=[{"Name": "db-cluster-id", "Values": [cluster_id]}]
    ):
        for inst in page["DBInstances"]:
            is_writer = False
            # Check cluster membership to determine role
            cluster_resp = inst.get("DBClusterIdentifier", "")
            instances.append({
                "id": inst["DBInstanceIdentifier"],
                "status": inst.get("DBInstanceStatus", "unknown"),
                "instance_class": inst.get("DBInstanceClass", ""),
                "az": inst.get("AvailabilityZone", ""),
                "region": session.region_name or "",
            })

    # Determine roles from cluster membership
    cluster_resp = client.describe_db_clusters(DBClusterIdentifier=cluster_id)
    members = cluster_resp["DBClusters"][0].get("DBClusterMembers", [])
    role_map = {
        m["DBInstanceIdentifier"]: "Writer" if m.get("IsClusterWriter") else "Reader"
        for m in members
    }
    for inst in instances:
        inst["role"] = role_map.get(inst["id"], "Unknown")

    return instances
