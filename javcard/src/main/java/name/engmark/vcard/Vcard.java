package name.engmark.vcard;

import java.util.Optional;

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

    public Optional<String> getError() {
        return Optional.ofNullable(error);
    }
}
