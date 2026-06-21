#!/usr/bin/env python3
"""
Bulk loader for Oklahoma Juvenile Justice mock data into Elasticsearch.

Usage:
    python bulk_load.py --host https://your-cluster.es.cloud.io --api-key YOUR_API_KEY

    # Or with username/password:
    python bulk_load.py --host https://your-cluster.es.cloud.io --user elastic --password YOUR_PASSWORD

    # To delete and recreate indices first:
    python bulk_load.py --host https://your-cluster.es.cloud.io --api-key YOUR_API_KEY --recreate
"""

import argparse
import json
import sys
import os
from pathlib import Path
import urllib.request
import urllib.error
import ssl

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = SCRIPT_DIR / "data"
MAPPINGS_FILE = SCRIPT_DIR / "mappings.json"

INDICES = ["youth_profiles", "case_notes", "assessments", "outcomes"]


def make_request(url, method="GET", data=None, headers=None, auth=None, api_key=None):
    """Simple HTTP request wrapper using urllib (no dependencies)."""
    ctx = ssl.create_default_context()

    req = urllib.request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")

    if api_key:
        req.add_header("Authorization", f"ApiKey {api_key}")
    elif auth:
        import base64
        creds = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        req.add_header("Authorization", f"Basic {creds}")

    if headers:
        for k, v in headers.items():
            req.add_header(k, v)

    if data:
        if isinstance(data, str):
            req.data = data.encode("utf-8")
        else:
            req.data = json.dumps(data).encode("utf-8")

    try:
        resp = urllib.request.urlopen(req, context=ctx)
        body = resp.read().decode("utf-8")
        return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"error": body}


def create_indices(host, auth=None, api_key=None, recreate=False):
    """Create indices with mappings."""
    with open(MAPPINGS_FILE) as f:
        mappings = json.load(f)

    for index_name in INDICES:
        if index_name not in mappings:
            print(f"  WARNING: No mapping found for {index_name}, skipping creation")
            continue

        if recreate:
            print(f"  Deleting index: {index_name}...")
            make_request(f"{host}/{index_name}", method="DELETE", auth=auth, api_key=api_key)

        print(f"  Creating index: {index_name}...")
        status, resp = make_request(
            f"{host}/{index_name}",
            method="PUT",
            data=mappings[index_name],
            auth=auth,
            api_key=api_key
        )

        if status == 200:
            print(f"    Created successfully")
        elif status == 400 and "resource_already_exists_exception" in str(resp):
            print(f"    Already exists (use --recreate to replace)")
        else:
            print(f"    Response ({status}): {json.dumps(resp, indent=2)}")


def bulk_load(host, auth=None, api_key=None):
    """Bulk load NDJSON files into Elasticsearch."""
    for index_name in INDICES:
        filepath = DATA_DIR / f"{index_name}.ndjson"
        if not filepath.exists():
            print(f"  SKIP: {filepath} not found (run generate_mock_data.py first)")
            continue

        with open(filepath) as f:
            lines = f.readlines()

        total_docs = len(lines) // 2
        print(f"\n  Loading {index_name}: {total_docs} documents...")

        # Bulk API accepts chunks; send in batches of 1000 docs (2000 lines)
        batch_size = 2000  # lines, = 1000 docs
        errors = 0

        for i in range(0, len(lines), batch_size):
            batch = "".join(lines[i:i + batch_size])
            batch_num = (i // batch_size) + 1
            total_batches = (len(lines) + batch_size - 1) // batch_size

            status, resp = make_request(
                f"{host}/_bulk",
                method="POST",
                data=batch,
                headers={"Content-Type": "application/x-ndjson"},
                auth=auth,
                api_key=api_key
            )

            if status == 200:
                batch_errors = resp.get("errors", False)
                if batch_errors:
                    err_items = [item for item in resp.get("items", [])
                                 if "error" in item.get("index", {})]
                    errors += len(err_items)
                    if err_items:
                        print(f"    Batch {batch_num}/{total_batches}: {len(err_items)} errors")
                        print(f"      Sample: {json.dumps(err_items[0]['index']['error'], indent=2)}")
                else:
                    docs_in_batch = len(batch.strip().split("\n")) // 2
                    print(f"    Batch {batch_num}/{total_batches}: {docs_in_batch} docs indexed")
            else:
                print(f"    Batch {batch_num}/{total_batches}: HTTP {status}")
                print(f"      {json.dumps(resp, indent=2)[:500]}")
                errors += 1

        if errors == 0:
            print(f"  {index_name}: All {total_docs} documents indexed successfully")
        else:
            print(f"  {index_name}: {total_docs - errors}/{total_docs} indexed ({errors} errors)")


def verify(host, auth=None, api_key=None):
    """Quick count check on all indices."""
    print("\n  Index document counts:")
    for index_name in INDICES:
        status, resp = make_request(f"{host}/{index_name}/_count", auth=auth, api_key=api_key)
        if status == 200:
            print(f"    {index_name}: {resp.get('count', '?')} docs")
        else:
            print(f"    {index_name}: error ({status})")


def main():
    parser = argparse.ArgumentParser(description="Bulk load OJA mock data into Elasticsearch")
    parser.add_argument("--host", required=True, help="Elasticsearch URL (e.g., https://my-cluster.es.cloud.io:443)")
    parser.add_argument("--api-key", help="Elasticsearch API key")
    parser.add_argument("--user", help="Username (basic auth)")
    parser.add_argument("--password", help="Password (basic auth)")
    parser.add_argument("--recreate", action="store_true", help="Delete and recreate indices before loading")
    parser.add_argument("--skip-create", action="store_true", help="Skip index creation, just load data")
    parser.add_argument("--verify-only", action="store_true", help="Just check document counts")
    args = parser.parse_args()

    host = args.host.rstrip("/")
    auth = (args.user, args.password) if args.user and args.password else None
    api_key = args.api_key

    if not auth and not api_key:
        print("ERROR: Provide either --api-key or --user/--password")
        sys.exit(1)

    # Test connection
    print(f"Connecting to {host}...")
    status, resp = make_request(host, auth=auth, api_key=api_key)
    if status == 200:
        cluster = resp.get("cluster_name", "unknown")
        version = resp.get("version", {}).get("number", "unknown")
        print(f"  Connected: {cluster} (Elasticsearch {version})")
    else:
        print(f"  Connection failed ({status}): {resp}")
        sys.exit(1)

    if args.verify_only:
        verify(host, auth=auth, api_key=api_key)
        return

    if not args.skip_create:
        print("\nCreating indices...")
        create_indices(host, auth=auth, api_key=api_key, recreate=args.recreate)

    print("\nBulk loading data...")
    bulk_load(host, auth=auth, api_key=api_key)

    verify(host, auth=auth, api_key=api_key)
    print("\nDone!")


if __name__ == "__main__":
    main()
