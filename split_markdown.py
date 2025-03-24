import os

def split_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    sections = content.split('\n## ')
    if sections[0].strip() == '':
        sections = sections[1:]

    if not os.path.exists('_openings'):
        os.makedirs('_openings')

    for section in sections:
        lines = section.split('\n')
        title = lines[0].strip()
        filename = f"_openings/{title.replace(' ', '-').lower()}.md"
        with open(filename, 'w', encoding='utf-8') as output_file:
            output_file.write('---\n')
            output_file.write(f'layout: post\n')
            output_file.write(f'title: "{title}"\n')
            output_file.write('---\n\n')
            output_file.write('## ' + '\n'.join(lines))

if __name__ == '__main__':
    split_markdown('all_in_one_auxiliary.md')