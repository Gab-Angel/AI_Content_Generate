from langchain_core.prompts import PromptTemplate
from src.graph.states import ResearchResult, FinalReport
from langchain_groq import ChatGroq
#from langchain_openai import ChatOpenAI
from langchain_cerebras import ChatCerebras
from langchain_core.messages import SystemMessage, HumanMessage
from src.prompts.prompt_search import system_prompt_search, human_prompt_search
from src.prompts.prompt_writer import system_prompt_writer, human_prompt_writer
from dotenv import load_dotenv
import os

load_dotenv()


"""llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)"""

"""llm = ChatOpenAI(
    model='gpt-4.1-mini',
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)"""


llm = ChatCerebras(
    model="gpt-oss-120b",
    api_key=os.getenv('CEREBRAS_API_KEY'),
    temperature=0
    )

search_prompt = PromptTemplate.from_template(human_prompt_search)
writer_prompt = PromptTemplate.from_template(human_prompt_writer)

def search_agent(state, llm_model):
    print('🤖 SEARCH AGENT...')

    topic = state.topic 
    idea = state.idea
    messages = state.messages or []
    
    # Primeira execução - chama tools
    if not messages:
        prompt_search = search_prompt.format(topic=topic, idea=idea)
        
        messages = [
            SystemMessage(content=system_prompt_search),
            HumanMessage(content=prompt_search),
        ]
        
        response = llm_model.invoke(messages)
        return {"messages": [response]}
    
    # Segunda+ execução - estrutura resultado
    else:
        structured_llm = llm_model.with_structured_output(ResearchResult)
        
        instruction = HumanMessage(content="Estruture os resultados da pesquisa")
        response = structured_llm.invoke(messages + [instruction])
        
        return {"result_research": response}

def writer_agent(state, llm_model):
    print('🤖 WRITER AGENT...')

    type_post = state.type_post
    tone = state.tone
    qtd_slides = state.slides
    research = state.result_research
    

    prompt_writer = writer_prompt.format(
        type_post=type_post,
        tone = tone,
        slides = qtd_slides,
        research = research
    )

    messages = [
        SystemMessage(content=system_prompt_writer),
        HumanMessage(content=prompt_writer),
    ]

    structured_llm = llm_model.with_structured_output(FinalReport)

    response = structured_llm.invoke(messages)


    return {"final_report": response}
