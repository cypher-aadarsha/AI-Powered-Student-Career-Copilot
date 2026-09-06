"""Seeds the interview question bank Phase 8's mock interviews draw from.
Behavioral/situational questions are general (no skill tags); technical
questions are tagged against the shared skill catalogue so a session
started against a career role can prefer role-relevant ones. Every
technical question carries a short `model_answer` used only by the
heuristic feedback provider (app/ai/interview_provider.py) for keyword
overlap — never shown to the student before they answer.

Idempotent: re-running skips any question whose text already exists.

Usage (from backend/, with DATABASE_URL pointed at the target database):
    python -m seed.interview_questions
"""
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.interview_question import InterviewQuestion, InterviewQuestionSkill, QuestionCategory, QuestionDifficulty
from app.models.skill import SkillCategory
from app.repositories.interview_question_repository import InterviewQuestionRepository
from app.repositories.skill_repository import SkillRepository

# (question_text, category, difficulty, model_answer, [(skill name, category), ...])
QUESTIONS = [
    (
        "Tell me about a time you faced a conflict within a team and how you resolved it.",
        QuestionCategory.behavioral,
        QuestionDifficulty.medium,
        None,
        [],
    ),
    (
        "Describe a situation where you had to learn a new technology quickly to complete a task.",
        QuestionCategory.behavioral,
        QuestionDifficulty.easy,
        None,
        [],
    ),
    (
        "Tell me about a challenging project and how you handled unexpected setbacks.",
        QuestionCategory.behavioral,
        QuestionDifficulty.medium,
        None,
        [],
    ),
    (
        "How do you prioritize tasks when you have multiple deadlines?",
        QuestionCategory.behavioral,
        QuestionDifficulty.easy,
        None,
        [],
    ),
    (
        "Describe a time you made a mistake — what happened and what did you learn?",
        QuestionCategory.behavioral,
        QuestionDifficulty.medium,
        None,
        [],
    ),
    (
        "Tell me about a time you received critical feedback. How did you respond?",
        QuestionCategory.behavioral,
        QuestionDifficulty.medium,
        None,
        [],
    ),
    (
        "Describe a time you had to explain a technical concept to a non-technical person.",
        QuestionCategory.behavioral,
        QuestionDifficulty.easy,
        None,
        [],
    ),
    (
        "How would you handle a disagreement with your manager about a technical decision?",
        QuestionCategory.situational,
        QuestionDifficulty.medium,
        None,
        [],
    ),
    (
        "What would you do if you discovered a critical bug right before a release deadline?",
        QuestionCategory.situational,
        QuestionDifficulty.hard,
        None,
        [],
    ),
    (
        "How would you approach joining a project with an unfamiliar, undocumented codebase?",
        QuestionCategory.situational,
        QuestionDifficulty.medium,
        None,
        [],
    ),
    (
        "What is the difference between a list and a tuple in Python?",
        QuestionCategory.technical,
        QuestionDifficulty.easy,
        "Lists are mutable and typically used for collections that change; tuples are immutable and "
        "often used for fixed collections or as dictionary keys. Tuples are generally slightly faster "
        "and use less memory.",
        [("Python", SkillCategory.programming_language)],
    ),
    (
        "Explain what a Python decorator is and give an example use case.",
        QuestionCategory.technical,
        QuestionDifficulty.medium,
        "A decorator is a function that wraps another function to extend its behavior without modifying "
        "its code, e.g. logging, timing, or access control, applied using the @decorator syntax.",
        [("Python", SkillCategory.programming_language)],
    ),
    (
        "What is the difference between INNER JOIN and LEFT JOIN?",
        QuestionCategory.technical,
        QuestionDifficulty.easy,
        "INNER JOIN returns only rows with matches in both tables; LEFT JOIN returns all rows from the "
        "left table and matched rows from the right, with NULLs where there is no match.",
        [("SQL", SkillCategory.technical)],
    ),
    (
        "How would you find and fix a slow SQL query?",
        QuestionCategory.technical,
        QuestionDifficulty.medium,
        "Use EXPLAIN to see the query plan, check for missing indexes on filtered or joined columns, "
        "avoid SELECT star, and reduce unnecessary joins or subqueries.",
        [("SQL", SkillCategory.technical)],
    ),
    (
        "Explain the difference between let, const, and var in JavaScript.",
        QuestionCategory.technical,
        QuestionDifficulty.easy,
        "var is function-scoped and hoisted; let and const are block-scoped. const prevents reassignment "
        "of the variable binding, though the referenced object can still be mutated.",
        [("JavaScript", SkillCategory.programming_language)],
    ),
    (
        "What is a closure in JavaScript?",
        QuestionCategory.technical,
        QuestionDifficulty.medium,
        "A closure is a function that retains access to variables from its enclosing scope even after "
        "that scope has finished executing, commonly used for data privacy and callbacks.",
        [("JavaScript", SkillCategory.programming_language)],
    ),
    (
        "What is the virtual DOM and why does React use it?",
        QuestionCategory.technical,
        QuestionDifficulty.medium,
        "The virtual DOM is an in-memory representation of the UI; React diffs it against the previous "
        "version to compute the minimal set of real DOM updates, improving performance.",
        [("React", SkillCategory.framework)],
    ),
    (
        "Explain the difference between state and props in React.",
        QuestionCategory.technical,
        QuestionDifficulty.easy,
        "Props are read-only data passed from a parent component; state is data managed within a "
        "component that can change over time and trigger re-renders.",
        [("React", SkillCategory.framework)],
    ),
    (
        "What is the difference between git merge and git rebase?",
        QuestionCategory.technical,
        QuestionDifficulty.medium,
        "Merge creates a new commit combining two histories, preserving branch history; rebase replays "
        "commits onto a new base, producing a linear history but rewriting commit hashes.",
        [("Git", SkillCategory.tool)],
    ),
    (
        "What is the difference between a Docker image and a container?",
        QuestionCategory.technical,
        QuestionDifficulty.easy,
        "An image is a read-only template with application code and dependencies; a container is a "
        "running instance of an image with its own writable layer.",
        [("Docker", SkillCategory.tool)],
    ),
    (
        "What are the main HTTP methods and when would you use each?",
        QuestionCategory.technical,
        QuestionDifficulty.easy,
        "GET retrieves data, POST creates a resource, PUT and PATCH update a resource, and DELETE "
        "removes it. Methods should generally be idempotent except POST.",
        [("REST APIs", SkillCategory.technical)],
    ),
    (
        "What is overfitting and how can you prevent it?",
        QuestionCategory.technical,
        QuestionDifficulty.medium,
        "Overfitting is when a model learns noise in the training data and performs poorly on unseen "
        "data; it can be reduced with more data, regularization, cross-validation, or simpler models.",
        [("Machine Learning", SkillCategory.technical)],
    ),
    (
        "How would you find which process is using a specific port on Linux?",
        QuestionCategory.technical,
        QuestionDifficulty.medium,
        "Use a command like lsof -i :PORT or ss -tulpn | grep PORT to identify the process bound to "
        "that port.",
        [("Linux", SkillCategory.technical)],
    ),
    (
        "What is SQL injection and how can it be prevented?",
        QuestionCategory.technical,
        QuestionDifficulty.medium,
        "SQL injection is when untrusted input is concatenated into a SQL query, letting an attacker "
        "alter its logic; prevent it with parameterized queries or prepared statements and input "
        "validation.",
        [("Security Fundamentals", SkillCategory.technical)],
    ),
    (
        "What is the difference between correlation and causation?",
        QuestionCategory.technical,
        QuestionDifficulty.easy,
        "Correlation means two variables move together; causation means one variable's change directly "
        "produces a change in the other. Correlation alone does not establish causation.",
        [("Statistics", SkillCategory.technical)],
    ),
]


def seed_interview_questions(db: Session) -> int:
    """Inserts every question in QUESTIONS that doesn't already exist (by
    text). Returns how many were created. Flushes but does not commit."""
    questions = InterviewQuestionRepository(db)
    skills = SkillRepository(db)
    existing_texts = {question.question_text for question in questions.list_all()}

    created = 0
    for question_text, category, difficulty, model_answer, skill_specs in QUESTIONS:
        if question_text in existing_texts:
            continue
        question = InterviewQuestion(
            question_text=question_text, category=category, difficulty=difficulty, model_answer=model_answer
        )
        db.add(question)
        db.flush()
        for name, skill_category in skill_specs:
            skill = skills.get_or_create(name=name, category=skill_category)
            db.add(InterviewQuestionSkill(interview_question_id=question.id, skill_id=skill.id))
        created += 1

    db.flush()
    return created


def run() -> None:
    db = SessionLocal()
    try:
        created = seed_interview_questions(db)
        db.commit()
        print(f"Seeded {created} new interview question(s); {len(QUESTIONS) - created} already existed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
