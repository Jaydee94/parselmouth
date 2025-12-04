from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pathlib import Path

def create_pdf(filename, content):
    c = canvas.Canvas(str(filename), pagesize=letter)
    width, height = letter
    
    text_object = c.beginText(40, height - 40)
    text_object.setFont("Helvetica", 12)
    
    for line in content.split('\n'):
        text_object.textLine(line)
        
    c.drawText(text_object)
    c.save()
    print(f"Created {filename}")

def main():
    data_dir = Path("tests/data")
    data_dir.mkdir(parents=True, exist_ok=True)

    # invoice.pdf
    invoice_content = """
    INVOICE #1023
    Date: 2023-10-27
    
    Bill To:
    John Doe
    123 Maple Street
    Springfield, IL 62704
    
    Items:
    1. Widget A - $50.00
    2. Widget B - $25.00
    3. Service C - $100.00
    
    Total: $175.00
    
    Thank you for your business!
    """
    create_pdf(data_dir / "invoice.pdf", invoice_content)

    # meeting_notes.pdf
    notes_content = """
    Meeting Notes - Project Alpha
    Date: 2023-10-26
    Attendees: Alice, Bob, Charlie
    
    Agenda:
    1. Review Q3 performance.
    2. Discuss roadmap for Q4.
    3. Assign tasks for the new feature launch.
    
    Action Items:
    - Alice to finalize the design mockups by Friday.
    - Bob to set up the CI/CD pipeline.
    - Charlie to draft the user documentation.
    """
    create_pdf(data_dir / "meeting_notes.pdf", notes_content)

    # recipe.pdf
    recipe_content = """
    Grandma's Chocolate Chip Cookies
    
    Ingredients:
    - 2 1/4 cups all-purpose flour
    - 1 tsp baking soda
    - 1 tsp salt
    - 1 cup butter, softened
    - 3/4 cup sugar
    - 3/4 cup brown sugar
    - 1 tsp vanilla extract
    - 2 large eggs
    - 2 cups chocolate chips
    
    Instructions:
    1. Preheat oven to 375 F.
    2. Mix flour, baking soda, and salt.
    3. Beat butter, sugars, and vanilla. Add eggs.
    4. Stir in flour mixture and chocolate chips.
    5. Drop onto baking sheet.
    6. Bake for 9-11 minutes.
    """
    create_pdf(data_dir / "recipe.pdf", recipe_content)

if __name__ == "__main__":
    main()
