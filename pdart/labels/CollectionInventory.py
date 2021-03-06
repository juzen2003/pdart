"""
Functionality to build a collection inventory using a SQLite database.
"""

from typing import List, cast

from pdart.db.BundleDB import BundleDB
from pdart.db.SqlAlchTables import (
    Collection,
    DocumentCollection,
    OtherCollection,
    switch_on_collection_subtype,
)


def get_collection_inventory_name(bundle_db: BundleDB, collection_lidvid: str) -> str:
    # We have to jump through some hoops to apply
    # switch_on_collection_type().
    def get_context_collection_inventory_name(collection: Collection) -> str:
        return "collection_context.csv"

    def get_document_collection_inventory_name(collection: Collection) -> str:
        return "collection.csv"

    def get_schema_collection_inventory_name(collection: Collection) -> str:
        return "collection_schema.csv"

    def get_other_collection_inventory_name(collection: Collection) -> str:
        prefix = cast(OtherCollection, collection).prefix
        return f"collection_{prefix}.csv"

    collection: Collection = bundle_db.get_collection(collection_lidvid)
    return switch_on_collection_subtype(
        collection,
        get_context_collection_inventory_name,
        get_document_collection_inventory_name,
        get_schema_collection_inventory_name,
        get_other_collection_inventory_name,
    )(collection)


def make_collection_inventory(bundle_db: BundleDB, collection_lidvid: str) -> bytes:
    """
    Create the inventory text for the collection having this LIDVID
    using the bundle database.
    """
    collection = bundle_db.get_collection(collection_lidvid)
    return switch_on_collection_subtype(
        collection,
        make_context_collection_inventory,
        make_other_collection_inventory,
        make_schema_collection_inventory,
        make_other_collection_inventory,
    )(bundle_db, collection_lidvid)


def make_context_collection_inventory(
    bundle_db: BundleDB, collection_lidvid: str
) -> bytes:
    """
    Create the inventory text for the collection having this LIDVID
    using the bundle database.
    """
    products = bundle_db.get_context_products()
    inventory_lines: List[str] = [f"S,{product.lidvid}\r\n" for product in products]
    res: str = "".join(inventory_lines)
    return res.encode()


def make_schema_collection_inventory(
    bundle_db: BundleDB, collection_lidvid: str
) -> bytes:
    """
    Create the inventory text for the collection having this LIDVID
    using the bundle database.
    """
    products = bundle_db.get_schema_products()
    inventory_lines: List[str] = [f"S,{product.lidvid}\r\n" for product in products]
    res: str = "".join(inventory_lines)
    return res.encode()


def make_other_collection_inventory(
    bundle_db: BundleDB, collection_lidvid: str
) -> bytes:
    """
    Create the inventory text for the collection having this LIDVID
    using the bundle database.
    """
    products = bundle_db.get_collection_products(collection_lidvid)
    inventory_lines: List[str] = [f"P,{product.lidvid}\r\n" for product in products]
    res: str = "".join(inventory_lines)
    return res.encode()
