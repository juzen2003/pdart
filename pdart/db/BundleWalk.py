from typing import cast

from pdart.db.BundleDB import BundleDB
from pdart.db.SqlAlchTables import (
    BadFitsFile,
    BrowseFile,
    BrowseProduct,
    Bundle,
    Collection,
    ContextCollection,
    ContextProduct,
    DocumentCollection,
    DocumentFile,
    DocumentProduct,
    FitsFile,
    FitsProduct,
    SchemaCollection,
    SchemaProduct,
    OtherCollection,
    switch_on_collection_subtype,
)


class BundleWalk(object):
    """
    A walk of a bundle, given its BundleDB.

    The visit_xxx() methods will be called twice: once before
    (post=False) visiting its children, and once after (post=True)
    visiting its children.  Override them to have the walk do
    something.

    The __walk_xxx() methods encode the details of walking an object.
    The knowledge of what kind of children an object can have is
    encoded in these methods and only there.  If a new type of
    database object is added (for instance, we don't have SPICE
    products as I write this, but will in the future), we'll change
    the implementation of only these functions, and only in this
    class.  That is why they are named private, with double
    underscores: they should not be overridden in child classes.

    This class exists because it's error-prone to walk the tree by
    hand and to localize necessary changes in code.
    """

    def __init__(self, bundle_db: BundleDB) -> None:
        self.db = bundle_db

    def walk(self) -> None:
        bundle = self.db.get_bundle()
        self.__walk_bundle(bundle)

    ############################################################

    # The structure of a _walk_xxx() method is:
    #    pre-visit xxx
    #    visit xxx's children
    #    post-visit xxx

    def __walk_bundle(self, bundle: Bundle) -> None:
        bundle_lidvid = str(bundle.lidvid)
        self.visit_bundle(bundle, False)

        for collection in self.db.get_bundle_collections(bundle_lidvid):
            # We have to jump through some hoops to apply
            # switch_on_collection_type().

            def walk_context(coll: Collection) -> None:
                self.__walk_context_collection(cast(ContextCollection, coll))

            def walk_doc(coll: Collection) -> None:
                self.__walk_document_collection(cast(DocumentCollection, coll))

            def walk_sch(coll: Collection) -> None:
                self.__walk_schema_collection(cast(SchemaCollection, coll))

            def walk_other(coll: Collection) -> None:
                self.__walk_other_collection(cast(OtherCollection, coll))

            switch_on_collection_subtype(
                collection, walk_context, walk_doc, walk_sch, walk_other
            )(collection)

        self.visit_bundle(bundle, True)

    def __walk_context_collection(self, context_collection: ContextCollection) -> None:
        self.visit_context_collection(context_collection, False)

        collection_lidvid = str(context_collection.lidvid)
        for product in self.db.get_collection_products(collection_lidvid):
            self.__walk_context_product(cast(ContextProduct, product))

        self.visit_context_collection(context_collection, True)

    def __walk_document_collection(
        self, document_collection: DocumentCollection
    ) -> None:
        self.visit_document_collection(document_collection, False)

        collection_lidvid = str(document_collection.lidvid)
        for product in self.db.get_collection_products(collection_lidvid):
            self.__walk_document_product(cast(DocumentProduct, product))

        self.visit_document_collection(document_collection, True)

    def __walk_schema_collection(self, schema_collection: SchemaCollection) -> None:
        self.visit_schema_collection(schema_collection, False)

        collection_lidvid = str(schema_collection.lidvid)
        for product in self.db.get_collection_products(collection_lidvid):
            self.__walk_schema_product(cast(SchemaProduct, product))

        self.visit_schema_collection(schema_collection, True)

    def __walk_other_collection(self, other_collection: OtherCollection) -> None:
        self.visit_other_collection(other_collection, False)

        collection_lidvid = str(other_collection.lidvid)
        for product in self.db.get_collection_products(collection_lidvid):
            product_lidvid = str(product.lidvid)
            if self.db.browse_product_exists(product_lidvid):
                self.__walk_browse_product(cast(BrowseProduct, product))
            elif self.db.fits_product_exists(product_lidvid):
                self.__walk_fits_product(cast(FitsProduct, product))
            else:
                assert False, f"Missing product case: {product_lidvid}"

        self.visit_other_collection(other_collection, True)

    def __walk_browse_product(self, browse_product: BrowseProduct) -> None:
        self.visit_browse_product(browse_product, False)

        product_lidvid = str(browse_product.lidvid)
        browse_file = self.db.get_product_file(product_lidvid)
        self.visit_browse_file(cast(BrowseFile, browse_file))

        self.visit_browse_product(browse_product, True)

    def __walk_context_product(self, context_product: ContextProduct) -> None:
        self.visit_context_product(context_product, False)
        self.visit_context_product(context_product, True)

    def __walk_schema_product(self, schema_product: SchemaProduct) -> None:
        self.visit_schema_product(schema_product, False)
        self.visit_schema_product(schema_product, True)

    def __walk_document_product(self, document_product: DocumentProduct) -> None:
        self.visit_document_product(document_product, False)

        product_lidvid = str(document_product.lidvid)
        for document_file in self.db.get_product_files(product_lidvid):
            self.visit_document_file(cast(DocumentFile, document_file))

        self.visit_document_product(document_product, True)

    def __walk_fits_product(self, fits_product: FitsProduct) -> None:
        self.visit_fits_product(fits_product, False)

        product_lidvid = str(fits_product.lidvid)
        fits_file = self.db.get_product_file(product_lidvid)
        basename = str(fits_file.basename)
        if self.db.bad_fits_file_exists(basename, product_lidvid):
            self.visit_bad_fits_file(cast(BadFitsFile, fits_file))
        elif self.db.fits_file_exists(basename, product_lidvid):
            self.visit_fits_file(cast(FitsFile, fits_file))
        else:
            assert False, "Missing FITS product case: {basename} in {product_lidvid}u"

        self.visit_fits_product(fits_product, True)

    ############################################################

    def visit_bundle(self, bundle: Bundle, post: bool) -> None:
        pass

    ############################################################

    def visit_context_collection(
        self, context_collection: ContextCollection, post: bool
    ) -> None:
        pass

    def visit_document_collection(
        self, document_collection: DocumentCollection, post: bool
    ) -> None:
        pass

    def visit_schema_collection(
        self, schema_collection: SchemaCollection, post: bool
    ) -> None:
        pass

    def visit_other_collection(
        self, other_collection: OtherCollection, post: bool
    ) -> None:
        pass

    ############################################################

    def visit_browse_product(self, browse_product: BrowseProduct, post: bool) -> None:
        pass

    def visit_context_product(
        self, context_product: ContextProduct, post: bool
    ) -> None:
        pass

    def visit_document_product(
        self, document_product: DocumentProduct, post: bool
    ) -> None:
        pass

    def visit_schema_product(self, schema_product: SchemaProduct, post: bool) -> None:
        pass

    def visit_fits_product(self, fits_product: FitsProduct, post: bool) -> None:
        pass

    ############################################################

    def visit_browse_file(self, browse_file: BrowseFile) -> None:
        pass

    def visit_document_file(self, document_file: DocumentFile) -> None:
        pass

    def visit_fits_file(self, fits_file: FitsFile) -> None:
        pass

    def visit_bad_fits_file(self, bad_fits_file: BadFitsFile) -> None:
        pass
