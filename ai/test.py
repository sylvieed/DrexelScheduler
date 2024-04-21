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
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

examples = [
    {"input": "How many professors are there?", 
     "query": "SELECT COUNT(*) FROM professors"},
    {
    "input": "How many courses have zero enrollments?", 
    "query": "SELECT COUNT(*) FROM courses WHERE enroll = '0'"
    },
    {
    "input": "What is the average rating for instructor John Doe?",
    "query": "SELECT avg_rating FROM instructors WHERE name = 'John Doe'"
    },
    {
    "input": "Which instructors have an average rating above 4.0?",
    "query": "SELECT name FROM instructors WHERE avg_rating > 4.0"
    },
    {
    "input": "How many courses are electives?",
    "query": "SELECT COUNT(*) FROM courses WHERE prereqs IS NULL"
    },
    {
    "input": "What is the most common start time for courses?",
    "query": "SELECT start_time, COUNT(*) AS frequency FROM courses GROUP BY start_time ORDER BY frequency DESC LIMIT 1"
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
    "input": "Who is the instructor with the highest average rating for each subject code?",
    "query": "SELECT c.subject_code, i.name, MAX(i.avg_rating) AS highest_rating FROM courses c JOIN course_instructor ci ON c.crn = ci.course_id JOIN instructors i ON ci.instructor_id = i.id GROUP BY c.subject_code"
    },

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

If the question does not seem related to the database, just return "I don't know" as the answer."""

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
    agent = create_sql_agent(
    llm=llm,
    db=db,
    prompt=full_prompt,
    verbose=False,
    agent_type="openai-tools",
    )

    print(agent.invoke({"input": "How many students are there?",
                        "top_k": 5,
                        "dialect": "SQLite",
                        "agent_scratchpad": []}))

    