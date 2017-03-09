package name.engmark.vcard;

public class VcardParser {
    public Vcard parse(String content) {
        if (!content.startsWith("BEGIN:VCARD")) {
            return new Vcard(null, "Missing ‘BEGIN:VCARD’ line at line 1, character 1");
        }
        return null;
    }
}
