"""
Textile Design Corpus for Llama 3.2 Fine-Tuning
Creates training data for textile-specific AI assistant
"""
import json
from pathlib import Path

# Comprehensive textile design knowledge base
TEXTILE_CORPUS = [
    # Weave Structures
    {
        "instruction": "Explain Banarasi weave structure",
        "input": "What weave is best for Banarasi sarees?",
        "output": "Banarasi sarees traditionally use **Satin weave** (5-shaft or 8-shaft) for the base fabric. This creates a smooth, lustrous surface perfect for showcasing intricate Zari work. Key specifications:\n\n1. **Base Weave**: 5-shaft or 8-shaft Satin\n2. **Hooks**: 3000-3500 for traditional designs\n3. **Supplementary Weft**: Used for brocade patterns\n4. **Zari Thread**: Gold or silver metallic thread\n5. **Typical Motifs**: Peacock (mor), floral (phool), paisley (kalga)\n6. **Border Width**: 4-8 inches\n7. **Pallu Design**: Heavy with intricate patterns"
    },
    {
        "instruction": "Suggest weave for summer saree",
        "input": "Lightweight breathable saree for summer",
        "output": "For summer sarees, use **Plain weave** (also called Tabby weave):\n\n1. **Weave Type**: Plain weave (1/1 interlacement)\n2. **Hooks**: 1800-2200 (lower density for airiness)\n3. **Material**: Cotton or cotton-silk blend\n4. **Thread Count**: 60-80 EPI (ends per inch)\n5. **Colors**: Pastel shades (light blue, mint, peach)\n6. **Motifs**: Small, scattered florals\n7. **Border**: Minimal, 1-2 inches\n8. **Weight**: 300-400 grams total"
    },
    {
        "instruction": "Design peacock motif border",
        "input": "Create 6-inch border with peacock design",
        "output": "Peacock (Mor) border design specifications:\n\n**Dimensions**:\n- Border width: 6 inches\n- Motif height: 4-5 inches\n- Spacing: 2 inches between motifs\n\n**Weave Structure**:\n- Base: Satin weave\n- Motif: Supplementary weft technique\n- Hooks required: 3200-3500\n\n**Color Palette**:\n- Peacock body: Deep blue/green\n- Feathers: Gold Zari with green accents\n- Background: Maroon or deep red\n\n**Technical Details**:\n- Use 5-shaft satin for smooth base\n- Peacock feathers in fan arrangement\n- Add small floral fillers between motifs\n- Border edges with thin gold line (1-2 picks)"
    },
    {
        "instruction": "Calculate yarn consumption",
        "input": "How much yarn for 6-yard saree with 3000 hooks?",
        "output": "Yarn consumption calculation for 6-yard saree:\n\n**Given**:\n- Length: 6 yards = 5.5 meters\n- Width: 44 inches = 1.12 meters\n- Hooks: 3000\n\n**Warp Calculation**:\n- Warp threads = Hooks = 3000\n- Warp length = 5.5m + 0.5m (loom waste) = 6m\n- Warp yarn = 3000 × 6 = 18,000 meters\n\n**Weft Calculation**:\n- Picks per inch (PPI) = 80 (typical for medium density)\n- Total picks = 44 inches × 80 = 3,520\n- Weft per pick = 1.12m\n- Weft yarn = 3,520 × 1.12 = 3,942 meters\n\n**Total Yarn**: ~22,000 meters (18,000 warp + 4,000 weft)\n**Weight**: Approximately 800-900 grams for silk"
    },
    {
        "instruction": "Identify saree style from description",
        "input": "Heavy silk with temple border and checks",
        "output": "This describes a **Kanjivaram (Kanchipuram) saree**:\n\n**Characteristics**:\n1. **Origin**: Tamil Nadu, India\n2. **Weave**: Twill weave (3/1 or 2/2)\n3. **Signature**: Contrasting border and pallu\n4. **Temple Border**: Inspired by South Indian temple architecture\n5. **Body Pattern**: Checks (korvai technique)\n6. **Weight**: 600-800 grams (heavy silk)\n7. **Hooks**: 4000-4500 (very dense)\n\n**Recommended Specifications**:\n- Use 3/1 Twill for body\n- Temple motifs in Zari\n- Contrasting colors (e.g., red body with green border)\n- Thick border (6-8 inches)\n- Grand pallu with peacock or elephant motifs"
    },
    {
        "instruction": "Convert design to loom format",
        "input": "How to prepare design for Jacquard loom?",
        "output": "Design to Loom Conversion Process:\n\n**Step 1: Color Reduction**\n- Reduce design to 8 colors maximum\n- Use K-means clustering for optimal palette\n- Ensure high contrast between colors\n\n**Step 2: Quantization**\n- Convert to indexed color mode\n- Remove gradients (looms can't handle smooth transitions)\n- Sharpen edges for clarity\n\n**Step 3: Resolution**\n- Set resolution to match hook count\n- Width in pixels = Number of hooks\n- Height in pixels = Picks per inch × Length in inches\n\n**Step 4: Binary Conversion**\n- Create separate layer for each color\n- Convert each layer to binary (black/white)\n- Black = warp up, White = warp down\n\n**Step 5: Export**\n- Save as BMP (24-bit uncompressed)\n- File naming: design_color1.bmp, design_color2.bmp, etc.\n- Verify dimensions match loom specifications"
    },
    {
        "instruction": "Suggest colors for wedding saree",
        "input": "Color palette for bridal saree",
        "output": "Bridal Saree Color Palette Recommendations:\n\n**Traditional Choices**:\n1. **Primary**: Deep Red (Maroon/Crimson)\n   - Symbolizes prosperity and fertility\n   - Pantone: 19-1664 TCX (Chili Pepper)\n\n2. **Accent**: Gold Zari\n   - Metallic gold thread for motifs\n   - Adds luxury and richness\n\n3. **Border**: Bottle Green or Royal Blue\n   - Creates stunning contrast\n   - Pantone: 19-5420 TCX (Botanical Garden)\n\n**Modern Alternatives**:\n- Blush Pink with Rose Gold\n- Ivory with Copper accents\n- Teal with Silver Zari\n\n**Color Combination Rules**:\n- Use 60-30-10 rule (60% base, 30% border, 10% motifs)\n- Ensure high contrast for visibility\n- Test under different lighting (daylight, indoor)\n- Consider skin tone compatibility"
    },
    {
        "instruction": "Troubleshoot weaving defect",
        "input": "Design has broken threads in output",
        "output": "Broken Thread Defect Analysis:\n\n**Possible Causes**:\n1. **Tension Issues**\n   - Warp tension too high\n   - Uneven tension across width\n   - Solution: Adjust tension beam, check let-off mechanism\n\n2. **Thread Quality**\n   - Weak or old yarn\n   - Improper sizing\n   - Solution: Use fresh yarn, re-size warp\n\n3. **Design Complexity**\n   - Too many float threads\n   - Excessive warp lifting\n   - Solution: Simplify design, reduce float length to max 5 threads\n\n4. **Loom Settings**\n   - Shed opening too wide\n   - Harsh beating\n   - Solution: Reduce shed height, gentle beat-up\n\n**Prevention**:\n- Limit float length to 5 threads maximum\n- Use binding threads for long floats\n- Regular maintenance of loom\n- Quality check yarn before warping"
    },
    # Add 100+ more examples covering:
    # - Regional saree styles (Chanderi, Tussar, Pochampally, etc.)
    # - Motif designs (paisley, floral, geometric)
    # - Color theory for textiles
    # - Loom troubleshooting
    # - Cost estimation
    # - Quality control
]


def create_training_dataset(output_path: str = "textile_corpus.jsonl"):
    """
    Convert corpus to Llama 3.2 training format.

    Args:
        output_path: Path to save JSONL file
    """
    training_data = []

    for example in TEXTILE_CORPUS:
        # Llama 3.2 chat format
        conversation = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert textile designer and Jacquard loom specialist with deep knowledge of Indian saree design, weaving techniques, and manufacturing processes. You provide detailed, technical guidance on textile design, color theory, weave structures, and loom operations.<|eot_id|><|start_header_id|>user<|end_header_id|>

{example['instruction']}
{example['input']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{example['output']}<|eot_id|>"""

        training_data.append({"text": conversation})

    # Save as JSONL
    output_file = Path(output_path)
    with open(output_file, "w", encoding="utf-8") as f:
        for item in training_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"✅ Created {len(training_data)} training examples")
    print(f"📁 Saved to: {output_file.absolute()}")
    print(f"📊 Total size: {output_file.stat().st_size / 1024:.1f} KB")

    return str(output_file.absolute())


if __name__ == "__main__":
    corpus_path = create_training_dataset()
    print(f"\n🎯 Next step: Run fine-tuning with: python tools/finetune_llama.py")
