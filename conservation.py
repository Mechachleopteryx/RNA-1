from .Rate4SiteRunner import Rate4Site
from Bio import AlignIO
import tempfile,os
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

def average(vlist,winlen):
    '''
    computes the average of each segmant in the length of winlen
    '''
    retlist=[]
    for i in range(len(vlist)-winlen+1):
        retlist.append(sum(vlist[i:i+winlen-1])/float(winlen))
    return retlist

def rate4site_cons(seqs,tree,onlytxid=None,winlen=13,rate4site='rate4site',emmacmd='emma'):
    '''
    Compute the conservation according to rate4site. The rates for each position
    for each sequence is returned. Gaps in the multiple alignment should
    be taken into consideration when mapping position to evolutionary rate.
    Assume that seqs is a dictionary with the txid as key and a sequence as
    value. tree is a file name containing the tree in newick format 
    '''
    #send the sequences to multiple alignment
    #write them down
    seqfile = tempfile.NamedTemporaryFile()
    for txid in seqs:
        seqfile.write('>'+txid+'\n')
        if isinstance(seqs[txid],Seq):
            seqfile.write(str(seqs[txid])+'\n')
        elif isinstance(seqs[txid],SeqRecord):
            seqfile.write(str(seqs[txid].seq)+'\n')
    seqfile.flush()
    #run emma
    alnfile = tempfile.NamedTemporaryFile()
    dndfile = tempfile.NamedTemporaryFile()
    os.system(emmacmd+' -sequence '+seqfile.name+' -outseq '+alnfile.name+
              ' -dendoutfile '+dndfile.name+' >& /dev/null')
    #call Rate4Site
    grate=Rate4Site(alnfile.name,tree)
    if onlytxid:
        rates=grate.runRate(refseq=onlytxid)
        return average(rates,winlen)
    else:
        urates={}
        for txid in seqs:
            rates=grate.runRate(refseq=txid)
            urates[txid]=average(rates,winlen)
        return urates

        