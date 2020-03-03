import os
import os.path
from pdart.documents.Downloads import download_product_documents

def download_docs(documents_dir, proposal_id):
    # type: (unicode, int) -> None
    assert not os.path.isdir(documents_dir)
    os.makedirs(documents_dir)
    download_product_documents(proposal_id, documents_dir)
    
    
