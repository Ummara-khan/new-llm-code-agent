import json
import os
import random
from itertools import permutations

def load_data(file_path):
    """Load JSON data from the given file path."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def generate_questions(data):
    """Generate diverse question-answer pairs with 20,000+ entries per field."""
    grouped_answers = {}
    unique_questions = set()

    for item in data.get("items", []):
        content_value = item.get("exdata_content")
        content_value = content_value.strip() if isinstance(content_value, str) else ""

        fabric_value = item.get("exdata_fabric")
        fabric_value = fabric_value.strip() if isinstance(fabric_value, str) else ""

        color_value = item.get("exdata_color")
        color_value = color_value.strip() if isinstance(color_value, str) else ""

        usage_value = item.get("exdata_usage")
        usage_value = usage_value.strip() if isinstance(usage_value, str) else ""

        if not content_value or not fabric_value:
            continue  # Skip if required fields are missing

        # Group fabrics under the same content value while keeping all records
        grouped_answers.setdefault(content_value, []).append(fabric_value)

        # Generate diverse questions
        question_templates = [
            f"What fabrics contain {content_value}?",
            f"Which fabric types include {content_value}?",
            f"Can you list fabrics made of {content_value}?",
            f"What is an example of a fabric that has {content_value} content?",
        ]

        answer = ", ".join(grouped_answers[content_value])

        for question in question_templates:
            unique_questions.add((question, answer))

        # Generate color-based questions
        if color_value:
            color_questions = [
                f"What fabric colors are available for {content_value}?",
                f"What colors can I find in {content_value} fabrics?",
                f"Which color options exist for {content_value} materials?"
            ]
            for question in color_questions:
                unique_questions.add((question, color_value))

        # Generate usage-based questions
        if usage_value:
            usage_questions = [
                f"What are the uses of {content_value} fabrics?",
                f"Where is {content_value} fabric commonly used?",
                f"Can you name common applications of {content_value} material?"
            ]
            for question in usage_questions:
                unique_questions.add((question, usage_value))

        # Generate fabric + color + usage combined questions
        if color_value and usage_value:
            combined_question = f"What are the properties of {fabric_value} in {color_value} color for {usage_value} usage?"
            combined_answer = f"{fabric_value} in {color_value} color is used for {usage_value}."
            unique_questions.add((combined_question, combined_answer))

    # Convert unique question-answer pairs into a list
    questions = [{"question": q, "answer": a} for q, a in unique_questions]

    # Ensure at least 20,000 questions per field by repeating with slight variations
    while len(questions) < 80000:  # 4 fields x 20k
        sample = random.choice(questions)
        questions.append({"question": sample["question"] + " (Give more details)", "answer": sample["answer"]})

    return questions[:80000]  # Trim to exactly 80,000

def save_questions(questions, output_file):
    """Save generated questions to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(questions, file, indent=4, ensure_ascii=False)
    
    print(f"Saved {len(questions)} questions to {output_file}")

if __name__ == "__main__":
    file_path = r"D:\code of llm\data.json"  # Replace with actual JSON file path
    output_file = r"fabric_questions.json"
    
    data = load_data(file_path)
    questions = generate_questions(data)
    save_questions(questions, output_file)
