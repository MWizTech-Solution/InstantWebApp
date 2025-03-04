import json
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler('app.log'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def process_feedback(feedback_file, output_file):
    try:
        with open(feedback_file, 'r') as f:
            feedback = [line.strip().split(' - ')[0] for line in f.readlines()]
        keywords = Counter(' '.join(feedback).split()).most_common(5)
        weights = {word: count / len(feedback) for word, count in keywords}
        with open(output_file, 'r') as f:
            data = json.load(f)
        for msg in data["messages"]:
            msg["weight"] += sum(weights.get(word, 0) for word in msg["text"].split()) * 0.1  # Incremental weight
        with open(output_file, 'w') as f:
            json.dump(data, f)
        logger.info(f"Updated weights in {output_file} with {len(feedback)} entries")
    except FileNotFoundError:
        logger.error(f"{feedback_file} missing—no update")

if __name__ == "__main__":
    process_feedback('feedback.txt', 'welcome_messages.json')
    process_feedback('chat_feedback.txt', 'chat_responses.json')