from dotenv import load_dotenv
from operator import itemgetter
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnablePassthrough
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings

load_dotenv()

db = SQLDatabase.from_uri("sqlite:///mydatabase.sqlite")
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

examples = [
    {"input": "How many professors are there?", 
     "query": "SELECT COUNT(*) FROM professors"},
    {
    "input": "How many courses have zero enrollments?", 
    "query": "SELECT COUNT(*) FROM courses WHERE enroll = '0'"
    },
    {
    "input": "What is the rating for professor John Doe?",
    "query": "SELECT avg_rating FROM instructors WHERE name LIKE '%John Doe%'"
    },
    {
    "input": "How many courses are electives?",
    "query": "SELECT COUNT(*) FROM courses WHERE prereqs IS NULL"
    },
    {
    "input": "How many courses does each instructor teach?",
    "query": "SELECT i.name, COUNT(ci.course_id) AS num_courses FROM instructors i JOIN course_instructor ci ON i.id = ci.instructor_id GROUP BY i.name"
    },
    {
    "input": "List all courses along with their instructor names, sorted by course title",
    "query": "SELECT c.course_title, i.name FROM courses c JOIN course_instructor ci ON c.crn = ci.course_id JOIN instructors i ON ci.instructor_id = i.id ORDER BY c.course_title"
    },
    {
    "input": "List all courses that are related to data analysis at night",
    "query": "SELECT course_title, description FROM courses WHERE description LIKE '%data analysis%'"
    },
    {
    "input": "Can you tell me some courses that are about machine learning and artificial intelligence?",
    "query": "SELECT crn, subject_code, course_number, course_title, description FROM courses WHERE description LIKE '%machine learning%' AND description LIKE '%artificial intelligence%'"
    },
    {
    "input": "I don't want to wake up early. Recommend some finance courses",
    "query": "SELECT crn, subject_code, course_number, course_title, start_time, description FROM courses WHERE subject_code = 'FIN' AND start_time >= '10:00'"
    },
    {
    "input": "Give me some high rated architecture professors and the courses they teach",
    "query": "SELECT i.name AS Professor_Name, i.avg_rating AS Rating, c.course_title AS Course FROM instructors i JOIN course_instructor ci ON i.id = ci.instructor_id JOIN courses c ON ci.course_id = c.crn WHERE i.avg_rating >= 4 AND c.subject_code = 'ARCH'"
    },
    {
    "input": "Give me electives that have less than 15 students in it",
    "query": "SELECT crn, subject_code, course_number, course_title, max_enroll FROM courses WHERE max_enroll <= 15 AND (prereqs IS NULL OR prereqs = '')"
    },
    {
    "input": "Find elective courses that have high ratings",
    "query": "SELECT c.crn, c.subject_code, c.course_number, c.course_title, i.avg_rating FROM courses c JOIN course_instructor ci ON c.crn = ci.course_id JOIN instructors i ON ci.instructor_id = i.id WHERE i.avg_rating >= 4 AND (c.prereqs IS NULL OR c.prereqs = '')"
    },
    {
    "input": "Find math courses available on Tuesday and Thursday between 2pm and 5pm",
    "query": "SELECT crn, subject_code, course_number, course_title, start_time, end_time, days FROM courses WHERE subject_code = 'MATH' AND days LIKE '%Tu%' AND days LIKE '%Th%' AND TIME(start_time) >= TIME('14:00') AND TIME(end_time) <= TIME('17:00')"
    },
    {
    "input": "Find me an online elective that is on Friday",
    "query": "SELECT crn, subject_code, course_number, course_title, days FROM courses WHERE instruction_method = 'Online-Asynchronous' AND days LIKE '%Friday%' AND (prereqs IS NULL OR prereqs = '')"
    },
    {
    "input": "give me electives that are related to cooking that have high ratings",
    "query": "SELECT c.crn, c.subject_code, c.course_number,c.course_title, i.avg_rating, FROM courses c JOIN course_instructor ci ON c.crn = ci.course_id JOIN instructors i ON ci.instructor_id = i.id WHERE c.description LIKE '%cooking%' AND (c.prereqs IS NULL OR c.prereqs = '') AND i.avg_rating >= 4"
    },
    {
    "input": "What class does Professor Mark teach?",
    "query": "SELECT c.crn, c.subject_code, c.course_title, i.name FROM courses c JOIN course_instructor ci ON c.crn = ci.course_id JOIN instructors i ON ci.instructor_id = i.id WHERE i.name LIKE '%Mark%'"
    }

]

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    OpenAIEmbeddings(),
    FAISS,
    k=5,
    input_keys=["input"],
)

system_prefix = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

If the question does not seem related to the database, just return "I don't know" as the answer.

While listing courses, ALWAYS include the course title, course number, and subject code in the format (subject_codecourse_number).

Here are some examples of user inputs and their corresponding SQL queries:"""

few_shot_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=PromptTemplate.from_template(
        "User input: {input}\nSQL query: {query}"
    ),
    input_variables=["input", "dialect", "top_k"],
    prefix=system_prefix,
    suffix="",
)

full_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate(prompt=few_shot_prompt),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)

answer = answer_prompt | llm | StrOutputParser()

if __name__ == "__main__":
    
    chain = create_sql_query_chain(llm, db)
    execute_query = QuerySQLDataBaseTool(db=db)
    write_query = create_sql_query_chain(llm, db)

    chain = (
    RunnablePassthrough.assign(query=write_query).assign(
        result=itemgetter("query") | execute_query
    )
    | answer
    )

    # user_input = str(input("Enter the question: "))
    # agent = create_sql_agent(
    # llm=llm,
    # db=db,
    # prompt=full_prompt,
    # verbose=False,
    # agent_type="openai-tools",
    # )

    # print(agent.invoke({"input": "Who teaches course CS 265",
    #                     "top_k": 5,
    #                     "dialect": "SQLite",
    #                     "agent_scratchpad": []}))

def ai_response(query):
    agent = create_sql_agent(
        llm=llm,
        db=db,
        prompt=full_prompt,
        verbose=False,
        agent_type="openai-tools",
    )

    response = agent.invoke({"input": query,
                                "top_k": 100,
                                "dialect": "SQLite",
                                "agent_scratchpad": []})
    return response
