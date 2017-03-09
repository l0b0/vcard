package name.engmark.vcard;

public class Vcard {
    private final String content;
    private final String error;

    public Vcard(String content, String error) {
        this.content = content;
        this.error = error;
    }

    public String getContent() {
        return content;
    }

    public String getError() {
        return error;
    }
}
