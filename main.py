import json
import os
import sys

DATA_FILE = "grades_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"assignments": {}, "students": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def weighted_average(scores, assignments):
    total_weight = 0.0
    weighted_sum = 0.0
    for aname, weight in assignments.items():
        if weight == 0:
            continue
        if aname in scores and scores[aname] is not None:
            weighted_sum += scores[aname] * weight
            total_weight += weight
    if total_weight == 0:
        return None
    return weighted_sum / total_weight

def letter_grade(avg):
    if avg is None:
        return "N/A"
    if avg >= 90:
        return "A"
    elif avg >= 80:
        return "B"
    elif avg >= 70:
        return "C"
    elif avg >= 60:
        return "D"
    else:
        return "F"

def add_student(data):
    name = input("Student name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    if name in data["students"]:
        print(f"Student '{name}' already exists.")
        return
    data["students"][name] = {}
    save_data(data)
    print(f"Student '{name}' added.")

def remove_student(data):
    name = input("Student name to remove: ").strip()
    if name not in data["students"]:
        print(f"Student '{name}' not found.")
        return
    del data["students"][name]
    save_data(data)
    print(f"Student '{name}' removed.")

def add_assignment(data):
    aname = input("Assignment name: ").strip()
    if not aname:
        print("Assignment name cannot be empty.")
        return
    if aname in data["assignments"]:
        print(f"Assignment '{aname}' already exists.")
        return
    try:
        weight = float(input("Weight (e.g. 0.25 for 25%, or any positive number for relative): ").strip())
    except ValueError:
        print("Invalid weight.")
        return
    if weight < 0:
        print("Weight cannot be negative.")
        return
    data["assignments"][aname] = weight
    save_data(data)
    print(f"Assignment '{aname}' with weight {weight} added.")

def remove_assignment(data):
    aname = input("Assignment name to remove: ").strip()
    if aname not in data["assignments"]:
        print(f"Assignment '{aname}' not found.")
        return
    del data["assignments"][aname]
    for sname in data["students"]:
        data["students"][sname].pop(aname, None)
    save_data(data)
    print(f"Assignment '{aname}' removed.")

def enter_scores(data):
    if not data["students"]:
        print("No students in the system.")
        return
    if not data["assignments"]:
        print("No assignments in the system.")
        return
    sname = input("Student name: ").strip()
    if sname not in data["students"]:
        print(f"Student '{sname}' not found.")
        return
    print(f"Enter scores for {sname} (press Enter to skip/leave missing):")
    for aname in data["assignments"]:
        current = data["students"][sname].get(aname)
        prompt = f"  {aname} (current: {current if current is not None else 'missing'}): "
        val = input(prompt).strip()
        if val == "":
            continue
        try:
            score = float(val)
            if score < 0 or score > 100:
                print("  Score must be 0-100, skipping.")
                continue
            data["students"][sname][aname] = score
        except ValueError:
            print("  Invalid value, skipping.")
    save_data(data)
    print("Scores saved.")

def list_students(data):
    if not data["students"]:
        print("No students in the system.")
        return
    if not data["assignments"]:
        print("No assignments defined yet.")
    print(f"\n{'Student':<20} {'Avg':>6} {'Grade':>5}")
    print("-" * 35)
    for sname, scores in data["students"].items():
        avg = weighted_average(scores, data["assignments"])
        grade = letter_grade(avg)
        avg_str = f"{avg:.2f}" if avg is not None else "N/A"
        print(f"{sname:<20} {avg_str:>6} {grade:>5}")
    print()

def list_assignments(data):
    if not data["assignments"]:
        print("No assignments in the system.")
        return
    print(f"\n{'Assignment':<25} {'Weight':>8}")
    print("-" * 35)
    total_w = sum(data["assignments"].values())
    for aname, weight in data["assignments"].items():
        print(f"{aname:<25} {weight:>8.4f}")
    print(f"{'Total weight:':<25} {total_w:>8.4f}\n")

def export_report(data):
    if not data["students"]:
        print("No students to export.")
        return
    choice = input("Export for (a)ll students or (s)ingle student? ").strip().lower()
    if choice == "s":
        sname = input("Student name: ").strip()
        if sname not in data["students"]:
            print(f"Student '{sname}' not found.")
            return
        students_to_export = {sname: data["students"][sname]}
    else:
        students_to_export = data["students"]

    for sname, scores in students_to_export.items():
        lines = []
        lines.append("=" * 45)
        lines.append("           STUDENT REPORT CARD")
        lines.append("=" * 45)
        lines.append(f"Student : {sname}")
        lines.append("-" * 45)
        if not data["assignments"]:
            lines.append("No assignments defined.")
        else:
            lines.append(f"{'Assignment':<22} {'Weight':>7} {'Score':>7}")
            lines.append("-" * 45)
            total_weight = 0.0
            for aname, weight in data["assignments"].items():
                score = scores.get(aname)
                score_str = f"{score:.2f}" if score is not None else "missing"
                lines.append(f"{aname:<22} {weight:>7.4f} {score_str:>7}")
                total_weight += weight
            lines.append("-" * 45)
            lines.append(f"{'Total Weight':<22} {total_weight:>7.4f}")
            lines.append("-" * 45)
        avg = weighted_average(scores, data["assignments"])
        grade = letter_grade(avg)
        avg_str = f"{avg:.2f}" if avg is not None else "N/A"
        lines.append(f"Weighted Average : {avg_str}")
        lines.append(f"Letter Grade     : {grade}")
        lines.append("=" * 45)
        lines.append("")

        safe_name = sname.replace(" ", "_").replace("/", "_")
        filename = f"report_{safe_name}.txt"
        with open(filename, "w") as f:
            f.write("\n".join(lines))
        print(f"Report saved: {filename}")

def print_menu():
    print("\n--- Grade Tracker ---")
    print("1. Add student")
    print("2. Remove student")
    print("3. Add assignment")
    print("4. Remove assignment")
    print("5. Enter/update scores")
    print("6. List students & grades")
    print("7. List assignments")
    print("8. Export report card(s)")
    print("9. Exit")

def main():
    data = load_data()
    while True:
        print_menu()
        choice = input("Choice: ").strip()
        if choice == "1":
            add_student(data)
        elif choice == "2":
            remove_student(data)
        elif choice == "3":
            add_assignment(data)
        elif choice == "4":
            remove_assignment(data)
        elif choice == "5":
            enter_scores(data)
        elif choice == "6":
            list_students(data)
        elif choice == "7":
            list_assignments(data)
        elif choice == "8":
            export_report(data)
        elif choice == "9":
            print("Goodbye.")
            sys.exit(0)
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()