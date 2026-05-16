from docling.document_converter import DocumentConverter
import os

def parse_local_pdf(pdf_path: str):
    """Parse any local PDF using Docling."""
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    return result.document.export_to_markdown()

def get_regulation_context(query: str, text: str):
    """Search parsed text for relevant regulation context."""
    lines = text.split('\n')
    relevant = []
    query_words = query.lower().split()
    
    for i, line in enumerate(lines):
        if any(word in line.lower() for word in query_words):
            start = max(0, i-2)
            end = min(len(lines), i+3)
            relevant.extend(lines[start:end])
            relevant.append("---")
    
    return '\n'.join(relevant[:50]) if relevant else "No relevant content found."

def create_sample_regulations():
    """Create a sample F1 regulations text file for demo purposes."""
    os.makedirs("data", exist_ok=True)
    sample = """
# F1 Sporting Regulations - Key Pit Stop Rules

## Article 23 - Pit Stops
23.1 During a race, a pit stop is defined as any time a car stops in the pit lane.
23.2 Each driver must use at least two different compounds during a dry race.
23.3 The pit lane speed limit is 80 km/h during the race.

## Article 24 - Tyre Compounds
24.1 Pirelli supplies three dry compounds per race weekend: SOFT, MEDIUM, HARD.
24.2 Each driver must use at least two different dry compounds during the race.
24.3 The nominated compounds are announced before each Grand Prix.

## Article 25 - Safety Car Periods
25.1 During a Safety Car period, pit stops are permitted.
25.2 Teams often use Safety Car periods to make pit stops without losing track position.
25.3 The pit lane remains open during Virtual Safety Car periods.

## Pit Stop Strategy Notes
- Undercut: pit earlier than competitors to gain track position via faster new tyres
- Overcut: stay out longer on older tyres while competitors pit, then pit later
- Tyre degradation affects optimal pit window timing
- Track position is crucial at circuits like Monaco where overtaking is difficult
"""
    with open("data/f1_regulations_summary.txt", 'w') as f:
        f.write(sample)
    return "data/f1_regulations_summary.txt"

def get_pit_rules_context():
    """Get pit stop rules as context for Granite."""
    txt_path = create_sample_regulations()
    with open(txt_path, 'r') as f:
        content = f.read()
    return content

if __name__ == "__main__":
    print("Testing regulations context...")
    context = get_pit_rules_context()
    print(context[:500])