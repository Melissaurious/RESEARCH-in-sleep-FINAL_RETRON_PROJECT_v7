import org.biojava.nbio.structure.*;
import org.biojava.nbio.structure.io.PDBFileReader;
import org.biojava.nbio.structure.domain.LocalProteinDomainParser;
import org.biojava.nbio.structure.domain.pdp.Domain;
import org.biojava.nbio.structure.domain.pdp.Segment;
import java.util.List;
import org.biojava.nbio.structure.chem.ChemCompGroupFactory;
import org.biojava.nbio.structure.chem.ReducedChemCompProvider;
/** Thin driver: BioJava's own PDP on the CA atoms of every chain in each input PDB file.
 *  Output: file  n_ca  n_domains  domain_index  seg_from_resnum  seg_to_resnum  (one line per segment). */
public class RunPDP {
  public static void main(String[] args) {
    System.out.println("MAIN_REACHED"); System.out.flush();
    try { run(args); } catch (Throwable t) { System.out.println("FATAL "+t); t.printStackTrace(System.out); System.exit(2);} }
  static void run(String[] args) throws Exception {
    ChemCompGroupFactory.setChemCompProvider(new ReducedChemCompProvider());
    PDBFileReader r = new PDBFileReader();
    for (String f : args) {
      System.out.println("reading "+f); System.out.flush();
      Structure s = r.getStructure(f);
      System.out.println("read ok"); System.out.flush();
      Atom[] ca = StructureTools.getRepresentativeAtomArray(s);
      if (ca.length < 20) { System.out.println(f+"\t"+ca.length+"\t0\tNA\tNA\tNA"); continue; }
      List<Domain> doms = LocalProteinDomainParser.suggestDomains(ca);
      int di = 0;
      for (Domain d : doms) {
        di++;
        for (Segment sg : d.getSegments()) {
          String a = ca[sg.getFrom()].getGroup().getResidueNumber().toString();
          String b = ca[sg.getTo()].getGroup().getResidueNumber().toString();
          System.out.println(f+"\t"+ca.length+"\t"+doms.size()+"\t"+di+"\t"+a+"\t"+b);
        }
      }
    }
  }
}
