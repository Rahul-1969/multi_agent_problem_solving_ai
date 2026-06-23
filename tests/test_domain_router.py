import pytest
from router.domain_router import route_domain


class TestDomainRouter:
    """Comprehensive tests for the weighted domain router."""

    @pytest.mark.parametrize("query", [
        "Explain DBMS",
        "Explain Newton's Second Law",
        "What is Operating System",
        "Explain Data Structures",
        "Explain Data Structure",
        "What is DBMS",
        "What is OS",
        "Explain OSI Model",
        "Explain Multithreading",
    ])
    def test_reported_education_queries(self, query):
        """Original reported examples must route to education."""
        assert route_domain(query) == "education"

    @pytest.mark.parametrize("query", [
        # CS fundamentals
        "Explain binary search",
        "Explain bubble sort",
        "Explain pointers",
        "Explain arrays",
        "Explain variables",
        "Explain loops",
        "Explain data types",
        "Explain control structures",
        "Explain iteration",
        "Explain traversal",
        "Explain dynamic programming",
        "Explain hash table",
        "Explain runtime error",
        "Explain syntax error",
        "Explain sorting algorithm",
        "Explain searching algorithm",
        "Explain compiler",
        "Explain interpreter",
        "Explain recursion",
        "Explain object oriented programming",
        # Math
        "Explain algebra",
        "Explain geometry",
        "Explain trigonometry",
        "Explain statistics",
        "Explain probability",
        "Explain calculus",
        "Explain linear algebra",
        # Physics
        "Explain thermodynamics",
        "Explain electromagnetism",
        "Explain optics",
        "Explain kinematics",
        "Explain mechanics",
        "Explain newton",
        "Explain relativity",
        "Explain quantum physics",
        # Chemistry
        "Explain organic chemistry",
        "Explain inorganic chemistry",
        "Explain biochemistry",
        "Explain electrochemistry",
        "Explain elements",
        "Explain compounds",
        "Explain reactions",
        "Explain acids",
        # Biology
        "Explain photosynthesis",
        "Explain genetics",
        "Explain evolution",
        "Explain cell biology",
        "Explain ecosystems",
        "Explain mitosis",
        "Explain meiosis",
        "Explain chromosomes",
        "Explain enzymes",
        "Explain proteins",
        "Explain viruses",
        "Explain bacteria",
        "Explain fungi",
        # Advanced CS
        "Explain machine learning",
        "Explain deep learning",
        "Explain artificial intelligence",
        "Explain cloud computing",
        "Explain software engineering",
        "Explain computer networks",
        "Explain computer architecture",
        "Explain compiler design",
        "Explain theory of computation",
        "Explain blockchain",
        "Explain cyber security",
    ])
    def test_academic_concepts_routed_to_education(self, query):
        """Academic concepts across CS, math, science should route to education."""
        assert route_domain(query) == "education"

    @pytest.mark.parametrize("query", [
        "I have a fever",
        "What is diabetes",
        "Headache and nausea",
        "I feel sick",
        "My blood pressure is high",
        "What are symptoms of covid",
        "I have a virus infection",
        "Stomach pain and nausea",
        "What is depression",
        "What is anxiety",
        "Doctor appointment",
        "Hospital near me",
        "Chest pain",
        "Shortness of breath",
        "I am suffering from fatigue",
    ])
    def test_medical_queries_stay_medical(self, query):
        """Medical symptom and diagnosis queries must not leak to education."""
        assert route_domain(query) == "medical"

    @pytest.mark.parametrize("query", [
        "Write a Python program",
        "Implement binary search",
        "Debug my code",
        "Code for bubble sort",
        "Develop a rest api",
        "Build an app in django",
        "Sort a list in python",
        "How to debug runtime error",
        "React component example",
        "Flask vs django",
        "Build a web app",
        "Create a rest api",
        "Write a program to add two numbers",
        "Build an api",
        "Code for login page",
    ])
    def test_coding_queries_stay_coding(self, query):
        """Code-writing and implementation queries must route to coding."""
        assert route_domain(query) == "coding"

    @pytest.mark.parametrize("query", [
        "My rank is 10000",
        "College predictor",
        "eamcet rank 12345",
        "Seat allotment results",
        "Counselling date",
        "Admission process",
        "What is my cutoff",
        "JNTUH colleges",
    ])
    def test_college_queries_stay_college(self, query):
        """College and counselling queries must route to college."""
        assert route_domain(query) == "college"

    @pytest.mark.parametrize("query", [
        "Summarize this document",
        "What is in the pdf",
        "Extract text from my file",
        "Read the uploaded file",
        "From the pdf explain chapter 1",
        "My document has errors",
    ])
    def test_pdf_queries_stay_pdf(self, query):
        """PDF and document references must route to pdf."""
        assert route_domain(query) == "pdf"

    @pytest.mark.parametrize("query", [
        "What is the weather",
        "Tell me a joke",
        "Explain the solar system",
        "What is the capital of France",
        "How are you",
        "Good morning",
        "Tell me about yourself",
        "What is the capital of Japan",
        "Why is the sky blue",
        "Latest news today",
        "Who won the match",
    ])
    def test_general_queries_stay_general(self, query):
        """General knowledge and conversational queries must route to general."""
        assert route_domain(query) == "general"
