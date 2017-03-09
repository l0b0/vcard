package name.engmark.vcard;

public class Vcard {
    private final String originalContent;
    private final String error;

    public Vcard(String content, String error) {
        originalContent = content;
        this.error = error;
    }

    public String originalContent() {
        return originalContent;
    }

    public String getError() {
        return error;
    }
}
