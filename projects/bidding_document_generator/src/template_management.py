from jinja2 import Template


def fill_template(template_path, data):
    with open(template_path, 'r') as f:
        template_str = f.read()
    template = Template(template_str)
    filled_template = template.render(data)
    return filled_template