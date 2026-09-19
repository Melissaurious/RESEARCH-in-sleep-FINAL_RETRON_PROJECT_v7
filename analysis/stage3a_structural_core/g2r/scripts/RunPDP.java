// g2r C3r driver (amendment 1). Thin wrapper around BioJava 7.1.4
// LocalProteinDomainParser.suggestDomains(Atom[]); no PDP constant is set here.
//
// Usage: RunPDP <out_dir> <chain.pdb> [...]
// Per input writes <out_dir>/<basename>.pdp.tsv, one row per representative atom (atom-array index order):
//   idx  model  chain  resnum  icode  resname  domain   (domain = 1..n; 0 = not in any returned domain)
// and prints one summary line per input: SUMMARY <file> <n_atoms> <n_domains> <status>.
// Preflight (F2): exactly one model, exactly one chain carrying representative atoms, unique residue keys.
// A violation writes no assignment and reports status PREFLIGHT_FAIL:<reason>.
import org.biojava.nbio.structure.*;
import org.biojava.nbio.structure.io.PDBFileReader;
import org.biojava.nbio.structure.domain.LocalProteinDomainParser;
import org.biojava.nbio.structure.domain.pdp.Domain;
import org.biojava.nbio.structure.domain.pdp.Segment;
import org.biojava.nbio.structure.chem.ChemCompGroupFactory;
import org.biojava.nbio.structure.chem.ReducedChemCompProvider;
import java.io.*;
import java.util.*;

public class RunPDP {
  public static void main(String[] args) {
    try { run(args); } catch (Throwable t) { System.out.println("FATAL " + t); t.printStackTrace(System.out); System.exit(2); }
  }

  static void run(String[] args) throws Exception {
    ChemCompGroupFactory.setChemCompProvider(new ReducedChemCompProvider());
    PDBFileReader r = new PDBFileReader();
    File outDir = new File(args[0]); outDir.mkdirs();
    for (int a = 1; a < args.length; a++) {
      String f = args[a];
      String base = new File(f).getName().replaceAll("\\.pdb$", "");
      Structure s = r.getStructure(f);
      Atom[] ca = StructureTools.getRepresentativeAtomArray(s);
      String fail = null;
      if (s.nrModels() != 1) fail = "models=" + s.nrModels();
      Set<String> chains = new TreeSet<>();
      Set<String> keys = new HashSet<>();
      for (Atom at : ca) {
        Group g = at.getGroup();
        chains.add(g.getChain().getName());
        ResidueNumber rn = g.getResidueNumber();
        if (!keys.add(rn.getSeqNum() + "|" + (rn.getInsCode() == null ? "" : rn.getInsCode())))
          fail = "duplicate_residue_key=" + rn;
      }
      if (fail == null && chains.size() != 1) fail = "chains=" + chains;
      if (fail == null && ca.length < 20) fail = "too_few_atoms=" + ca.length;  // disclosed driver guard
      if (fail != null) { System.out.println("SUMMARY\t" + f + "\t" + ca.length + "\tNA\tPREFLIGHT_FAIL:" + fail); continue; }

      List<Domain> doms = LocalProteinDomainParser.suggestDomains(ca);
      int[] lab = new int[ca.length];
      String status = "OK";
      int di = 0;
      for (Domain d : doms) {
        di++;
        for (Segment sg : d.getSegments()) {
          if (sg == null) continue;
          for (int i = sg.getFrom(); i <= sg.getTo(); i++) {
            if (i < 0 || i >= ca.length) { status = "SEGMENT_OUT_OF_RANGE"; continue; }
            if (lab[i] != 0 && lab[i] != di) status = "OVERLAPPING_DOMAINS";
            lab[i] = di;
          }
        }
      }
      try (PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, base + ".pdp.tsv")))) {
        w.println("idx\tmodel\tchain\tresnum\ticode\tresname\tdomain");
        for (int i = 0; i < ca.length; i++) {
          Group g = ca[i].getGroup();
          ResidueNumber rn = g.getResidueNumber();
          String ic = (rn.getInsCode() == null) ? "" : String.valueOf(rn.getInsCode());
          w.println(i + "\t1\t" + g.getChain().getName() + "\t" + rn.getSeqNum() + "\t" + ic + "\t"
                    + g.getPDBName() + "\t" + lab[i]);
        }
      }
      System.out.println("SUMMARY\t" + f + "\t" + ca.length + "\t" + doms.size() + "\t" + status);
    }
  }
}
