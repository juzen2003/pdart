"""
**SCRIPT:** Build the database then build bundle, collection, and
product labels, and collection inventories.  This is a temporary
script under active development and so is underdocumented.
"""
from contextlib import closing
import os.path
import sqlite3

from pdart.exceptions.Combinators import *
from pdart.db.CreateDatabase import create_database
from pdart.pds4.Archives import *
from pdart.pds4labels.BundleLabel import *
from pdart.pds4labels.CollectionLabel import *
from pdart.pds4labels.ProductLabel import *

VERIFY = False
IN_MEMORY = False
CREATE_DB = True


def make_db_labels(conn):
    """
    Write labels for the whole archive in hierarchical order to
    increase cache hits for bundles and collections.  NOTE: This
    doesn't seem to run any faster, perhaps because of extra cost to
    having three open cursors.
    """
    with closing(conn.cursor()) as bundle_cursor:
        for (bundle,) in bundle_cursor.execute('SELECT bundle FROM bundles'):

            with closing(conn.cursor()) as collection_cursor:
                for (coll,) in collection_cursor.execute(
                  'SELECT collection FROM collections WHERE bundle=?',
                  (bundle,)):

                    with closing(conn.cursor()) as product_cursor:
                        for (prod,) in product_cursor.execute(
                          """SELECT product FROM products WHERE collection=?
                           EXCEPT SELECT product FROM bad_fits_files""",
                          (coll,)):

                            make_db_product_label(conn, prod, VERIFY)

                    make_db_collection_label_and_inventory(conn, coll, VERIFY)

            make_db_bundle_label(conn, bundle, VERIFY)


def make_db_bundle_labels(conn):
    with closing(conn.cursor()) as cursor:
        for (lid,) in cursor.execute('SELECT bundle FROM bundles'):
            make_db_bundle_label(conn, lid, VERIFY)


def make_db_collection_labels_and_inventories(conn):
    with closing(conn.cursor()) as cursor:
        for (lid,) in cursor.execute('SELECT collection FROM collections'):
            make_db_collection_label_and_inventory(conn, lid, VERIFY)


def make_db_product_labels(conn):
    with closing(conn.cursor()) as cursor:
        for (lid,) in cursor.execute(
            """SELECT product FROM products EXCEPT
               SELECT product FROM bad_fits_files"""):
            make_db_product_label(conn, lid, VERIFY)


def get_conn():
    if IN_MEMORY:
        return sqlite3.connect(':memory:')
    else:
        return sqlite3.connect(os.path.join(get_any_archive_dir(),
                                            'archive.spike.db'))


def dev():
    archive = get_any_archive()
    with closing(get_conn()) as conn:
        if CREATE_DB:
            create_database(conn, archive)
        # It seems to run about the same, building labels
        # hierarchically or by type.
        if True:
            make_db_labels(conn)
        else:
            make_db_product_labels(conn)
            make_db_collection_labels_and_inventories(conn)
            make_db_bundle_labels(conn)


if __name__ == '__main__':
    raise_verbosely(dev)
