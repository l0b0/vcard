package name.engmark.vcard;

import org.junit.Test;

import java.util.Optional;

import static org.hamcrest.core.Is.is;
import static org.hamcrest.core.IsEqual.equalTo;
import static org.junit.Assert.assertThat;

public class VcardParserTest {
    @Test
    public void shouldSucceedWithMinimalInput() {
        VcardParser parser = new VcardParser();
        String content = "BEGIN:VCARD\r\nVERSION:3.0\r\nFN:\r\nN:;;;;\r\nEND:VCARD\r\n";

        Vcard vcard = parser.parse(content);
        assertThat(vcard.getError(), is(equalTo(Optional.empty())));
    }

    @Test
    public void shouldSaveOriginalContentToVcardOnSuccess() {
        VcardParser parser = new VcardParser();
        String content = "BEGIN:VCARD\r\nVERSION:3.0\r\nFN:\r\nN:;;;;\r\nEND:VCARD\r\n";

        Vcard vcard = parser.parse(content);

        assertThat(vcard.getContent(), is(equalTo(content)));
    }

    @Test
    public void shouldSaveOriginalContentToVcardOnFailure() {
        VcardParser parser = new VcardParser();
        String content = "invalid";

        Vcard vcard = parser.parse(content);

        assertThat(vcard.getContent(), is(equalTo(content)));
    }

    @Test
    public void shouldFailWithoutBeginProperty() {
        VcardParser parser = new VcardParser();
        String content = "VERSION:3.0\r\nFN:\r\nN:;;;;\r\nEND:VCARD\r\n";

        Vcard vcard = parser.parse(content);

        assertThat(vcard.getError(), is(equalTo(Optional.of("Missing ‘BEGIN:VCARD’ line at line 1, character 1"))));
    }
}
