import os.path
import sys
import traceback

import pyfits

import FileArchive
import FileArchives
import HstFilename

def validateArchive(arch):
    print 'Now validating the archive at %s' % arch.root
    proposalDict = {}
    fileCount = 0

    try:
        for (inst, prop, vis, f) in arch.walkFiles():
            filepath = os.path.join(arch.visitFilepath(inst, prop, vis), f)
            hfn = HstFilename.HstFilename(filepath)

            # Get the proposal from the file, using caching
            hstProposId = hfn.hstInternalProposalId();
            try:
                proposId = pyfits.getval(filepath, 'PROPOSID')
            except:
                proposId = 0;
            if proposId == 0:
                # TODO We do have a problem with wfpc2/hst_00000/visit_01/...
                # If I put -1 instead of 0 here, assertion fails.  What
                # does this mean?
                proposId = proposalDict.get(hstProposId, 0);
            else:
                proposalDict[hstProposId] = proposId;

            assert hfn.instrumentName() == inst
            assert hfn.visit() == vis
            assert proposId == prop, 'On %s: proposId %d != prop %d' % (filepath, proposId, prop)

            if True:
                fileCount = fileCount + 1
                if fileCount % 10000 == 0:
                    print ("Seen %dK files." % (fileCount / 1000))

        print "Archive tests okay (%d files)." % fileCount
    except:
        print "Archive test failed:"
        print(traceback.format_exc())
        sys.exit(1)

validateArchive(FileArchives.getAnyArchive())
