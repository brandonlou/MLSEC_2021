import argparse
import base64
import os


def get_html(payload):
    return """\
    <!DOCTYPE html>
    <html lang="en-us">
    <head>
        <meta charset="UTF-8">
        <title>Things to do in San Francisco</title>
    </head>
    <body>
        <object style="position:absolute; top:0; left:0; bottom:0; right:0; width:100%; height:100%; margin:0; padding:0;"></object>
    </body>
    <script>
        const encoded = "{payload}";
        const decoded = atob(encoded);
        const encoded_uri = "data:text/html;charset=utf-8," + encodeURIComponent(decoded)
        document.getElementsByTagName("object")[0].setAttribute("data", encoded_uri);
    </script>
    </html>
    """.format(payload=payload)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir')
    parser.add_argument('output_dir')

    args = parser.parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir

    for filename in os.listdir(input_dir):
        if filename[0] == '.': # Skip hidden files
            continue
        with open(f'{input_dir}/{filename}', 'rt') as in_file:
            html = in_file.read()
        encoded_bytes = base64.b64encode(html.encode('utf-8'))
        encoded_str = str(encoded_bytes, 'utf-8')
        output_html = get_html(encoded_str)
        with open(f'{output_dir}/{filename}', 'wt') as out_file:
            out_file.write(output_html)

    print('Done.')


if __name__ == '__main__':
    main()
