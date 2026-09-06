"""Import every model module here so Base.metadata sees all tables —
Alembic's env.py and the test fixtures both rely on this side effect.
"""
from app.models.career_role import CareerRole, CareerRoleSkill, RoleSkillImportance  # noqa: F401
from app.models.certification import Certification  # noqa: F401
from app.models.experience import Experience, EmploymentType  # noqa: F401
from app.models.interview_question import InterviewQuestion, InterviewQuestionSkill, QuestionCategory, QuestionDifficulty  # noqa: F401
from app.models.job_posting import JobEmploymentType, JobPosting, JobPostingSkill  # noqa: F401
from app.models.learning_resource import LearningResource, LearningResourceSkill, ResourceType  # noqa: F401
from app.models.mock_interview import MockInterviewAnswer, MockInterviewSession, MockInterviewSessionQuestion, SessionStatus  # noqa: F401
from app.models.project import Project, ProjectSkill  # noqa: F401
from app.models.resume import Resume, ResumeStatus  # noqa: F401
from app.models.skill import Skill, SkillCategory  # noqa: F401
from app.models.student_profile import StudentProfile  # noqa: F401
from app.models.student_skill import ProficiencyLevel, SkillSource, StudentSkill  # noqa: F401
from app.models.user import User, UserRole  # noqa: F401
