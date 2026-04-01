import json
import os
import sys
from typing import Dict, List, Tuple

DATA_FILE = "grades_data.json"

def load_data() -> Dict:
    """Load grades data from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"assignments": {}, "students": {}}

def save_data(data: Dict) -> None:
    """Save grades data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def weighted_average(scores: Dict[str, float], assignments: Dict[str, float]) -> float:
    """Calculate weighted average of scores."""
    if not assignments or sum(assignments.values()) == 0:
        return 0.0
    
    total_weight = 0.0
    weighted_sum = 0.0
    
    for aname, weight in assignments.items():
        if aname in scores and scores[aname] is not None:
            weighted_sum += scores[aname] * weight
            total_weight += weight
    
    if total_weight == 0:
        return 0.0
    
    return weighted_sum / total_weight

def letter_grade(average: float) -> str:
    """Convert numeric average to letter grade."""
    if average >= 90:
        return "A"
    elif average >= 80:
        return "B"
    elif average >= 70:
        return "C"
    elif average >= 60:
        return "D"
    else:
        return "F"

def add_student(data: Dict, name: str) -> None:
    """Add a new student."""
    if name in data["students"]:
        print(f"Student '{name}' already exists.")
        return
    data["students"][name] = {}
    save_data(data)
    print(f"Student '{name}' added successfully.")

def remove_student(data: Dict, name: str) -> None:
    """Remove a student."""
    if name not in data["students"]:
        print(f"Student '{name}' not found.")
        return
    del data["students"][name]
    save_data(data)
    print(f"Student '{name}' removed successfully.")

def add_assignment(data: Dict, name: str, weight: float) -> None:
    """Add a new assignment with weight."""
    if weight <= 0:
        print("Weight must be positive.")
        return
    if name in data["assignments"]:
        print(f"Assignment '{name}' already exists.")
        return
    data["assignments"][name] = weight
    save_data(data)
    print(f"Assignment '{name}' added with weight {weight}.")

def remove_assignment(data: Dict, name: str) -> None:
    """Remove an assignment."""
    if name not in data["assignments"]:
        print(f"Assignment '{name}' not found.")
        return
    del data["assignments"][name]
    for student in data["students"]:
        if name in data["students"][student]:
            del data["students"][student][name]
    save_data(data)
    print(f"Assignment '{name}' removed successfully.")

def set_score(data: Dict, student: str, assignment: str, score: float) -> None:
    """Set a student's score on an assignment."""
    if student not in data["students"]:
        print(f"Student '{student}' not found.")
        return
    if assignment not in data["assignments"]:
        print(f"Assignment '{assignment}' not found.")
        return
    if not (0 <= score <= 100):
        print("Score must be between 0 and 100.")
        return
    
    data["students"][student][assignment] = score
    save_data(data)
    print(f"Score set: {student} on {assignment} = {score}")

def view_student(data: Dict, name: str) -> None:
    """Display student's scores and average."""
    if name not in data["students"]:
        print(f"Student '{name}' not found.")
        return
    
    scores = data["students"][name]
    avg = weighted_average(scores, data["assignments"])
    grade = letter_grade(avg)
    
    print(f"\n--- {name} ---")
    for aname in data["assignments"]:
        score = scores.get(aname, "Missing")
        print(f"  {aname}: {score}")
    print(f"Weighted Average: {avg:.2f}")
    print(f"Letter Grade: {grade}\n")

def view_all(data: Dict) -> None:
    """Display all students with their averages."""
    if not data["students"]:
        print("No students in the system.")
        return
    
    print("\n--- All Students ---")
    for name in sorted(data["students"]):
        scores = data["students"][name]
        avg = weighted_average(scores, data["assignments"])
        grade = letter_grade(avg)
        print(f"{name}: {avg:.2f} ({grade})")
    print()

def export_report_card(data: Dict, student: str = None) -> None:
    """Export formatted report card(s) to text file(s)."""
    if student:
        if student not in data["students"]:
            print(f"Student '{student}' not found.")
            return
        students_to_export = {student: data["students"][student]}
    else:
        if not data["students"]:
            print("No students to export.")
            return
        students_to_export = data["students"]
    
    for name, scores in students_to_export.items():
        avg = weighted_average(scores, data["assignments"])
        grade = letter_grade(avg)
        
        filename = f"{name.replace(' ', '_')}_report.txt"
        with open(filename, "w") as f:
            f.write("=" * 50 + "\n")
            f.write(f"REPORT CARD: {name}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("ASSIGNMENT SCORES:\n")
            f.write("-" * 50 + "\n")
            for aname in sorted(data["assignments"]):
                score = scores.get(aname, "Missing")
                weight = data["assignments"][aname]
                f.write(f"{aname:<30} {str(score):<10} (weight: {weight})\n")
            
            f.write("\n" + "=" * 50 + "\n")
            f.write(f"WEIGHTED AVERAGE: {avg:.2f}\n")
            f.write(f"LETTER GRADE: {grade}\n")
            f.write("=" * 50 + "\n")
        
        print(f"Report card exported: {filename}")

def show_menu() -> None:
    """Display the CLI menu."""
    print("\n=== Grade Tracker ===")
    print("1. Add student")
    print("2. Remove student")
    print("3. Add assignment")
    print("4. Remove assignment")
    print("5. Set student score")
    print("6. View student")
    print("7. View all students")
    print("8. Export report card(s)")
    print("9. Exit")
    print("====================\n")

def main() -> None:
    """Main CLI loop."""
    data = load_data()
    
    while True:
        show_menu()
        try:
            choice = input("Enter choice (1-9): ").strip()
        except EOFError:
            print("\nExiting Grade Tracker.")
            break
        
        if choice == "1":
            name = input("Student name: ").strip()
            if name:
                add_student(data, name)
        
        elif choice == "2":
            name = input("Student name to remove: ").strip()
            if name:
                remove_student(data, name)
        
        elif choice == "3":
            name = input("Assignment name: ").strip()
            try:
                weight = float(input("Assignment weight: ").strip())
                if name:
                    add_assignment(data, name, weight)
            except ValueError:
                print("Weight must be a number.")
        
        elif choice == "4":
            name = input("Assignment name to remove: ").strip()
            if name:
                remove_assignment(data, name)
        
        elif choice == "5":
            student = input("Student name: ").strip()
            assignment = input("Assignment name: ").strip()
            try:
                score = float(input("Score (0-100): ").strip())
                if student and assignment:
                    set_score(data, student, assignment, score)
            except ValueError:
                print("Score must be a number.")
        
        elif choice == "6":
            name = input("Student name: ").strip()
            if name:
                view_student(data, name)
        
        elif choice == "7":
            view_all(data)
        
        elif choice == "8":
            export_all = input("Export all students? (y/n): ").strip().lower()
            if export_all == "y":
                export_report_card(data)
            else:
                student = input("Student name: ").strip()
                if student:
                    export_report_card(data, student)
        
        elif choice == "9":
            print("Exiting Grade Tracker.")
            break
        
        else:
            print("Invalid choice. Please enter 1-9.")

if __name__ == "__main__":
    main()