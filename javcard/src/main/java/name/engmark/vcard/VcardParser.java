package name.engmark.vcard;

public class VcardParser {
    public Vcard parse(String content) {
        String error = null;
        if (!content.startsWith("BEGIN:VCARD")) {
            error = "Missing ‘BEGIN:VCARD’ line at line 1, character 1";
        }
        return new Vcard(content, error);
    }
}
