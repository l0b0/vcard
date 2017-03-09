package name.engmark.vcard;

public class Vcard {
    private final String originalContent;

    public Vcard(String content) {
        originalContent = content;
    }

    public String originalContent() {
        return originalContent;
    }
}
