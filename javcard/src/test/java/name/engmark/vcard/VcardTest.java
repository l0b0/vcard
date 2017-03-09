package name.engmark.vcard;

import org.junit.Test;

import static org.hamcrest.core.Is.is;
import static org.hamcrest.core.IsEqual.equalTo;
import static org.junit.Assert.assertThat;

public class VcardTest {
    @Test
    public void shouldStoreOriginalContent() {
        Vcard vcard = new Vcard("BEGIN:VCARD\r\nVERSION:3.0\r\nFN:\r\nN:;;;;\r\nEND:VCARD\r\n");

        assertThat(vcard.originalContent(), is(equalTo(vcard.originalContent())));
    }
}
