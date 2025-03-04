import json
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler('app.log'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def process_feedback(feedback_file, output_file):
    try:
        with open(feedback_file, 'r') as f:
            feedback = [line.strip().split(' - ')[0] for line in f.readlines() if line.strip()]
        if not feedback:
            logger.info(f"No feedback in {feedback_file}—skipping update")
            return
        keywords = Counter(' '.join(feedback).split()).most_common(5)
        weights = {word: count / len(feedback) for word, count in keywords}
        with open(output_file, 'r') as f:
            data = json.load(f)
        # Determine key based on file content
        key = "responses" if "responses" in data else "messages"
        for item in data[key]:
            item["weight"] += sum(weights.get(word, 0) for word in item["text"].split()) * 0.1  # Incremental weight
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Updated weights in {output_file} with {len(feedback)} feedback entries")
    except FileNotFoundError:
        logger.error(f"{feedback_file} missing—no update")
    except json.JSONDecodeError:
        logger.error(f"{output_file} corrupted—check JSON format")
    except Exception as e:
        logger.error(f"Error processing {output_file}: {e}")

if __name__ == "__main__":
    process_feedback('feedback.txt', 'welcome_messages.json')
    process_feedback('chat_feedback.txt', 'chat_responses.json')