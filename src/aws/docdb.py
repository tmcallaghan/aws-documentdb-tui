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
