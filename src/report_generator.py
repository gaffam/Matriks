from jinja2 import Template


def generate_report(findings: dict) -> str:
    """Convert inspection findings into a formatted report string."""
    template = Template(
        """
        <h1>Ariza Raporu</h1>
        {% for key, value in findings.items() %}
        <p><strong>{{ key }}:</strong> {{ value }}</p>
        {% endfor %}
        """
    )
    return template.render(findings=findings)
