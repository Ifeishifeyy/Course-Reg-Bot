import json
import random
import torch
import re
from model import NeuralNet
from datetime import datetime
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

with open('courses.json', 'r') as f:
    courses = json.load(f)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"

def get_response(msg, program, level):
    """ Returns course recommendations or general responses. """
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if any(word in msg.lower() for word in ["tell me ", "what is", "what","details about", "explain"]) and "about" in msg.lower():
        return get_course_details(msg, program, level)

    if any(word in msg.lower() for word in ["prerequisites for", "prerequisite for", "prerequisites of", "prerequisite of"]):
        return get_prerequisite(msg, program, level)

    if program and level:  # If message contains "elective" or is just a number (like "400")
            # Extract career choice from the message
            career_choice = extract_career_choice(msg)
            if career_choice:
                return recommend_electives(program, level, career_choice)
            else:
                return recommend_electives(program, level)

    if program and not level:
        return f"Got it! You are studying {program}. Now, please tell me your level (e.g., 100, 200, 300, 400)."

    if prob.item() > 0.5:
        if tag == "elective_recommendation":
            if program and level:
                return recommend_electives(program, level)
            else:
                return "Please specify your program and level to get course recommendations."
        elif tag == "prerequisite_query":
            return get_prerequisite(msg, program, level)
        elif tag == "course_details":
            return get_course_details(msg, program, level)
        else:
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    return random.choice(intent['responses'])
    
    return "I do not understand. Can you rephrase?"


def get_current_semester():
    month = datetime.now().month
    return "Alpha" if month <= 2 else "Omega"

def extract_course_code(msg):
    """ Extracts the course code from the message. """
    # Assuming course codes are in the format ABC123 (e.g., MAT223)
    match = re.search(r'[A-Za-z]{2,}\d{3}', msg)
    if match:
        return match.group(0).upper()  # Return the matched course code in uppercase
    return None

def recommend_electives(program, level,career_choice=None):
    semester = get_current_semester()

    if level == "100":
        return "No electives for 100 level students."
    
    if level == "300" and semester == "Omega":
        return "No electives for SIWES students."
    
    program = next((p for p in courses if p.lower() == program.lower()), program)
    if program in courses and level in courses[program].get("electives", {}):
        electives = courses[program]['electives'][level][semester]

        if career_choice:
            recommended_electives = []
        # Check each elective's career relevance
            for elective_code in electives:
                for course in courses[program]["courses"]:
                    if course["code"] == elective_code:
                        if any(career_choice.lower() == cr.lower() for cr in course.get("career_relevance", [])):
                            recommended_electives.append(f"{course['code']} - {course['title']}")

            if recommended_electives:
                return (
                    f"Based on your career choice ({career_choice}), here are the best electives for you:\n"
                    f"{'\n'.join(recommended_electives)}"
                )
            else:
                return f"No electives found that align with your career choice ({career_choice})."
        else:
            # Return all electives if no career choice is provided
            elective_list = "\n".join(electives)
            return (
                f"The electives available for {program} students in {semester} semester, {level} level are:\n"
                f"{elective_list}\n\n"
                "Do you have a specific career choice in mind? (e.g., Data Science, Software Engineering, etc.) "
             )
    return "No electives found for your selection."
        

def get_prerequisite(course_name, program, level):
    course_code = extract_course_code(course_name)
    if not course_code:
        return "Please provide a valid course code"
    for course in courses[program]["courses"]:
        if course["code"].upper() == course_code :
            if "prerequisites" in course:
                return f"Prerequisites for {course_code}: {', '.join(course['prerequisites'])}"
            return f"{course_code} has no prerequisites."
    return "Course not found."

def get_course_details(course_name, program, level):
    for course in courses[program]["courses"]:
        if course["code"].lower() in course_name.lower():
            return f"{course['code']} - {course['description']}"
    return "Course not found."

def extract_career_choice(msg):
    career_keywords = {
        "data scientist": ["data science", "data scientist", "data engineer"],
        "statistician": ["statistics", "statistician"],
        "AI engineer": ["artificial intelligence", "ai engineer", "ai specialist", "ai researcher","AI/ML engineer"],
        "machine learning engineer": ["ML engineer","machine learning engineer"],
        "data analyst": ["data analysis", "data analyst", "data analytics"],
        "software engineer": ["software engineering", "software engineer", "software developer"],
        "web developer": ["web development", "web developer", "frontend developer", "full-stack developer"],
        "mathematician": ["mathematician"],
        "Cryptographer": ["cryptographer", "cryptography"],
        "academic researcher": ["academic research", "research scientist", "researcher","lecturer"],
        "network engineer": ["networking", "network engineer", "network administrator", "network architect","network security engineer"],
        "engineer": ["engineering", "computer engineering", "embedded systems engineer","engineer"],
        "animator": ["animator","3D animator","2D animator","3D artist","2D artist","3D Generalist"],
        "project manager": ["project manager","project management", "project manager", "IT project manager"],
        "business analyst": ["business analysis","business analytics" ,"business analyst", "business intelligence analyst"],
        "operations research analyst": ["operations research", "operations research analyst"],
        "system administrator": ["system administration", "systems analyst", "system administrator"],
        "game developer": ["game development", "game developer","game programmer",],
        "bioinformatics specialist": ["bioinformatics", "computational biologist", "bioinformatics specialist"],
        "simulation engineer": ["simulation", "simulation engineer"],
        "cloud architect": ["cloud computing", "cloud architect", "distributed systems engineer"],
        "database administrator": ["database administration", "database administrator"],
        "cybersecurity specialist": ["cybersecurity", "cybersecurity specialist","cybersecurity expert","security specialist", "penetration tester","cybersecurity analyst"],
        "performance engineer": ["performance engineering", "performance engineer"],
        "quality control analyst": ["quality control", "quality control analyst","quality control engineer"],
        "hardware engineer": ["hardware engineering", "hardware engineer"],
        "it consultant": ["it consulting", "it consultant","IT Support Specialist"],
        "supply chain analyst": ["supply chain", "supply chain analyst"],
        "UI/UX designer": ["UI/UX designer", "UI designer", "UX designer"]
    }
    
    for career, variations in career_keywords.items():
        if any(variation in msg.lower() for variation in variations):
            return career
    return None

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break
        response = get_response(sentence)
        print(response)
