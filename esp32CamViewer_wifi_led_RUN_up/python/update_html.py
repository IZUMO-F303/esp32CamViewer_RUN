import gzip
import re

file_path = 'lib/Sketch_06.1_CameraWebServer/camera_index.h'

# Read the original content from the backup, as the current file is corrupted
with open('H:\document\PlatformIO\Projects\esp32CamViewer_wifi_led\.pio\libdeps\freenove_esp32_wrover\esp32-camera\camera_index.h', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(
    r"(const\s+uint8_t\s+(index_ov\w+_html_gz)\[\]\s+=\s+\{)(.*?)(\}\;)",
    re.DOTALL
)

new_file_content = content
matches = list(pattern.finditer(content))

for match in reversed(list(pattern.finditer(content))):
    array_name = match.group(2)
    hex_values_str = match.group(3)

    # Clean the hex string and convert to bytes
    hex_values = [s.strip() for s in hex_values_str.replace('\n', '').split(',') if s.strip()]
    byte_values = bytes([int(h, 16) for h in hex_values])

    # Decompress, modify, recompress
    html = gzip.decompress(byte_values).decode('utf-8')
    if 'id="led-switch"' not in html:
        replacement_html = """
<table class="info">
  <tbody>
    <tr><td class="section" colspan="2">LED</td></tr>
    <tr>
      <td>LED</td>
      <td>
        <input id="led-switch" type="checkbox" onchange="fetch('/control?var=led&val=' + (this.checked ? 1 : 0))">
      </td>
    </tr>
  </tbody>
</table>
</body>"""
        html = html.replace('</body>', replacement_html)

    gzipped_html = gzip.compress(html.encode('utf-8'))

    # Format back to C code
    new_len_define = f'#define {array_name}_len {len(gzipped_html)}'
    c_array_content = []
    for i in range(0, len(gzipped_html), 16):
        chunk = gzipped_html[i:i+16]
        c_array_content.append('  ' + ', '.join([f'0x{b:02X}' for b in chunk]))
    
    new_array_declaration = f"const uint8_t {array_name}[] = {{
' + ',\n'.join(c_array_content) + '\n}};"

    # Replace the old block with the new one
    original_block = match.group(0)
    new_block = f"{new_len_define}\n{new_array_declaration}"
    content = content.replace(original_block, new_block, 1)

with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print(f"File '{file_path}' updated successfully.")