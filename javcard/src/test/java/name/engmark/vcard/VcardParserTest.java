package name.engmark.vcard;

import org.junit.Test;

public class VcardParserTest {
    @Test
    public void shouldSucceedWithMinimalInput() {
        VcardParser parser = new VcardParser();
        String content = "BEGIN:VCARD\r\nVERSION:3.0\r\nFN:\r\nN:;;;;\r\nEND:VCARD\r\n";

        parser.parse(content);
    }
}
